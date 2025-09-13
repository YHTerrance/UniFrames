import os
from typing import List, Optional, Iterator
import boto3
from botocore.client import Config
from urllib.parse import quote

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN")

def _client():
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET, R2_PUBLIC_DOMAIN]):
        missing = [k for k in ["R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET","R2_PUBLIC_DOMAIN"]
                   if not os.getenv(k)]
        raise RuntimeError(f"Missing environment variables: {missing}")
    return boto3.client(
        "s3",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

def list_keys(prefix: str) -> List[str]:
    s3 = _client()
    keys, token = [], None
    while True:
        kw = {"Bucket": R2_BUCKET, "Prefix": prefix}
        if token: kw["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kw)
        for o in resp.get("Contents", []):
            k = o["Key"]
            if not k.endswith("/"):
                keys.append(k)
        if resp.get("IsTruncated"):
            token = resp.get("NextContinuationToken")
        else:
            break
    return keys

def public_url_for_key(key: str) -> str:
    from urllib.parse import quote
    return f"{R2_PUBLIC_DOMAIN}/{quote(key, safe='/@._-')}"


R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

s3 = boto3.client(
    "s3",
    region_name='auto',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

## add
def list_top_level_folders(bucket: Optional[str] = None) -> List[str]:
    bucket = bucket or R2_BUCKET
    paginator = s3.get_paginator("list_objects_v2")

    folders: List[str] = []
    for page in paginator.paginate(Bucket=bucket, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []):
            prefix = cp.get("Prefix", "")
            if prefix:
                folders.append(prefix.rstrip("/"))
    folders = sorted(set(folders), key=lambda x: x.lower())
    return folders


def list_keys(prefix: str, bucket: Optional[str] = None) -> Iterator[str]:
    bucket = bucket or R2_BUCKET
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []) or []:
            yield obj["Key"]

def key_exists(key: str, bucket: Optional[str] = None) -> bool:
    bucket = bucket or R2_BUCKET
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:
        return False

def public_url_for_key(key: str) -> str:
    base = R2_PUBLIC_DOMAIN.rstrip("/")
    k = quote(key.lstrip("/"))
    return f"{base}/{k}"