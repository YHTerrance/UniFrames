import os
from typing import List
import boto3
from botocore.client import Config

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
