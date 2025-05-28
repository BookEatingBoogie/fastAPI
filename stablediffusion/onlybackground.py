import os
import json
import requests
import asyncio
from fastapi import HTTPException
from stablediffusion.comfyUI_servers import get_server_by_index  # ✅ 서버 분산 로직 활용

# 워크플로우 파일 경로 설정
WORKFLOW_PATH = "background.json"

def get_workflow():
    """워크플로우 JSON 파일을 불러옴"""
    if not os.path.exists(WORKFLOW_PATH):
        raise HTTPException(status_code=404, detail=f"{WORKFLOW_PATH} 파일이 없습니다.")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

async def generate_background_from_prompt(file_name: str, prompt: str, server_url: str):
    """배경 이미지를 생성 (file_name은 일관성을 위한 인자, 사용되지 않음)"""
    try:
        workflow = get_workflow()

        # 텍스트 프롬프트 삽입
        for node in workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

        # ComfyUI에 워크플로우 전송
        res = requests.post(f"{server_url}/prompt", json={"prompt": workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # 결과 polling (최대 30초)
        for _ in range(30):
            result = requests.get(f"{server_url}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()
            outputs = result_json.get(prompt_id, {}).get("outputs", {}) or result_json.get("outputs", {})
            if outputs:
                break
            await asyncio.sleep(1)

        if not outputs:
            raise Exception("출력 결과가 비어 있습니다.")

        # 이미지 출력 정보 추출
        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{server_url}/view?filename={image_filename}&type=output"

        return {
            "image_url": image_url,
            "image_filename": image_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
