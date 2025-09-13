import os, re, sqlite3
from typing import List, Dict, Any, Optional
from app.services.r2_client import list_keys, public_url_for_key

DEFAULT_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../yujin/univ.db"))
UNIV_DB_PATH = os.getenv("UNIV_DB_PATH", DEFAULT_DB)
print(UNIV_DB_PATH)
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")

_norm_keep = re.compile(r"[a-z0-9\s-]", re.IGNORECASE)
def normalize_name(s: str) -> str:
    s = (s or "").strip().lower()
    s = "".join(ch for ch in s if _norm_keep.match(ch) is not None)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def db():
    con = sqlite3.connect(UNIV_DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON;")
    return con

def list_all_universities():
    conn = sqlite3.connect(UNIV_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT university_id, name FROM Universities ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def list_universities_with_frames():
    with db() as con:  # 이미 row_factory=sqlite3.Row 로 세팅됨
        rows = con.execute("""
            SELECT DISTINCT u.university_id, u.name
            FROM Universities u
            JOIN frames f ON u.university_id = f.university_id
            ORDER BY u.name
        """).fetchall()
        return [{"id": r["university_id"], "name": r["name"]} for r in rows]


def find_university_id_by_name(query: str) -> Optional[int]:
    with db() as con:
        cur = con.cursor()
        row = cur.execute("SELECT university_id FROM Universities WHERE name = ? COLLATE NOCASE", (query,)).fetchone()
        if row: return row["university_id"]
        key = normalize_name(query)
        rows = cur.execute("SELECT university_id, name FROM Universities").fetchall()
        candidates = [r["university_id"] for r in rows if normalize_name(r["name"]) == key]
        if len(candidates) >= 1: return candidates[0]
        row = cur.execute("""
            SELECT university_id FROM Universities
            WHERE name LIKE ? COLLATE NOCASE
            ORDER BY LENGTH(name) ASC LIMIT 1
        """, (f"%{query}%",)).fetchone()
        return row["university_id"] if row else None

def get_frames_for_university_id(university_id: int) -> List[Dict[str, Any]]:
    with db() as con:
        rows = con.execute("""
            SELECT id, filename, r2_url, sort_order
            FROM frames
            WHERE university_id = ?
            ORDER BY sort_order, filename
        """, (university_id,)).fetchall()
        return [dict(r) for r in rows]

def upsert_frame(university_id: int, filename: str, url: str, sort_order: int) -> None:
    with db() as con:
        con.execute("""
            INSERT INTO frames (university_id, r2_url, filename, sort_order)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(university_id, filename)
            DO UPDATE SET r2_url=excluded.r2_url, sort_order=excluded.sort_order
        """, (university_id, url, filename, sort_order))
        con.commit()

def parse_sort(filename: str) -> int:
    stem = filename.rsplit(".", 1)[0]
    if stem.isdigit(): return int(stem)
    m = re.match(r"^(\d{1,3})[-_ ]", filename)
    return int(m.group(1)) if m else 999

def on_demand_sync_by_folder(university_name: str, university_id: int) -> int:
    with db() as con:
        row = con.execute("SELECT name FROM Universities WHERE university_id=?", (university_id,)).fetchone()
        canonical = row["name"] if row else university_name

    candidates = []
    for c in [university_name, canonical]:
        if c and c not in candidates:
            candidates.append(c)

    inserted = 0
    for folder in candidates:
        keys = list_keys(f"{folder}/")
        pairs = []
        for k in keys:
            parts = k.split("/")
            if len(parts) != 2:
                continue
            fname = parts[1]
            if not fname.lower().endswith(IMG_EXTS):
                continue
            pairs.append((k, fname))

        pairs.sort(key=lambda x: (parse_sort(x[1]), x[1].lower()))
        for key, fname in pairs:
            url = public_url_for_key(key)
            order = parse_sort(fname)
            upsert_frame(university_id, fname, url, order)
            inserted += 1
        if pairs:
            break
    return inserted
