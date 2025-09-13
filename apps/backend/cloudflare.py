# main.py
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sqlite3
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# --- 환경 변수 로드 (개발환경) ---
load_dotenv()

# --- FastAPI 앱 ---
app = FastAPI(title="University Logo API", version="1.0.0")

# --- 환경변수 설정 ---
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET", "frame-images")
SQLITE_PATH = os.getenv("SQLITE_PATH", "/home/young/Leeyujin/frame-gen/apps/backend/univ.db")

# 선택: 서버 기동 시 테이블 없는 경우 자동 생성할지 여부 (기본 True)
AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", "true").lower() in {"1", "true", "yes"}

# --- Cloudflare R2 (S3 호환) 클라이언트 ---
# R2는 region_name="auto", signature_version="s3v4" 권장
s3 = boto3.client(
    "s3",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    endpoint_url=R2_ENDPOINT,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

# --- DB 유틸 ---
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def run_migrations_if_needed() -> None:
    if not AUTO_MIGRATE:
        return
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS Universities (
                name TEXT PRIMARY KEY,
                website_url TEXT,
                r2_logo_key TEXT,   -- Cloudflare R2 object key (ex: logos/harvard.png)
                r2_logo_url TEXT    -- 선택: 절대 URL 직접 저장 시
            );
            """
        )
        # 빠른 조회를 위한 인덱스(부분검색 대비)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_universities_name ON Universities(name);"
        )
        conn.commit()

def normalize_name(s: str) -> str:
    # 양 끝 공백 제거 + 내부 연속 공백 1칸으로, 대소문자 무시 검색에 사용
    return " ".join(s.strip().split())

# --- 모델 ---
class UniversityLogoResponse(BaseModel):
    name: str
    website_url: str | None = None
    logo_url: str

class ErrorResponse(BaseModel):
    detail: str

# --- 앱 라이프사이클 ---
@app.on_event("startup")
def on_startup():
    # 필수 환경 변수 점검
    missing = []
    if not SQLITE_PATH:
        missing.append("SQLITE_PATH")
    if not R2_ENDPOINT:
        missing.append("R2_ENDPOINT")
    if not R2_ACCESS_KEY_ID:
        missing.append("R2_ACCESS_KEY_ID")
    if not R2_SECRET_ACCESS_KEY:
        missing.append("R2_SECRET_ACCESS_KEY")
    if not R2_BUCKET:
        missing.append("R2_BUCKET")
    if missing:
        # 개발 편의를 위해 로그만 남기고 계속할 수도 있지만, 여기선 명확히 에러를 띄우도록 함
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # DB 파일 폴더가 없다면 생성
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

    # 옵션: 테이블 자동 생성
    run_migrations_if_needed()


]
@app.get(
    "/university/logo",
    response_model=UniversityLogoResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_university_logo(
    university_name: str = Query(..., description="University name (exact or near-exact)")
):
    """
    이름으로 Universities에서 조회.
    - r2_logo_key가 있으면 R2 presigned URL 생성
    - 없고 r2_logo_url이 있으면 그대로 사용
    """
    search_name = normalize_name(university_name)

    # 1) 먼저 대소문자 무시 정확 일치 시도
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT name, website_url, r2_logo_key, r2_logo_url
            FROM Universities
            WHERE lower(name) = lower(?)
            """,
            (search_name,),
        ).fetchone()

        # 2) 정확 일치가 없다면 "부분일치"도 시도 (예: 'Harvard'로 'Harvard University' 찾기)
        if not row:
            like_term = f"%{search_name}%"
            row = conn.execute(
                """
                SELECT name, website_url, r2_logo_key, r2_logo_url
                FROM Universities
                WHERE lower(name) LIKE lower(?)
                ORDER BY length(name) ASC
                LIMIT 1
                """,
                (like_term,),
            ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"University not found: {university_name}")

    name = row["name"]
    website_url = row["website_url"]
    r2_logo_key = row["r2_logo_key"]
    r2_logo_url = row["r2_logo_url"]

    # 3) 로고 URL 결정
    logo_url = None
    if r2_logo_key:
        try:
            logo_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": R2_BUCKET, "Key": r2_logo_key},
                ExpiresIn=60,  # 필요시 300 등으로 늘려도 됨
            )
        except Exception as e:
            # presign 실패 시, r2_logo_url이 있으면 폴백
            if r2_logo_url:
                logo_url = r2_logo_url
            else:
                raise HTTPException(status_code=500, detail=f"Failed to presign URL: {str(e)}")
    elif r2_logo_url:
        logo_url = r2_logo_url
    else:
        raise HTTPException(status_code=500, detail="No logo key/url stored for this university")

    return UniversityLogoResponse(name=name, website_url=website_url, logo_url=logo_url)