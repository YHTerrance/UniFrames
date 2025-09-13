import os
import sqlite3
from typing import List
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

# 라우터 정의
router = APIRouter(prefix="/frames", tags=["frames"])

# DB 경로 로드
load_dotenv()
DB_PATH = os.getenv("UNIV_DB_PATH")

def get_conn():
    return sqlite3.connect(DB_PATH)

# -------------------------------
# Pydantic 모델
# -------------------------------
class FrameBase(BaseModel):
    university_id: int
    r2_url: str
    filename: str
    sort_order: Optional[int] = 0

class FrameCreate(FrameBase):
    pass

class Frame(FrameBase):
    id: int
    class Config:
        from_attributes = True  # Pydantic v2 방식


# -------------------------------
# CRUD 엔드포인트
# -------------------------------
@router.get("/", response_model=List[Frame])
def get_frames():
    """모든 frame 불러오기"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, university_id, r2_url, filename, sort_order FROM frames")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "university_id": r[1], "r2_url": r[2], "filename": r[3], "sort_order": r[4]}
        for r in rows
    ]


@router.get("/{frame_id:int}", response_model=Frame)
def get_frame(frame_id: int):
    """특정 frame 불러오기 (id 기준)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, university_id, r2_url, filename, sort_order FROM frames WHERE id=?", (frame_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Frame not found")
    return {"id": row[0], "university_id": row[1], "r2_url": row[2], "filename": row[3], "sort_order": row[4]}


@router.post("/", response_model=Frame, status_code=status.HTTP_201_CREATED)
def create_frame(frame: FrameCreate):
    """새 frame 추가"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO frames (university_id, r2_url, filename, sort_order) VALUES (?, ?, ?, ?)",
        (frame.university_id, frame.r2_url, frame.filename, frame.sort_order),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, **frame.dict()}


@router.put("/{frame_id:int}", response_model=Frame)
def update_frame(frame_id: int, frame: FrameBase):
    """frame 업데이트"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE frames SET university_id=?, r2_url=?, filename=?, sort_order=? WHERE id=?",
        (frame.university_id, frame.r2_url, frame.filename, frame.sort_order, frame_id),
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Frame not found")
    conn.commit()
    conn.close()
    return {"id": frame_id, **frame.dict()}


@router.delete("/{frame_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def delete_frame(frame_id: int):
    """frame 삭제"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM frames WHERE id=?", (frame_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Frame not found")
    conn.commit()
    conn.close()