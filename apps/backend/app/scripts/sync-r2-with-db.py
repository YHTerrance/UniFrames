import boto3
import sqlite3
import os

R2_ENDPOINT = "https://87a58f0eba6db52831d96aff269da7b7.r2.cloudflarestorage.com"
R2_ACCESS_KEY = "02d0f3922b424d5fa5e31ef8c6dd87ab"
R2_SECRET_KEY = "22258b06d205145f496c97e8fb43670e4ace14bfa4f3e2c437698bbec29a7111"
R2_BUCKET = "frame-images"
# os.environ["R2_PUBLIC_DOMAIN"] = "https://pub-ee8f31fc638a430ba19e1dc299a82447.r2.dev"

DB_PATH = "../univ.db"


# Connect R2
session = boto3.session.Session()
r2 = session.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
)

# Connect SQLite
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# frames table reproduce
cur.execute("DROP TABLE IF EXISTS frames")
cur.execute("""
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university TEXT NOT NULL,
    r2_url TEXT NOT NULL,
    filename TEXT NOT NULL
)
""")

# 
def list_folders():
    """버킷 최상위 prefix(=대학 이름) 폴더 목록 가져오기"""
    response = r2.list_objects_v2(Bucket=R2_BUCKET, Delimiter="/")
    prefixes = [p["Prefix"].rstrip("/") for p in response.get("CommonPrefixes", [])]
    return prefixes

def list_files(univ_name):
    """대학별 폴더 안에 있는 파일 리스트 가져오기"""
    response = r2.list_objects_v2(Bucket=R2_BUCKET, Prefix=f"{univ_name}/")
    files = []
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".png") or key.endswith(".jpg"):
            files.append(key)
    return files

# insert DB
folders = list_folders()
print("Found universities:", folders)

for univ in folders:
    files = list_files(univ)
    for f in files:
        file_url = f"https://{R2_BUCKET}.r2.dev/{f}"  # 퍼블릭 URL 규칙
        cur.execute("INSERT INTO frames (university, r2_url, filename) VALUES (?, ?, ?)",
                    (univ, file_url, os.path.basename(f)))

conn.commit()
conn.close()

