from fastapi import FastAPI

from app.schemas.endingRequest import endingRequest
from app.schemas.contentRequest import contentRequest
from app.schemas.imgPrompt import imgUrl
from app.schemas.introRequest import introRequest
from app.service.getImgPromptService import *
from app.service.getStoryService import *
from app.service.storyFormating import *
from stablediffusion.s3_uploader import *
from stablediffusion.illust_success import *
from stablediffusion.character_success import *
from stablediffusion.comfyUI_uploader import uploadImage_to_comfyUI

app = FastAPI()

# 생성된 동화 저장
story = []
# 생성된 삽화 프롬프트 저장
illustPrompt = []
# 생성된 캐릭터 이미지 저장
illustUrl = []
# 생성된 캐릭터 캐릭터 정보
charLook = ""

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


# 동화 도입부 생성
@app.post("/generate/intro/")
async def getIntro(introRequest: introRequest):

    global story, illustUrl, charLook

    story = []
    illustUrl = []

    try:
        intro = generateIntro(introRequest)

        # 스토리 저장
        story.append(intro.intro)
        file_name = getFileName(introRequest.imgUrl)

        imgPrompt = createStoryImage(intro.intro)
        illustPrompt.append(imgPrompt)
        result = await generate_image_from_prompt(file_name, imgPrompt)
        charLook = formatCharLook(introRequest.charLook, intro.charLook)
        print(charLook)

        image_url = result["image_url"]
        filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{filename}"
        )

        illustUrl.append(s3_url)

        return {
            "intro": intro.intro,
            "question": intro.question,
            "options": intro.options,
            "charLook": intro.charLook,
            "s3_url": s3_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"동화 : 도입부 생성 실패: {e}")


# 동화 중심부 생성
@app.post("/generate/content/")
async def getContent(contentRequest: contentRequest):

    global story, illustUrl, charLook

 
    try:
        if contentRequest.page == 1:
            content = generateFinalQuestion(contentRequest)
        else:
            content = generateContent(contentRequest)

        # 스토리 저장
        story.append(content.story)
        file_name = getFileName(contentRequest.imgUrl)

        imgPrompt = createStoryImage(content.story) + charLook
        illustPrompt.append(imgPrompt)
        result = await generate_image_from_prompt(file_name, imgPrompt)

        image_url = result["image_url"]
        image_filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{image_filename}"
        )

        illustUrl.append(s3_url)

        print(content.options)

        return {
            "story": content.story,
            "question": content.question,
            "choices": content.options,
            "s3_url": s3_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"동화 : 중간부 생성 실패: {e}")


# 전체 동화를 정제. 최종 동화 반환.
@app.post("/generate/story/")
async def getStory(endingRequest: endingRequest):

    global story, illustUrl, charLook

    try:
        # 동화 엔딩 생성
        ending = generateEnding(endingRequest)
        story.append(ending.story)
        file_name = getFileName(endingRequest.imgUrl)

        imgPrompt = createStoryImage(ending.story) + charLook
        illustPrompt.append(imgPrompt)
        print("createStory, imageprompt 완성!")
        result = await generate_image_from_prompt(file_name, imgPrompt)
        print("이미지 생성 완료!")
        image_url = result["image_url"]
        image_filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{image_filename}"
        )
        print("이미지 업로드 완료!")
        illustUrl.append(s3_url)

        # 동화 전체 정제 -> 삽화 재생성 기다려서 이미지 url과 함께 페이지별로 엮어서 json 파일 생성. -> 파일 이름은 storyId.json -> 파일 저장 위치는 s3.
        renderStory = generateStory(story).paragraphs
        print("동화 정제 완료!")
        formattedStory = formatStory(renderStory, illustUrl)

        # 파일 이름은 storyId.json -> 파일 저장 위치는 s3.
        s3_url = upload_file(
            file_content=formattedStory,
            bucket_name="bookeating", 
            s3_key=f"storybook/{endingRequest.storyId}/content.json"
        )
        print("동화 S3 업로드 완료!")
        story = []
        illustUrl = []

        return s3_url
    
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"동화 : 엔딩 생성 및 정제 실패: {e}")



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