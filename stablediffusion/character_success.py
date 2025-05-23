import os
import json
import requests
import asyncio
from fastapi import HTTPException

# 설정값
COMFYUI_URL = "https://jewellery-dubai-placing-poems.trycloudflare.com"
WORKFLOW_PATH = "character.json"

def get_workflow():
    # 워크플로우 파일 확인
    if not os.path.exists(WORKFLOW_PATH):
        raise HTTPException(status_code=404, detail=f"{WORKFLOW_PATH} 워크플로우 파일이 없습니다.")
    # 워크플로우 로딩 및 수정
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

workflow = get_workflow()

async def generate_character_from_prompt(file_name: str, prompt: str):
    print(file_name)
    try:
        global workflow
        if workflow is None:
            raise Exception("워크플로우 파일이 로드되지 않았습니다.")
        raw_workflow = workflow

        for node in raw_workflow.values():
            if not isinstance(node, dict):
                continue

            # 프롬프트 삽입
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

            # 이미지 파일명 교체 (pose 관련 이미지는 유지)
            elif node.get("class_type") == "LoadImage":
                if node["inputs"].get("image") != "posefinal.png":
                    node["inputs"]["image"] = file_name

            # 저장 노드 설정
            elif node.get("class_type") == "SaveImage":
                node["inputs"].setdefault("filename_prefix", "output")

        # ComfyUI에 프롬프트 전송
        res = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # Polling: 이미지 생성 기다리기 (최대 60초) ---> 이유가?
        outputs = {}
        for _ in range(60):
            result = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()

            outputs = result_json.get(prompt_id, {}).get("outputs", {})
            if outputs:
                found = any("images" in node and node["images"] for node in outputs.values())
                if found:
                    break

            await asyncio.sleep(1)

        if not outputs:
            raise HTTPException(status_code=500, detail="출력 결과가 비어 있습니다.")

        # 이미지 포함 노드에서 filename 추출
        image_filename = None
        for node in outputs.values():
            if isinstance(node, dict) and "images" in node and node["images"]:
                image_filename = node["images"][0]["filename"]
                break

        if not image_filename:
            raise HTTPException(status_code=500, detail="'images' 키가 있는 노드를 찾을 수 없습니다.")

        # 이미지 URL 생성
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"

        # 결과 반환
        return {
            "image_url": image_url,
            "image_filename": image_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
