import copy
import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY
from app.schemas.contentOutput import contentOutput
from app.schemas.endingOutput import endingOutput
from app.schemas.introOutput import introOutput
from app.service.storyFormating import formatStory


client = OpenAI(api_key=OPENAI_API_KEY)

responseId = ""


# 동화 도입부 생성 gpt 호출 - 최초 동화 생성 시 호출
def generateIntro(introRequest): # storyStyle: 장소, 장르, 주인공 이름
  
  global responseId

  # 요청 프롬프트
  storyPrompt = f"""Tell a story beginning in {introRequest.place},
  inspired by {introRequest.genre},
  following a main character named {introRequest.charName},
  allowing for unexpected developments.

  Then, based on this story opening, return your answer in a JSON object with 4 fields: 
  1. intro (Korean): Write the story intro **only in Korean** (about 300 characters).
  2. question (Korean): Ask one narrative question  in **Korean only** (where, who, what, or why). The question must not simply summarize or restate what happened in the story. Instead, it should help lead to a meaningful next event or choice.
  3. options (Korean): Give three one-word options related to that question in **Korean only**.
  4. outfit (English): Describe the character’s outfit in one concise sentence in **English only**. Focus only on clothing and accessories (e.g. top, bottom, jewelry, shoes), with no mention of the character’s name or other traits. Match the style and tone to the story’s setting and mood (e.g. fantasy ocean world, magical forest, etc). Use evocative but clear language suitable for use in image generation prompts.

  Important: Respond using the fields and languages exactly as instructed. Do not include explanations, formatting symbols, or extra text.
  """
  
  print(storyPrompt)
  
  try:
    # 동화 도입부 생성 프롬프트
    response = client.responses.parse(
      model="gpt-4o-2024-11-20",
      input=[      
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
        ],
      text_format=introOutput
    )

    # 현재 응답 id 저장
    responseId = response.id

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e


# 동화 내용 생성 gpt 호출 - 중심부 생성 시 호출
def generateContent(contentRequest): # select: 질문 선택지, charName: 주인공 이름

  global responseId
  
  # 요청 프롬프트
  storyPrompt = f"""The user has selected "{contentRequest.choice}" as their answer to the previous question.
  Please continue the story in Korean, writing the next scene.
  This scene should naturally follow the previous events, and reflect the user’s choice within the flow of the narrative.
  It should also include the actions of the main character, {contentRequest.charName}, and their surrounding situation.

  Avoid flat or generic scenes such as “즐거운 시간을 보냈습니다.” or “즐거운 하루를 보냈습니다.” Include some form of tension, surprise, discovery, or a decision the character has to make.

  The question must not simply summarize or restate what happened in the story. Instead, it should help lead to a meaningful next event or choice.

  Then, based on this story opening:
  1. story : Write the story by continuing naturally from the previous events. (about 200 characters).
  2. question : Ask one narrative question (where, who, what, or why). The question should not ask about things that have already been clearly described. It should help move the story forward.
  3. options : Give three one-word options related to that question.

  Important: Respond using the fields and languages exactly as instructed. Do not include explanations, formatting symbols, or extra text. Respond in Korean only.
  """

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4o-2024-11-20",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput
    )

    # 현재 응답 id 저장
    responseId = response.id

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e

# 동화 내용 생성 gpt 호출 - 결말 생성을 위한 질문 생성 프롬프트트
def generateFinalQuestion(contentRequest): # select: 질문 선택지, charName: 주인공 이름

  global responseId
  
  # 요청 프롬프트
  storyPrompt = f"""The user has selected "{contentRequest.choice}" as their answer to the previous question.
  Please continue the story in Korean, writing the next scene.
  This scene should naturally follow the previous events, and reflect the user’s choice within the flow of the narrative.
  It should also include the actions of the main character, {contentRequest.charName}, and their surrounding situation.

  Avoid flat or generic scenes such as “즐거운 시간을 보냈습니다.” or “즐거운 하루를 보냈습니다.” Include some form of tension, surprise, discovery, or a decision the character has to make.

  The question must not simply summarize or restate what happened in the story. Instead, it should help lead to a meaningful next event or choice.

  Then, based on this story opening:
  1. story : Write the story by continuing naturally from the previous events. (about 200 characters).
  2. question : Ask one question to make the ending of the story. The question should not ask about things that have already been clearly described. It should help move the story forward.
  3. options : Give three one-word options related to that question.

  Important: Respond using the fields and languages exactly as instructed. Do not include explanations, formatting symbols, or extra text. Respond in Korean only.
  """

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4o-2024-11-20",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput
    )

    # 현재 응답 id 저장
    responseId = response.id

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e

# 동화 결말부 프롬프트 요청
def generateEnding(contentRequest):

  global responseId

  # 요청 프롬프트
  storyPrompt = f"""The user has selected "{contentRequest.choice}" as their answer to the previous question.
  Please continue the story in Korean, writing the final scene. It's the end of the story.
  The ending should feel complete and meaningful. It must leave a gentle emotional impact or convey a simple, age-appropriate moral for children between 7 and 9 years old.
  Avoid rushed conclusions or vague endings. Show what the main character experiences or learns through the final event.
  Write the ending in Korean, about 300 characters. Do not include any extra explanations or formatting.
  It should also include the actions of the main character, {contentRequest.charName}, and their surrounding situation."""

  # 동화 결말 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4o-2024-11-20",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=endingOutput
    )

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e



def generateStory(story):

  try:
    response = client.responses.create(
      model="gpt-4o-2024-11-20",
      input=[
        {"role": "developer", "content": "You are responsible for refining an array of separated fairytale scenes into a smoothly connected story. The input and output must remain in array format, and both the order and number of scenes must be preserved."+
        "Improve the flow and emotional continuity by adjusting expressions or adding transitional phrases within each scene. Keep the core meaning intact, but feel free to rephrase naturally."+
        "Each scene must be written in Korean and limited to 300 characters or fewer.  Do not include any extra explanations or formatting."},
        {"role": "user", "content": story}
      ]
    )

    print(response.output_text)

    return response.output_text
  except Exception as e:
    raise e








# 동화 삽화 생성 프롬프트 요청
def requestStoryImagePrompt(paragraphs):
  
  # 각 문단에 번호 부여.
  numberedList = formatStory(paragraphs)

  # user 프롬프트
  userPrompt = f"""Here are the story paragraphs:
    {numberedList}
    Please generate one image prompt for each paragraph in the same numbered format."""

  #삽화 생성 프롬프트 요청
  response = client.responses.create(
    model="gpt-4o",
    input=[
      {"role":"developer", "content":"You are an assistant that creates visually rich and detailed image prompts for a text-to-image model like Stable Diffusion. You will receive a numbered list of storybook paragraphs. For each paragraph, generate one corresponding illustration prompt in natural English.\n"+
      "Each prompt should vividly describe the scene as if it were an illustration in a children’s picture book. Include visual elements such as:\n"+
      "- Setting and background (place, time of day, weather)\n"+
      "- Mood or emotional tone"+
      "Respond in the same numbered list format: one image prompt per paragraph. Keep the prompts descriptive, but concise and focused on what should be visually represented in the image.\n"+
      "Do not include title of each image prompt per paragraph."},
      {"role":"user", "content": userPrompt}
    ]
  )
  print(response.output_text)
  return response.output_text