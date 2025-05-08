# 이 코드는 삽화 생성을 위한 FastAPI 서버 코드입니다.
# 모델 다운 후 생성하면 5초도 안 걸립니다.
#


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
import asyncio
import uvicorn
import os

app = FastAPI()

#코랩에서 사용한 comfyui는 cloudflare을 사용했기 때문에 url이 항상 변합니다. 이를 고려하여 url을 변경해줘야 합니다.
COMFYUI_URL = "https://administrative-discharge-sunny-modified.trycloudflare.com"
WORKFLOW_PATH = "illust.json"

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

        payload = {"prompt": raw_workflow}
        print(" ComfyUI로 보낼 JSON 구조:")
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

            # 결과 안에 prompt_id 키가 있는 경우
            if prompt_id in result_json:
                outputs = result_json[prompt_id].get("outputs", {})
            else:
                outputs = result_json.get("outputs", {})

            if outputs:
                break
            await asyncio.sleep(1)

        if not outputs:
            raise Exception("출력 결과가 비어 있습니다. (이미지 생성에 실패했을 수 있습니다)")

        first_output = list(outputs.values())[0]
        image_filename = first_output["images"][0]["filename"]
        image_url = f"{COMFYUI_URL}/view?filename={image_filename}&type=output"

        return {
            "status": "success",
            "prompt": data.prompt,
            "image_url": image_url
        }

    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"프롬프트 전송 실패: {str(req_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
