import os
import json
import time
import requests
from fastapi import HTTPException
from stablediffusion.comfyUI_servers import get_server_by_index

# 워크플로우 로드 함수
def get_workflow(path: str = "illust.json"):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"{path} 파일이 없습니다.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 이미지 생성 요청 함수
def generate_image_from_prompt(file_name: str, prompt: str, server_url: str):
    try:
        workflow = get_workflow()

        for node in workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt
            elif node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = file_name

        res = requests.post(f"{server_url}/prompt", json={"prompt": workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # Polling: 최대 30초 대기
        for _ in range(30):
            result = requests.get(f"{server_url}/history/{prompt_id}")
            result.raise_for_status()
            outputs = result.json().get(prompt_id, {}).get("outputs", {})
            if outputs:
                break
            time.sleep(1)

        if not outputs:
            raise HTTPException(status_code=500, detail="출력 결과가 비어 있습니다.")

        first_output = next(iter(outputs.values()))
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{server_url}/view?filename={image_filename}&type=output"

        return {
            "image_url": image_url,
            "image_filename": image_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")
