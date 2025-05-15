import os
import json
import requests
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


#  ComfyUI 환경 변수 설정
COMFYUI_URL = "https://alternatively-knows-overview-textiles.trycloudflare.com"
WORKFLOW_PATH = "background.json"

#  요청 데이터 모델 정의
class PromptRequest(BaseModel):
    prompt: str

async def generate_background_from_prompt(prompt: str):
    try:
        # 워크플로우 파일 로드
        if not os.path.exists(WORKFLOW_PATH):
            raise HTTPException(status_code=404, detail=f"{WORKFLOW_PATH} 파일이 없습니다.")
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            raw_workflow = json.load(f)

        # 텍스트 프롬프트 삽입
        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

        # ComfyUI에 프롬프트 전달
        res = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # 결과 polling
        for _ in range(30):
            result = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()
            outputs = result_json.get(prompt_id, {}).get("outputs", {}) or result_json.get("outputs", {})
            if outputs:
                break
            await asyncio.sleep(1)

        if not outputs:
            raise Exception("출력 결과가 비어 있습니다.")

        # 출력 이미지 추출
        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"

        return {
            "status": "success",
            "prompt": prompt,
            "image_url": image_url,
            "used_image_name": "background.png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

