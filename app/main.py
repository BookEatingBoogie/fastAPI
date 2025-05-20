from typing import Dict
import uuid
from fastapi import FastAPI

from app.schemas.endingRequest import endingRequest
from app.schemas.contentRequest import contentRequest
from app.schemas.imgPrompt import imgUrl
from app.schemas.introRequest import introRequest
from app.service.getImgPromptService import *
from app.service.getStoryService import *
from app.service.onBackground import *
from app.service.storyFormating import *
from stablediffusion.illust_high import generate_image_high_from_prompt
from stablediffusion.s3_uploader import *
from stablediffusion.illust_success import *
from stablediffusion.character_success import *
from stablediffusion.comfyUI_uploader import uploadImage_to_comfyUI

app = FastAPI()

# 생성된 동화 저장
STORY = []
# 생성된 삽화 프롬프트 저장
ILLUST_PROMPT = []
# 생성된 캐릭터 이미지 저장
ILLUST_URL = []
# 생성된 캐릭터 캐릭터 정보
CHAR_LOOK = ""
# 사용자 사진
FILE_NAME = ""

RESPONSE_ID = ""

# 캐릭터 정보
characterInfo = ""

# 캐릭터 이미지 생성 후 s3에 저장. 이미지 경로 반환.
@app.post("/generate/character/")
async def generateCharacter(imgUrl: imgUrl):
    loop = asyncio.get_running_loop()

    print(imgUrl.imgUrl)

    # S3 이미지 경로로 gpt에 이미지 전송.
    try:

         # 1) S3에서 이미지 다운로드 (blocking) → 스레드 풀에 위임
        upload_task = loop.run_in_executor(None, uploadImage_to_comfyUI, imgUrl.imgUrl)
        # 2) prompt 생성 함수도 blocking이면 스레드 풀에 위임
        prompt_task   = loop.run_in_executor(None, createCharacter, imgUrl.imgUrl)
         # 두 작업을 동시에 진행 → 둘 다 완료되면 결과를 한꺼번에 받음
        file_name, imgPrompt = await asyncio.gather(upload_task, prompt_task)

        result = await generate_character_from_prompt(file_name, imgPrompt)

        image_url = result["image_url"]
        filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )
        print(s3_url)

        return {
            "s3_url": s3_url,
            "charLook": imgPrompt
        }

    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"캐릭터 생성 실패: {e}")





# 비동기 처리 시 주의사항
# 1. 비동기 처리 하면서 story 배열에 스토리 저장하면 안됨. 따로 선택지(ex.choices) 배열을 생성해서 1,2,3 순서대로 저장하던가, "선택지1":"동화1"...이런식으로 저장해뒀다가
# 사용자가 선택하는 선택지에 따라 해당 선택지의 스토리를 story 배열에 저장해야함.
# 2. 삽화 생성에 대해서도 동일하게 적용됨. illustPrompt 배열에 삽화 프롬프트를 바로 저장하면 안되고, 선택한 선택지의 삽화 프롬프트만 넣어줘야됨.

# 전역 상태 저장소
#    { request_id: { scene_idx: { choice: Task, … }, … }, … }
tasks: Dict[str, Dict[int, Dict[str, asyncio.Task]]] = {}

# 동화 도입부 생성
@app.post("/generate/intro/")
async def getIntro(introRequest: introRequest):

    global STORY, ILLUST_URL, CHAR_LOOK, FILE_NAME, RESPONSE_ID, ILLUST_PROMPT

    STORY = []
    ILLUST_URL = []
    CHAR_LOOK = ""
    FILE_NAME = ""
    RESPONSE_ID = ""

    try:
        intro, responseId = generateIntro(introRequest)

        # 스토리 저장
        STORY.append(intro.intro)
        FILE_NAME = getFileName(introRequest.imgUrl)

        imgPrompt = createStoryImage(intro.intro)

        CHAR_LOOK = formatCharLook(introRequest.charLook, intro.charLook)
        print(CHAR_LOOK)

        # 삽화 프롬프트 저장
        ILLUST_PROMPT.append(imgPrompt)
        result = generate_image_from_prompt(FILE_NAME, imgPrompt)
        
        print(result)

        RESPONSE_ID = responseId

        requestId = str(uuid.uuid4())
        print(requestId)
        tasks[requestId] = {}

        tasks[requestId][1] = {}
        for choice in intro.options:
            t = asyncio.create_task(
                handle_generate_scene(requestId, 1, FILE_NAME, choice, introRequest.charName, CHAR_LOOK, RESPONSE_ID)
            )
            tasks[requestId][1][choice] = t
        print(f"scene 1 생성 시작. {t}")
        # 삽화 이미지 업로드    
        image_url = result["image_url"]
        filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{filename}"
        )

        ILLUST_URL.append(s3_url)

        print(requestId)

        return {
            "requestId": requestId,
            "intro": intro.intro,
            "question": intro.question,
            "options": intro.options,
            "charLook": intro.charLook,
            "s3_url": s3_url,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동화 : 도입부 생성 실패: {e}")


# 동화 중심부 생성
@app.post("/generate/content/")
async def getContent(contentRequest: contentRequest):

    global STORY, ILLUST_URL, CHAR_LOOK, FILE_NAME, RESPONSE_ID, ILLUST_PROMPT

    requestId = contentRequest.requestId
    sceneIdx = contentRequest.page

    print(f"fastapi 실행 시작: {requestId}, {sceneIdx}")

    # 비동기로 동화가 생성되지 않았을 경우, 실시간으로 동화 뒷내용 생성.
    if requestId not in tasks or sceneIdx not in tasks[requestId]:
        result = await getContentNow(contentRequest.choice, contentRequest.charName, RESPONSE_ID, FILE_NAME, contentRequest.page)
    else:
        # 비동기로 생성된 동화 장면 가져오기
        scene_tasks = tasks[requestId][sceneIdx]

        if contentRequest.choice not in scene_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"선택한 '{contentRequest.choice}'는 존재하지 않습니다. 가능한 값: {list(scene_tasks.keys())}"
            )

        # 선택되지 않은 선택지에 대하여 실행 취소.
        for choice, task in list(scene_tasks.items()):
            if choice != contentRequest.choice:
                task.cancel()
                del scene_tasks[choice]

        # 선택된 선택지에 대하여 동화 생성 완료 대기.
        try:
            result = await asyncio.wait_for(scene_tasks[contentRequest.choice], timeout=60)
        except Exception as e:
            raise HTTPException(status_code=e.status_code, detail=f"scene {sceneIdx} 생성 실패: {e}")
        print(f"scene {sceneIdx} 생성 완료: {result}")

        STORY.append(result["story"])
        ILLUST_PROMPT.append(result["illust_prompt"])
        ILLUST_URL.append(result["s3_url"])

        RESPONSE_ID = result["responseId"]

        tasks[requestId][sceneIdx+1] = {}
        for choice in result["choices"]:
            if sceneIdx == 5:
                t = asyncio.create_task(
                    handle_generate_ending(requestId, FILE_NAME, choice, contentRequest.charName, CHAR_LOOK, RESPONSE_ID)
                )
            else:
                t = asyncio.create_task(
                    handle_generate_scene(requestId, sceneIdx+1, FILE_NAME, choice, contentRequest.charName, CHAR_LOOK, RESPONSE_ID)
                )
            tasks[requestId][sceneIdx+1][choice] = t
            print(f"scene {sceneIdx+1} 생성 시작.")

        return {
            "requestId": requestId,
            "story": result["story"],
            "question": result["question"],
            "choices": result["choices"],
            "s3_url": result["s3_url"]
        }


# 전체 동화를 정제. 최종 동화 반환.
@app.post("/generate/story/")
async def getStory(endingRequest: endingRequest):

    global STORY, ILLUST_URL, CHAR_LOOK, FILE_NAME, RESPONSE_ID, ILLUST_PROMPT
    
    loop = asyncio.get_running_loop()

    requestId = endingRequest.requestId
    sceneIdx = endingRequest.page

    if requestId not in tasks or sceneIdx not in tasks[requestId]:
        result = await getEndingNow(endingRequest.choice, endingRequest.charName, RESPONSE_ID)
    else:
        scene_tasks = tasks[requestId][sceneIdx][endingRequest.choice]

        try:
            result = await asyncio.wait_for(scene_tasks, timeout=60)
        except Exception as e:
            raise HTTPException(status_code=e.status_code, detail=f"scene {sceneIdx} 생성 실패: {e}")
    
        STORY.append(result["story"])
        ILLUST_PROMPT.append(result["illust_prompt"])
        ILLUST_URL.append(result["s3_url"])
    
    # 동화 전체 정제 -> 삽화 재생성 기다려서 이미지 url과 함께 페이지별로 엮어서 json 파일 생성. -> 파일 이름은 storyId.json -> 파일 저장 위치는 s3.
   
    render_result, high_illusts = await asyncio.gather(
        generateStory(STORY),
        generate_illust_high(FILE_NAME, ILLUST_PROMPT, endingRequest.storyId)
    )
    
    formattedStory = formatStory(render_result.paragraphs, high_illusts)

    # 파일 이름은 storyId.json -> 파일 저장 위치는 s3.
    s3_url = upload_file(
        file_content=formattedStory,
        bucket_name="bookeating", 
        s3_key=f"storybook/{endingRequest.storyId}/content.json"
    )
    print("동화 S3 업로드 완료!")

    STORY = []
    ILLUST_URL = []
    ILLUST_PROMPT = []

    return s3_url


@app.post("/test/")
async def test():

    formattedStory = [
        "story", "test",
        "illustUrl", "test"
    ]
    
    try:
        user_content = [{"type": "text", "text": scene} for scene in formattedStory]

        response = client.responses.parse(
        model="gpt-4o-2024-11-20",
        input=[
            {"role": "developer", "content": "You are responsible for refining an array of separated fairytale scenes into a smoothly connected story. The input and output must remain in array format, and both the order and number of scenes must be preserved."+
            "Improve the flow and emotional continuity by adjusting expressions or adding transitional phrases within each scene. Keep the core meaning intact, but feel free to rephrase naturally."+
            "Each scene must be written in Korean and limited to 300 characters or fewer.  Do not include any extra explanations or formatting."},
            {"role": "user", "content": user_content}
        ],
        text_format=renderOutput
        )
        
        return {"status": "success", "s3_url": response.output_parsed}
    

    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"생성 실패: {e}")
    

@app.get("/")
def start():
    return {"Hello":"World!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)