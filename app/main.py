from fastapi import FastAPI
from app.service.gptService import *
from app.schemas.gptPrompt import gptPrompt
from app.schemas.storyStyle import storyStyle
from app.service.storyFormating import splitParagraphs
from app.service.storyFormating import formatPrompt
from stablediffusion.image_uploader import save_and_upload_image
from stablediffusion.illust_success import *
from stablediffusion.character_success import *


# 캐릭터 및 스토리 질문 횟수
characterQuestionNum = 8
storyQuestionNum = 8

app = FastAPI()


# 실제 횟수 차감하는 변수
questionNum = characterQuestionNum

# 캐릭터 정보
characterInfo = ""

@app.post("/generate/character/")
async def generateCharacter(prompt: gptPrompt):

    global questionNum
    global characterInfo

    #questionNum-=1
    print(questionNum)

    # 캐릭터 생성 질문 리턴
    genQuestion = callGPT_character(prompt.userContent)

    # 질문 횟수가 0번 남으면(=질문이 끝나면) json 형식으로 정리.
    if questionNum == 8:
        questionNum = characterQuestionNum
        characterInfo = getCharacterJson()
        print(characterInfo)
        
        formatted_info = formatPrompt(characterInfo)
        
        english_prompt = createCharacter(formatted_info)

        result = await generate_character_from_prompt(english_prompt)
        
        
        image_url = result["image_url"]
        filename = result["used_image_name"]
        s3_url = save_and_upload_image(
            image_url=image_url,
            local_filename=filename,
            bucket_name="bookeating", 
            s3_key=f"storybook/{filename}"
        )

        return {"status": "success", "s3_url": s3_url}
    
    return genQuestion


@app.post("/generate/story/")
async def generateStory(storyStyle: storyStyle):
    response = getCharacterJson()
    story = generateStory(response, storyStyle)
    separateParagraph = splitParagraphs(story)
    return generateStory(response, storyStyle)

@app.post("/test/")
async def test():
    story = "깊은 바다 속에서, 어린아이들을 태운 작은 배가 항해하고 있었어요. 그 중에는 곱슬머리에 빨간색 땡땡이 원피스를 입은 박지연도 있었지요. 그녀는 갈색 샌들과 꽃모양 머리핀을 하고 친구들과 배를 타고 놀러 가고 있어요. \n\n지연이는 친구들과 언제나 즐거운 시간을 보내요. 모두와 쉽게 친해지기 때문에 어떤 모험을 하든 항상 친구들이 따라오죠. 하지만 오늘은 바다의 신비한 섬으로 가는 길이라 조금 긴장했어요.\n\n배가 조용한 해역에 도착하자, 갑자기 어두운 먹구름이 하늘을 덮었어요. 바다가 거칠어지면서 친구들은 모두 불안해졌어요. 하지만 지연이는 애써 웃으며 친구들을 안심시켰어요.\n\n갑자기, 파도 사이에서 빛나는 물고기가 나타났어요. \"안녕하세요, 저는 바다의 요정이에요!\" 물고기가 말했어요. 지연이와 친구들은 신기하고 놀라서 눈을 크게 뜨고 요정을 바라봤어요.\n\n바다의 요정은 친구들을 도와주러 왔어요. \"이 바다의 비밀을 푸는 열쇠를 알면 무사히 지날 수 있어요,\" 라며 요정은 빛나는 진주를 손에 쥐어주었어요.\n\n지연이는 친구들을 모아서 진주를 연구하기 시작했어요. 함께 힘을 모아 퍼즐을 풀어나갔어요. 그들은 서로 도우며 지혜를 모았어요. \n\n드디어, 진주가 반짝이며 퍼즐이 풀렸어요. 구름이 걷히고, 평화로운 햇살이 바다 위로 쏟아졌어요. 모두가 환호성을 질렀어요.\n\n바다의 요정도 기뻐하며 말을 했어요, \"친구들과의 협력 덕분이에요. 잘했어요, 지연아!\" 요정은 다시 물속으로 사라졌지만, 그들의 우정은 더욱 단단해졌어요.\n\n이후로 지연이와 친구들은 바다 여행을 계속했어요. 그들은 바다의 아름다움을 마음껏 즐기며 새로운 모험을 꿈꿨어요.\n\n비록 바다가 가끔 거칠었지만, 지연이는 친구들 곁에 있어 더 이상 짓궂은 파도도 두렵지 않았어요.\n\n그리고 시간이 흐르며 지연이는 바다와 친구들의 가치를 더 깊이 이해하게 되었어요. 그들은 함께라면 어떤 모험도 이겨낼 수 있다는 것을 배웠어요.\n\n지연이의 마음속의 두려움은 사라지고, 대신 용기와 희망이 가득 차게 되었어요. 이번 모험에서 큰 성장을 이룬 것이에요.\n\n그렇게 지연이와 친구들은 서로에게 힘이 되어주며, 언제나 더 나은 모험을 꿈꿀 준비를 마쳤어요."
    seperateParagraph = splitParagraphs(story)
    imagePrompt = requestStoryImagePrompt(seperateParagraph)
    return imagePrompt
    

@app.get("/")
def start():
    return {"Hello":"World!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)