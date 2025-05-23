import re
import pandas as pd
import os
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("C:/BookEating/model-obelisk-460705-i3-cb0d1bb7542d.json")

# 한글-영어 맵핑 사전 읽어오기
df = pd.read_csv('object_mapping.csv', encoding='utf-8')
object_dict = dict(zip(df['Korean'], df['English']))

def formatStory(renderStory, illustUrl):
    formattedStory = [
        {"story": story, "illustUrl": url}
        for story, url in zip(renderStory, illustUrl)
    ]
    return formattedStory

def getFileName(imgUrl: str):
    return imgUrl.split("/")[-1]

def formatPrompt(text):
    formatedPrompt = f'{{"prompt": "{text}"}}'
    return formatedPrompt

def formatCharLook(base, outfit):
    # "Wearing" 앞까지 분리
    parts = re.split(r'(?i)\bwearing\b', base, maxsplit=1)
    pre_wear = parts[0].strip().rstrip('.')

    # 새 outfit으로 재조합
    new_charLook = f"{pre_wear}. Wearing {outfit.lower()}."

    return new_charLook

# 한글 선택지 영어로 번역. - 단어가 사전에 없는 경우.
def translate_with_google(word: str, project_id="model-obelisk-460705-i3"):
    client = translate.TranslationServiceClient()
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [word],
            "mime_type": "text/plain",
            "source_language_code": "ko-KR",
            "target_language_code": "en-US",
        }
    )
    for translation in response.translations:
        print(f"번역 완료: {word}, {translation.translated_text}")
        return translation.translated_text

# # 선택지 객체화 -> 영어로 변환.
async def process_choices(choice):
    print(choice)
    if choice in object_dict:
        print(f"선택지 사전 여부 확인: {choice}, {object_dict[choice]}")
        return object_dict[choice]
    else:
        translated_choice = translate_with_google(choice)
        print(f"번역 확인: {translated_choice}, True")
        return translated_choice

