import os
import re
import json
import requests
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

COMFYUI_URL = "https://character-tunes-ending-terminals.trycloudflare.com"
WORKFLOW_PATH = "illust.json"
BASE_IMAGE_NAME = "hello.jpeg"

# 이전에 몇 번째까지 썼는지 추적 (메모리 기반)
current_index = -1

class PromptRequest(BaseModel):
    prompt: str

def get_next_image_name():
    global current_index
    current_index += 1
    if current_index == 0:
        return BASE_IMAGE_NAME
    name, ext = os.path.splitext(BASE_IMAGE_NAME)
    return f"{name} ({current_index}){ext}"

@app.post("/image")
async def generate_image(data: PromptRequest):
    try:
        # 다음 이미지 이름만 계산
        next_image_name = get_next_image_name()
        print(f"📸 다음 이미지 이름: {next_image_name}")

        # illust.json 열기
        if not os.path.exists(WORKFLOW_PATH):
            raise HTTPException(status_code=404, detail="illust.json 파일이 없습니다.")
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            raw_workflow = json.load(f)

        # JSON 내 텍스트와 이미지 경로 반영
        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode" and node["inputs"].get("clip") == ["4", 1]:
                node["inputs"]["text"] = data.prompt
            elif node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = next_image_name  # 💥 경로 확인 안 함, 그냥 값만 넣음

        # ComfyUI로 전송
        payload = {"prompt": raw_workflow}
        res = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
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

        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"

        return {
            "status": "success",
            "prompt": data.prompt,
            "image_url": image_url,
            "used_image_name": next_image_name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로컬 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
