import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# 이미지 다운로드 함수
def download_image_from_url(image_url: str, save_path: str):
    try:
        res = requests.get(image_url)
        res.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(res.content)
        return save_path
    except Exception as e:
        print(f"[ERROR] 이미지 다운로드 실패: {e}")
        return None

# S3 업로드 함수
def upload_file_to_s3(file_path: str, bucket_name: str, s3_key: str, region="ap-northeast-2"):
    # AWS S3 클라이언트 생성
    s3 = boto3.client("s3", region_name=region) 
    try:
        # S3에 파일 업로드
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, bucket_name, s3_key)
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        return s3_url
    except NoCredentialsError:
        print("AWS 인증 정보가 없음")
    except Exception as e:
        print(f"[ERROR] S3 업로드 실패: {e}")
    return None

# 전체 흐름 함수 - 이미지 URL로부터 다운로드 받고, S3에 업로드까지 수행한 뒤 S3 URL 반환
def save_and_upload_image(image_url: str, local_filename: str, bucket_name: str, s3_key: str):
    os.makedirs("temp", exist_ok=True) # temp 디렉토리 생성
    save_path = os.path.join("temp", local_filename) # 로컬 저장 경로
    if download_image_from_url(image_url, save_path): # 이미지 다운로드 성공
        return upload_file_to_s3(save_path, bucket_name, s3_key) # S3 업로드 성공
    return None
