import json
import requests
from stablediffusion.character_success import COMFYUI_URL
from stablediffusion.s3_uploader import download_image_from_s3

# comfyUI에 이미지 업로드
def uploadImage_to_comfyUI(imgUrl):
    try:
        #업로드할 이미지와 서버 설정
        image_buffer, file_name = download_image_from_s3(imgUrl)

        image_buffer.seek(0)
        # 멀티파트 폼 데이터 구성

        # with open('./temp/test.png', 'rb') as f:
        #     file = f.read()

        files = {
        'image': (file_name, image_buffer, 'image/jpeg')
        }
        data = {
        'type': 'input', # 업로드할 폴더 종류: input/temp/output
        'overwrite': 'false' # 이미 존재하면 덮어쓸지 여부
        }
        # POST 요청으로 이미지 업로드
        response = requests.post(f"{COMFYUI_URL}/upload/image", files=files, data=data)
        print(response.text)

        meta = json.loads(response.text)
        filename = meta.get("name")

        return filename

    except Exception as e:
        print(f"[ERROR] 이미지 업로드 실패: {e}")
        return None
