# 이 코드는 캐릭터 생성 용 코드입니다.
# openpose를 이용하여 포즈를 고정하고 캐릭터를 생성합니다.
# 포즈 참고 사진은 계속 바꿀 것입니다
# 못생기게 나와도 이해하세요
# 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
import asyncio
import uvicorn
import os

app = FastAPI()

# ComfyUI 주소 (로컬이 아닌 외부 URL 사용 시 변경)
COMFYUI_URL = "https://separated-chad-captured-consultants.trycloudflare.com"
WORKFLOW_PATH = "character.json"

class PromptRequest(BaseModel):
    prompt: str

@app.post("/image")
async def generate_image(data: PromptRequest):
    try:
        if not os.path.exists(WORKFLOW_PATH):
            raise HTTPException(status_code=404, detail="test.json 파일을 찾을 수 없습니다.")

        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            raw_workflow = json.load(f)

        # 프롬프트 반영 코드
        for node in raw_workflow.values():
            if node.get("class_type") == "CLIPTextEncode":
                if node["inputs"].get("clip") == ["4", 1]:
                    node["inputs"]["text"] = data.prompt

        # SaveImage 노드 추가
        new_node_id = max(map(int, raw_workflow.keys())) + 1
        raw_workflow[str(new_node_id)] = {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "output",
                "images": [
                    "8",  # 기존 VAE 디코딩 노드 ID
                    0
                ]
            },
            "_meta": {
                "title": "이미지 저장"
            }
        }

        payload = {"prompt": raw_workflow}
        print("🔥 ComfyUI로 보낼 JSON 구조:")
        print(json.dumps(payload, indent=2))

        # 프롬프트 전송 코드
        res = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]

        # Polling - 최대 30초간 1초 간격으로 반복 확인
        outputs = {}
        for i in range(30):
            result = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            result.raise_for_status()
            result_json = result.json()

            if prompt_id in result_json:
                outputs = result_json[prompt_id].get("outputs", {})
            else:
                outputs = result_json.get("outputs", {})

            if outputs:
                break
            await asyncio.sleep(1)

        if not outputs:
            raise Exception("출력 결과가 비어 있습니다. (이미지 생성에 실패했을 수 있습니다)")

        # SaveImage 노드에서 이미지 추출
        image_url = None
        for output in outputs.values():
            if "images" in output:
                image_filename = output["images"][0]["filename"]
                image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"
                break

        if not image_url:
            raise Exception("출력 결과에 이미지가 없습니다.")

        return {
            "status": "success",
            "prompt": data.prompt,
            "image_url": image_url
        }

    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"프롬프트 전송 실패: {str(req_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
