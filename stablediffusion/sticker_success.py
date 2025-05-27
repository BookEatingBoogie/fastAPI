import os
import json
import requests
import asyncio
from fastapi import HTTPException
from stablediffusion.comfyUI_servers import get_server_by_index

# 워크플로우 경로 및 초기 로딩
WORKFLOW_PATH = "background_no_bg.json"

def get_workflow():
    if not os.path.exists(WORKFLOW_PATH):
        raise HTTPException(status_code=404, detail=f"{WORKFLOW_PATH} 워크플로우 파일이 없습니다.")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

async def generate_sticker_from_prompt(prompt: str, server_index: int):
    try:
        # 서버 분산 로드
        server_url = get_server_by_index(server_index)
        raw_workflow = get_workflow()

        # 프롬프트 삽입
        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

        # 요청 전송
        res = requests.post(f"{server_url}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # Polling
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

        # 결과 파싱
        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{server_url}/view?filename={image_filename}&type=output"

        return {
            "image_url": image_url,
            "image_filename": image_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[Sticker] 생성 실패: {str(e)}")
