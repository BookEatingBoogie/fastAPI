import json
import requests
from stablediffusion.comfyUI_servers import COMFYUI_SERVERS  # 세 개의 서버 URL 리스트
from stablediffusion.s3_uploader import download_image_from_s3

# comfyUI의 모든 서버에 이미지 업로드

def uploadImage_to_comfyUI(imgUrl):
    try:
        # 이미지 다운로드
        image_buffer, file_name = download_image_from_s3(imgUrl)
        image_buffer.seek(0)

        # 멀티파트 폼 데이터 구성
        files = {
            'image': (file_name, image_buffer, 'image/jpeg')
        }
        data = {
            'type': 'input',
            'overwrite': 'false'
        }

        uploaded_filename = None

        # 모든 서버에 동일한 이미지 업로드
        for server_url in COMFYUI_SERVERS:
            try:
                response = requests.post(f"{server_url}/upload/image", files=files, data=data)
                response.raise_for_status()
                print(f"[업로드 성공] {server_url}: {response.text}")
                meta = json.loads(response.text)
                uploaded_filename = meta.get("name")
            except Exception as e:
                print(f"[업로드 실패] {server_url}: {e}")

        return uploaded_filename  # 가장 마지막 성공한 파일명 반환

    except Exception as e:
        print(f"[ERROR] 이미지 업로드 실패: {e}")
        return None
