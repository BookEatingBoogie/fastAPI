import os
import json
import requests
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ComfyUI 관련 설정
COMFYUI_URL = "https://blowing-convinced-confused-opening.trycloudflare.com"
WORKFLOW_PATH = "character.json"
BASE_IMAGE_NAME = "hello.jpeg"
current_index = -1

# 요청 데이터 모델 정의
class PromptRequest(BaseModel):
    prompt: str

# 이미지 파일 이름 자동 증가 함수
def get_next_character_name():
    global current_index
    current_index += 1
    if current_index == 0:
        return BASE_IMAGE_NAME
    name, ext = os.path.splitext(BASE_IMAGE_NAME)
    return f"{name} ({current_index}){ext}"

# 실제 이미지 생성 함수
async def generate_character_from_prompt(prompt: str):
    try:
        next_image_name = get_next_character_name()

        if not os.path.exists(WORKFLOW_PATH):
            raise HTTPException(status_code=404, detail="워크플로우 파일이 없습니다.")

        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            raw_workflow = json.load(f)

        # SaveImage 노드에 filename_prefix 추가 (없을 경우)
        for node_id, node in raw_workflow.items():
            if isinstance(node, dict) and node.get("class_type") == "SaveImage":
                if "filename_prefix" not in node.get("inputs", {}):
                    node["inputs"]["filename_prefix"] = "output"

        # Prompt 및 이미지 적용
        for node in raw_workflow.values():
            if not isinstance(node, dict):
                continue

            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

            elif node.get("class_type") == "LoadImage":
                original_image = node["inputs"].get("image", "")
                # pose 관련 이미지는 유지
                if original_image != "posefinish.png":
                    node["inputs"]["image"] = next_image_name

        # 프롬프트 전송
        res = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # 결과 polling
        outputs = {}
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

        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"

        return {
            "status": "success",
            "prompt": prompt,
            "image_url": image_url,
            "used_image_name": next_image_name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 라우터
@app.post("/image")
async def generate_image(data: PromptRequest):
    return await generate_character_from_prompt(data.prompt)
