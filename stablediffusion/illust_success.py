import os
import json
import time
import requests
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from stablediffusion.comfyUI_servers import get_server_by_index, get_first_server



#  ComfyUI 환경 변수 설정
COMFYUI_URL = "https://additions-both-described-intended.trycloudflare.com"

WORKFLOW_PATH = "illust.json"

def get_workflow():
    #워크플로우 파일 로드 및 예외처리
    if not os.path.exists(WORKFLOW_PATH):
        raise HTTPException(status_code=404, detail="illust.json 파일이 없습니다.")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

workflow = get_workflow()

#  이미지 생성 함수(비동기)
def generate_image_from_prompt(file_name: str, prompt: str, server_url: str):
    try:
        raw_workflow = get_workflow()

        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt
            elif node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = file_name

        res = requests.post(f"{server_url}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        for _ in range(30):
            result = requests.get(f"{server_url}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()
            outputs = result_json.get(prompt_id, {}).get("outputs", {}) or result_json.get("outputs", {})
            if outputs:
                break
            time.sleep(1)

        if not outputs:
            raise Exception("출력 결과가 비어 있습니다.")

        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{server_url}/view?filename={image_filename}&type=output"

        return {
            "image_url": image_url,
            "image_filename": image_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))