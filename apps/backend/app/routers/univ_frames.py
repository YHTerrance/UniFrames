# app/routers/univ_frames.py
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from app.services.univ_frames_service import (
    find_university_id_by_name,
    get_frames_for_university_id,
    on_demand_sync_by_folder,
    list_all_universities,
    list_universities_with_frames
)


router = APIRouter(prefix="/frames", tags=["frames"])

# @router.get("/universities", response_model=List[Dict[str, Any]])
# def list_universities():
#     return list_all_universities()

@router.get("/universities", response_model=List[Dict[str, Any]])
def list_universities():
    """프레임이 있는 대학 리스트만 반환"""
    return list_universities_with_frames()

@router.get("/by-name")
def frames_by_university_name(
    name: str = Query(..., description="예: 'Carnegie Mellon University'"),
    sync_if_empty: bool = Query(True, description="DB에 없으면 R2의 '<name>/'에서 즉시 동기화 시도"),
) -> Dict[str, Any]:
    print("DEBUG >>> API called with name:", name)
    uid = find_university_id_by_name(name)
    print("DEBUG >>> UID:", uid)
    if uid is None:
        raise HTTPException(status_code=404, detail=f"University not found for '{name}'")

    frames = get_frames_for_university_id(uid)
    print("DEBUG >>> Frames before sync:", frames)
    if not frames and sync_if_empty:
        on_demand_sync_by_folder(name, uid)
        frames = get_frames_for_university_id(uid)

    if not frames:
        return {
            "university_id": uid,
            "university_name": name,
            "has_frames": False,
            "frames": [],
            "message": f"No frames found for '{name}'.",
        }
    print("DEBUG >>> Frames after sync:", frames)
    return {
        "university_id": uid,
        "university_name": name,
        "has_frames": True,
        "count": len(frames),
        "frames": frames,
    }
    
@router.get("/by-id")
def frames_by_university_id(
    uid: int = Query(..., description="예: 'Carnegie Mellon University'")
) -> Dict[str, Any]:
    print("DEBUG >>> UID:", uid)

    frames = get_frames_for_university_id(uid)
    if not frames:
        return {
            "university_id": uid,
            "has_frames": False,
            "frames": [],
            "message": f"No frames found for '{uid}'.",
        }
    print("DEBUG >>> Frames after sync:", frames)
    return {
        "university_id": uid,
        "has_frames": True,
        "count": len(frames),
        "frames": frames,
    }