import os
import json
import requests
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


#  ComfyUI 환경 변수 설정
COMFYUI_URL = "https://jewellery-dubai-placing-poems.trycloudflare.com"
WORKFLOW_PATH = "illust_1024.json"

def get_workflow():
    #워크플로우 파일 로드 및 예외처리
    if not os.path.exists(WORKFLOW_PATH):
        raise HTTPException(status_code=404, detail=f"{WORKFLOW_PATH} 파일이 없습니다.")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

workflow = get_workflow()

#  이미지 생성 함수(비동기)
async def generate_image_high_from_prompt(file_name: str, prompt: str):
    try:
        # 워크플로우 파일 로드
        global workflow
        if workflow is None:
            raise Exception("워크플로우 파일이 로드되지 않았습니다.")
        raw_workflow = workflow

        # 워크플로우 내 텍스트 및 이미지 입력 값 수정
        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt
            elif node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = file_name

        # ComfyUI에 프롬프트 전달 (POST 요청)
        res = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": raw_workflow})
        res.raise_for_status()
        # prompt_id는 생성된 작업 ID
        prompt_id = res.json()["prompt_id"]

        # ComfyUI에서 결과를 가져오기 위한 대기(비동기로 최대 30초간 결과 polling함)
        for _ in range(30):
            result = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()
            outputs = result_json.get(prompt_id, {}).get("outputs", {}) or result_json.get("outputs", {})
            if outputs: 
                break
            await asyncio.sleep(1)

        # 결과가 비어 있으면 예외 발생
        if not outputs:
            raise Exception("출력 결과가 비어 있습니다.")
        
        # 첫 번째 출력 이미지 정보 추출
        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"


        # 최종 결과 반환(필요 없으면 지워도 됨)
        return {
            "image_url": image_url,
            "image_filename": image_filename
        }
    
    # 예외 발생 시 HTTPException 반환
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

