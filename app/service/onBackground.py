# 동화 중간부 생성
import asyncio
from fastapi import HTTPException

from app.schemas.contentRequest import contentRequest
from app.schemas.endingRequest import endingRequest
from app.service.getImgPromptService import createStoryImage
from app.service.getStoryService import *
from app.service.storyFormating import getFileName, process_choices
from stablediffusion.illust_high import generate_image_high_from_prompt
from stablediffusion.illust_success import generate_image_from_prompt
from stablediffusion.s3_uploader import upload_image_to_s3
from stablediffusion.sticker_success import generate_sticker_from_prompt

sticker_url = []

async def handle_generate_scene(request_id: str, scene_idx: int, file_name: str, choice: str, charName: str, charLook: str, responseId: str):
    loop = asyncio.get_running_loop()

    # 동화 엔딩 직전 질문 생성
    if scene_idx == 4:
        content, responseId = await loop.run_in_executor(None, generateFinalQuestion, choice, charName, responseId)
    else:
        # 동화 중간부 생성
        content, responseId = await loop.run_in_executor(None, generateContent, choice, charName, responseId)

    print(f"{scene_idx} 생성 완료: {content.story}")

    # 삽화 프롬프트 생성
    prompt = await loop.run_in_executor(None, createStoryImage, content.story) + charLook
    print(f"{scene_idx} 삽화 프롬프트 생성 완료: {prompt}")
    # 삽화 생성
    result = await loop.run_in_executor(None, generate_image_from_prompt, file_name, prompt)
    print(f"{scene_idx} 삽화 생성 완료: {result}")

    image_url = result["image_url"]
    image_filename = result["image_filename"]

    # 삽화 업로드
    s3_url = await loop.run_in_executor(None, upload_image_to_s3, image_url, "bookeating", f"storybook/temp/{image_filename}")
    print(f"{scene_idx} 삽화 업로드 완료: {s3_url}")

    return {
        "story": content.story,
        "question": content.question,
        "choices": content.options,
        "s3_url": s3_url,
        "illust_prompt": prompt,
        "responseId": responseId
    }
    

# 동화 엔딩 생성
async def handle_generate_ending(request_id: str, file_name: str, choice: str, charName: str, charLook: str):
    loop = asyncio.get_running_loop()

    ending = await loop.run_in_executor(None, generateEnding, choice, charName)
    print(f"엔딩 생성 완료: {ending.story}")

    # 삽화 프롬프트 생성
    prompt = await loop.run_in_executor(None, createStoryImage, ending.story) + charLook
    print(f"엔딩 삽화 프롬프트 생성 완료: {prompt}")

    # 삽화 생성
    result = await loop.run_in_executor(None, generate_image_from_prompt, file_name, prompt)
    print(f"엔딩 삽화 생성 완료: {result}")

    image_url = result["image_url"]
    image_filename = result["image_filename"]

    # 삽화 업로드
    s3_url = await loop.run_in_executor(None, upload_image_to_s3, image_url, "bookeating", f"storybook/temp/{image_filename}")
    print(f"엔딩 삽화 업로드 완료: {s3_url}")

    
    return {
        "story": ending.story,
        "s3_url": s3_url,
        "illust_prompt": prompt
    }


async def getContentNow(choice:str, charName:str, responseId:str, file_name:str, page:int):
    try:
        if page == 4:
            content, responseId = generateFinalQuestion(choice, charName, responseId)
        else:
            content, responseId = generateContent(choice, charName, responseId)

        imgPrompt = createStoryImage(content.story) + charName
        result = generate_image_from_prompt(file_name, imgPrompt)

        image_url = result["image_url"]
        image_filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{image_filename}"
        )


        return {
            "story": content.story,
            "question": content.question,
            "choices": content.options,
            "s3_url": s3_url,
            "illust_prompt": imgPrompt,
            "responseId": responseId
        }
    
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"동화 : 중간부 생성 실패: {e}")


async def getEndingNow(choice:str, charName:str, responseId:str, file_name:str):
    try:
        # 동화 엔딩 생성
        ending = generateEnding(choice, charName, responseId)

        imgPrompt = createStoryImage(ending.story) + charName

        result = generate_image_from_prompt(file_name, imgPrompt)
        image_url = result["image_url"]
        image_filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating", 
            s3_key=f"storybook/temp/{image_filename}"
        )
        
        return {
            "story": ending.story,
            "s3_url": s3_url,
            "illust_prompt": imgPrompt
        }
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"동화 : 엔딩 생성 실패: {e}")
    
async def get_english_choice(choices: list[str]):
    print(choices)
    object_or_not = await asyncio.gather(*(process_choices(w) for w in choices))
    print(object_or_not)
    return object_or_not

async def call_sticker_generator(choices: list[str]):
    object_or_not = await get_english_choice(choices)
    
    for word in object_or_not:
        sticker_prompt = f"a {word}, centered, isolated on a pure white background, full view, realistic lighting, no shadow"
        print(sticker_prompt)
        asyncio.get_running_loop().create_task(generate_sticker_and_store(sticker_prompt))

async def generate_sticker_and_store(prompt: str):
    print("[Sticker] 호출 시작")
    try:
        result = await generate_sticker_from_prompt(prompt)
        image_url = result["image_url"]
        image_filename = result["image_filename"]

        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating",
            s3_key=f"sticker/{image_filename}"
        )
        sticker_url.append(s3_url)
        print(f"[Sticker 생성 완료] {s3_url}")
    except Exception as e:
        print(f"[Sticker Error] 생성 실패: {e}")


async def generate_illust_high(file_name: str, prompts: list, storyId: str):
    loop = asyncio.get_running_loop()

    tasks = [
        generate_image_high_from_prompt(file_name, prompt)
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks, return_exceptions=False)

    formatted_results = list(results)

    image_urls = []       
    for result in formatted_results:
        image_url = result["image_url"]
        image_filename = result["image_filename"]
        s3_url = upload_image_to_s3(
            image_url=image_url,
            bucket_name="bookeating",
            s3_key=f"storybook/{storyId}/{image_filename}")
        image_urls.append(s3_url)
    return image_urls
