from fastapi import FastAPI

from app.schemas.endingRequest import endingRequest
from app.schemas.contentRequest import contentRequest
from app.schemas.imgPrompt import imgUrl
from app.schemas.introRequest import introRequest
from app.service.getImgPromptService import *
from app.service.getStoryService import *
from app.service.storyFormating import splitParagraphs
from app.service.storyFormating import formatPrompt
from stablediffusion.image_uploader import save_and_upload_image
from stablediffusion.illust_success import *
from stablediffusion.character_success import *
from stablediffusion.uploadImage import uploadImage

app = FastAPI()

# 생성된 동화 저장
story = []
# 생성된 삽화 프롬프트 저장
illustPrompt = []

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
        upload_task = loop.run_in_executor(None, uploadImage, imgUrl.imgUrl)
        # 2) prompt 생성 함수도 blocking이면 스레드 풀에 위임
        prompt_task   = loop.run_in_executor(None, createCharacter, imgUrl.imgUrl)
         # 두 작업을 동시에 진행 → 둘 다 완료되면 결과를 한꺼번에 받음
        file_name, imgPrompt = await asyncio.gather(upload_task, prompt_task)

        result = await generate_character_from_prompt(file_name, imgPrompt)

        image_url = result["image_url"]
        filename = result["used_image_name"]
        s3_url = save_and_upload_image(
            image_url=image_url,
            local_filename=filename,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )
        print(s3_url)

        return {
            "s3_url": s3_url,
            "charLook": imgPrompt
        }

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







# 비동기 처리 시 주의사항
# 1. 비동기 처리 하면서 story 배열에 스토리 저장하면 안됨. 따로 선택지(ex.choices) 배열을 생성해서 1,2,3 순서대로 저장하던가, "선택지1":"동화1"...이런식으로 저장해뒀다가
# 사용자가 선택하는 선택지에 따라 해당 선택지의 스토리를 story 배열에 저장해야함.
# 2. 삽화 생성에 대해서도 동일하게 적용됨. illustPrompt 배열에 삽화 프롬프트를 바로 저장하면 안되고, 선택한 선택지의 삽화 프롬프트만 넣어줘야됨.


# 동화 도입부 생성
@app.post("/generate/intro/")
async def getIntro(introRequest: introRequest):

    global story

    try:
        intro = generateIntro(introRequest)

        # 스토리 저장
        story.append(intro.intro)

        imgPrompt = createStoryImage(intro.intro)
        illustPrompt.append(imgPrompt)
        result = await generate_image_from_prompt(imgPrompt)
        
        image_url = result["image_url"]
        filename = result["used_image_name"]
        s3_url = save_and_upload_image(
            image_url=image_url,
            local_filename=filename,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )

        return {
            "intro": intro.intro,
            "question": intro.question,
            "options": intro.options,
            "charLook": intro.charLook,
            "s3_url": s3_url
        }
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}


# 동화 중심부 생성
@app.post("/generate/content/")
async def getContent(contentRequest: contentRequest):

    global story

    if contentRequest.page == 1:
        try:
            content = generateFinalQuestion(contentRequest)

            # 스토리 저장
            story.append(content.story)

            imgPrompt = createStoryImage(content.story)
            illustPrompt.append(imgPrompt)
            result = await generate_image_from_prompt(imgPrompt)

            image_url = result["image_url"]
            filename = result["used_image_name"]
            s3_url = save_and_upload_image(
                image_url=image_url,
                local_filename=filename,
                bucket_name="bookeating", 
                s3_key=f"storybook/{filename}"
            )

            print(content.options)

            return {
                "story": content.story,
                "question": content.question,
                "choices": content.options,
                "s3_url": s3_url
            }

        
        except Exception as e:
            return {"status": "error", "message": f"동화 생성 실패: {e}"}
    else:
        try:
            content = generateContent(contentRequest)

            # 스토리 저장
            story.append(content.story)

            imgPrompt = createStoryImage(content.story)
            illustPrompt.append(imgPrompt)
            result = await generate_image_from_prompt(imgPrompt)

            image_url = result["image_url"]
            filename = result["used_image_name"]
            s3_url = save_and_upload_image(
                image_url=image_url,
                local_filename=filename,
                bucket_name="bookeating", 
                s3_key=f"storybook/{filename}"
            )


            print(content.options)

            return {
                "story": content.story,
                "question": content.question,
                "choices": content.options,
                "s3_url": s3_url
            }

        
        except Exception as e:
            return {"status": "error", "message": f"동화 생성 실패: {e}"}


# 전체 동화를 정제. 최종 동화 반환.
@app.post("/generate/story/")
async def getStory(endingRequest: endingRequest):

    global story

    try:
        # 동화 엔딩 생성
        ending = generateEnding(endingRequest)
        story.append(ending.story)

        # 동화 전체 정제 -> 삽화 재생성 기다려서 이미지 url과 함께 페이지별로 엮어서 json 파일 생성. -> 파일 이름은 storyId.json -> 파일 저장 위치는 s3.
        renderStory = generateStory(story)



        story = []

        return renderStory
    
    except Exception as e:
        return {"status": "error", "message": f"동화 생성 실패: {e}"}



@app.post("/test/")
async def test(imgUrl: imgUrl):
    loop = asyncio.get_running_loop()
    
    try:
         # 1) S3에서 이미지 다운로드 (blocking) → 스레드 풀에 위임
        upload_task = loop.run_in_executor(None, uploadImage, imgUrl.imgUrl)
        # 2) prompt 생성 함수도 blocking이면 스레드 풀에 위임
        prompt_task   = loop.run_in_executor(None, createCharacter, imgUrl.imgUrl)
         # 두 작업을 동시에 진행 → 둘 다 완료되면 결과를 한꺼번에 받음
        file_name, imgPrompt = await asyncio.gather(upload_task, prompt_task)
        
        return {"status": "success", "file_name": file_name, "imgPrompt": imgPrompt}
    

    except Exception as e:
        return {"status": "error", "message": f"캐릭터 생성 실패: {e}"}
    

@app.get("/")
def start():
    return {"Hello":"World!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)