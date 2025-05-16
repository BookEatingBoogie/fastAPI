import io
import json
import os
from fastapi import HTTPException
from typing_extensions import Buffer
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# 리전 설정
region_name = "ap-northeast-2"
# S3 클라이언트 생성
s3 = boto3.client("s3", region_name=region_name) 

# S3 이미지 업로드 함수
def upload_image_to_s3(image_url: str, bucket_name: str, s3_key: str):
    try:
        # 이미지 URL로부터 이미지 파일 다운로드
        resp = requests.get(image_url, stream=True)
        resp.raise_for_status()

        # 이미지 버퍼에 이미지 파일 임시 저장
        # buffer = io.BytesIO(resp.content)

        # 이미지 버퍼에 저장된 이미지 파일을 S3에 업로드
        s3.upload_fileobj(resp.raw, bucket_name, s3_key)

        # S3 URL 생성
        s3_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
        return s3_url
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS 인증 정보가 없음")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 업로드 실패: {e}")

# S3에서 이미지 객체 가져오기
def download_image_from_s3(s3_url: str):
    try:
        # S3 URL 파싱
        s3_parts = s3_url.split("/")
        bucket_name = "bookeating"
        s3_key = "/".join(s3_parts[3:])
        file_name = "/".join(s3_parts[4:])
        print(file_name)

        # 메모리 버퍼에 S3 객체 다운로드
        buffer = io.BytesIO()
        s3.download_fileobj(bucket_name, s3_key, buffer)
        buffer.seek(0)

        return buffer, file_name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 이미지 다운로드 실패: {e}")

# S3에 파일 업로드 함수 : 스토리마다 폴더 생성하여 업로드
def upload_file(file_content: str, bucket_name: str, s3_key: str):
    try:
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json.dumps(file_content, ensure_ascii=False))
        s3_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
        return s3_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 파일 업로드 실패: {e}")