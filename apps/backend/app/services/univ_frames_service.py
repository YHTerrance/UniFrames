import os, re, sqlite3
from typing import List, Dict, Any, Optional, Set
from app.services.r2_client import list_keys, public_url_for_key, list_top_level_folders, s3, R2_BUCKET, key_exists


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



def list_universities_with_frames_from_r2(strict_check: bool = False) -> List[str]:

    folders = list_top_level_folders(R2_BUCKET)  # ['Carnegie Mellon University', ...]
    if not strict_check:
        return folders

    has_images: List[str] = []
    for name in folders:
        resp = s3.list_objects_v2(Bucket=R2_BUCKET, Prefix=f"{name}/", MaxKeys=50)
        contents = resp.get("Contents", []) or []
        found = False
        for obj in contents:
            key = obj.get("Key", "").lower()
            if key.endswith(IMG_EXTS):
                has_images.append(name)
                found = True
                break
    return has_images

IMG_TARGET = "1.png"

_norm_re = re.compile(r"[^a-z0-9]+")
def _norm(s: str) -> str:
    # 소문자 + 영숫자만 남김 (공백/하이픈/언더스코어/마침표 등 무시)
    return _norm_re.sub("", (s or "").lower())

def _resolve_folder_name(name: str) -> Optional[str]:
    """요청 name을 R2 최상위 폴더 중 하나로 정규화 매핑."""
    target = _norm(name)
    folders = list_top_level_folders(R2_BUCKET)  # ['Carnegie Mellon University', 'CMU', ...]
    # 1) 완전 동일
    for f in folders:
        if f == name:
            return f
    # 2) 정규화 비교(대소문자/공백/하이픈 등 무시)
    for f in folders:
        if _norm(f) == target:
            return f
    # 3) 부분 포함(정규화 기준) — 애매할 수 있어 마지막 fallback
    for f in folders:
        if target in _norm(f):
            return f
    return None

def get_public_frame_urls_for_university(name: str, recursive: bool = True) -> List[str]:
    """
    퍼블릭 루트를 사용해 '{resolved_name}/1.png' 또는 '{resolved_name}/**/1.png' 경로를 URL 리스트로 반환.
    공개 URL만 반환.
    """
    resolved = _resolve_folder_name(name)
    if not resolved:
        return []  # 폴더 자체를 못 찾음

    keys: Set[str] = set()
    prefix = f"{resolved}/"

    # 1) 최상위 바로 아래의 1.png
    direct = f"{resolved}/{IMG_TARGET}"
    if key_exists(direct, bucket=R2_BUCKET):
        keys.add(direct)

    # 2) 재귀적으로 */1.png 수집
    if recursive:
        for k in list_keys(prefix, bucket=R2_BUCKET):
            lk = k.lower()
            if lk.endswith(f"/{IMG_TARGET}") or (lk.endswith(IMG_TARGET) and k != direct):
                keys.add(k)

    return [public_url_for_key(k) for k in sorted(keys, key=lambda x: x.lower())]