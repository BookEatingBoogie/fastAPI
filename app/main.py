from fastapi import FastAPI

from app.schemas.contentRequest import contentRequest
from app.schemas.imgPrompt import imgUrl
from app.schemas.introRequest import introRequest
from app.service.getImgPromptService import *
from app.service.getStoryService import *
from app.schemas.gptPrompt import gptPrompt
from app.service.storyFormating import splitParagraphs
from app.service.storyFormating import formatPrompt
from stablediffusion.image_uploader import save_and_upload_image
from stablediffusion.illust_success import *
from stablediffusion.character_success import *


# 캐릭터 및 스토리 질문 횟수
characterQuestionNum = 8
storyQuestionNum = 8

app = FastAPI()

# 생성된 동화 저장
story = []

# 캐릭터 정보
characterInfo = ""

# 캐릭터 이미지 생성 후 s3에 저장. 이미지 경로 반환.
@app.post("/generate/character/")
async def generateCharacter(imgUrl: imgUrl):

    print(imgUrl.imgUrl)
    
    # S3 이미지 경로로 gpt에 이미지 전송.
    try:
        imgPrompt = createCharacter(imgUrl.imgUrl)

        result = await generate_character_from_prompt(imgPrompt)

        image_url = result["image_url"]
        filename = result["used_image_name"]
        s3_url = save_and_upload_image(
            image_url=image_url,
            local_filename=filename,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )

        return {"status": "success", "s3_url": s3_url}

    except Exception as e:
        return {"status": "error", "message": f"캐릭터 생성 실패: {e}"}


# 동화 삽화 생성 후 s3에 저장. 이미지 경로 반환.
@app.post("/generate/illust/")
async def generateIllust(scene: str):
    try:
        imgPrompt = createStoryImage(scene)

        result = await generate_image_from_prompt(imgPrompt)

        image_url = result["image_url"]
        filename = result["used_image_name"]
        s3_url = save_and_upload_image(
            image_url=image_url,
            local_filename=filename,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )

        return {"status": "success", "s3_url": s3_url}

    except Exception as e:
        return {"status": "error", "message": f"동화 삽화 생성 실패: {e}"}








# 동화 도입부 생성
@app.post("/generate/intro/")
async def getIntro(introRequest: introRequest):

    global story

    try:
        intro = generateIntro(introRequest)

        # 스토리 저장
        story.append(intro["intro"])
    
        return intro
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}


# 동화 중심부 생성
@app.post("/generate/content/")
async def getContent(contentRequest: contentRequest):

    global story

    try:
        content = generateContent(contentRequest)

        # 스토리 저장
        story.append(content["story"])

        return content
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}


# 동화 결말부 생성
@app.post("/generate/ending/")
async def getEnding(contentRequest: contentRequest):

    global story

    try:
        ending = generateEnding(contentRequest)

        # 스토리 저장
        story.append(ending["ending"])

        return ending
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}

# 전체 동화를 정제. 최종 동화 반환.
@app.post("/generate/story/")
async def generateStory():

    global story

    try:
        finalStory = generateStory(story)

        story = []

        return finalStory
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}



@app.post("/test/")
async def test(imgUrl: imgUrl):
    
    try:
        imgPrompt = createCharacter(imgUrl.imgUrl)

        return {"status": "success", "imgPrompt": imgPrompt}
    except Exception as e:
        return {"status": "error", "message": f"캐릭터 생성 실패: {e}"}
    

@app.get("/")
def start():
    return {"Hello":"World!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)