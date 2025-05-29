import io
import json
import requests
from stablediffusion.s3_uploader import download_image_from_s3
from stablediffusion.comfyUI_servers import COMFYUI_SERVERS
from stablediffusion.character_success import COMFYUI_URL  # 기본 서버

def uploadImage_to_comfyUI(imgUrl: str, all_servers: bool = False):
    """
    이미지를 ComfyUI에 업로드합니다.

    Parameters:
    - imgUrl: S3 등에서 다운로드할 이미지 URL
    - all_servers: True이면 COMFYUI_SERVERS 전체에 업로드, False이면 COMFYUI_URL 하나에만 업로드

    Returns:
    - 업로드된 파일 이름 (성공 시)
    - None (실패 시)
    """
    try:
        # 이미지 다운로드
        image_buffer, file_name = download_image_from_s3(imgUrl)
        image_bytes = image_buffer.getvalue()

        uploaded_filename = None

        # 여러 서버에 업로드할 경우
        if all_servers:
            for server_url in COMFYUI_SERVERS:
                try:
                    buffer_copy = io.BytesIO(image_bytes)
                    buffer_copy.seek(0)

                    files = {
                        'image': (file_name, buffer_copy, 'image/jpeg')
                    }
                    data = {
                        'type': 'input',
                        'overwrite': 'false'
                    }

                    response = requests.post(f"{server_url}/upload/image", files=files, data=data)
                    response.raise_for_status()
                    print(f"[업로드 성공] {server_url}: {response.text}")
                    meta = json.loads(response.text)
                    uploaded_filename = meta.get("name")

                except Exception as e:
                    print(f"[업로드 실패] {server_url}: {e}")

        else:
            # 단일 서버 업로드 (기본)
            image_buffer.seek(0)
            files = {
                'image': (file_name, image_buffer, 'image/jpeg')
            }
            data = {
                'type': 'input',
                'overwrite': 'false'
            }

            response = requests.post(f"{COMFYUI_URL}/upload/image", files=files, data=data)
            response.raise_for_status()
            print(f"[업로드 성공] {COMFYUI_URL}: {response.text}")
            meta = json.loads(response.text)
            uploaded_filename = meta.get("name")

        return uploaded_filename

    except Exception as e:
        print(f"[ERROR] 이미지 업로드 실패: {e}")
        return None
