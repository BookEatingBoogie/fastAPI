import re


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
