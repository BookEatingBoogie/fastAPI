import copy
import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY
from app.schemas.contentOutput import contentOutput
from app.schemas.endingOutput import endingOutput
from app.schemas.introOutput import introOutput
from app.schemas.renderOutput import renderOutput
from app.service.storyFormating import formatStory


client = OpenAI(api_key=OPENAI_API_KEY)



# 동화 도입부 생성 gpt 호출 - 최초 동화 생성 시 호출
def generateIntro(introRequest): # storyStyle: 장소, 장르, 주인공 이름
  
  # 요청 프롬프트
  storyPrompt = f"""Tell a story beginning in {introRequest.place},
  inspired by {introRequest.genre},
  following a main character named {introRequest.charName},
  allowing for unexpected developments.

  Make sure the story intro ends with the character experiencing or discovering something curious or unexpected.  
  This could be: entering a hidden place (e.g. cave, door, portal), noticing a strange sound, seeing a glowing object, or meeting someone unusual.  
  Use a variety of endings across outputs so the story does not always end the same way.

  Then, based on this story opening, return your answer in a JSON object with 4 fields:
  1. intro (Korean): Write the full intro in **Korean only** (around 300 characters). Use simple, child-friendly language. End with the main character stepping into or discovering something mysterious.
  2. question (Korean): Ask one narrative question in **Korean only**, using easy vocabulary suitable for children aged 7–9. The question must clearly continue from the intro and ask what the character sees, chooses, or interacts with next. Avoid repeated questions across outputs.
  3. options (Korean): Provide 3 possible answers in **Korean only**, each as one word concrete object or animal (e.g. "깃털", "다람쥐", "상자"). These should directly relate to the question. Avoid abstract ideas, verbs, or repeated items across outputs. Related to the problem situation at the end of the story.
  4. charLook (English): Describe the character’s outfit in one concise sentence in **English only**. Focus only on clothing and accessories (e.g. top, bottom, jewelry, shoes), with no mention of the character’s name or other traits. Include the color of the outfit. Match the style and tone to the story’s setting and mood (e.g. fantasy ocean world, magical forest, etc). Use evocative but clear language suitable for use in image generation prompts.

  Important: Respond with only the raw JSON object using these 4 fields. Do not include explanations, formatting symbols, or extra text.
  """
  
  print(storyPrompt)
  
  try:
    # 동화 도입부 생성 프롬프트
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      input=[      
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
        ],
      text_format=introOutput,
      temperature=0.8,
      top_p=0.7
    )

    # 현재 응답 id 저장
    responseId = response.id

    print(response.output_parsed)
    return response.output_parsed, responseId
  
  except Exception as e:
    raise e


# 동화 내용 생성 gpt 호출 - 중심부 생성 시 호출
def generateContent(choice, charName, responseId): # select: 질문 선택지, charName: 주인공 이름
  
  # 요청 프롬프트
  storyPrompt = f"""The user has selected "{choice}" as their answer to the previous question.
  Please continue the story in Korean, writing the next scene.
  This scene should naturally follow the previous events, and reflect the user’s choice within the flow of the narrative.
  It should also include the actions of the main character, {charName}, and their surrounding situation.

  Make sure the scene ends with the character experiencing or discovering something curious or unexpected.  
  This could be: entering a hidden place (e.g. cave, door, portal), noticing a strange sound, seeing a glowing object, or meeting someone unusual.  
  Use a variety of endings across outputs so the story does not always end the same way.

  Avoid flat or generic scenes such as “즐거운 시간을 보냈습니다.” or “즐거운 하루를 보냈습니다.” Include some form of tension, surprise, discovery, or a decision the character has to make.

  The question must not simply summarize or restate what happened in the story. Instead, it should help lead to a meaningful next event or choice.

  Then, based on this story opening:
  1. story : Write the story by continuing naturally from the previous events. (about 300 characters). Use simple, child-friendly language. End with the main character stepping into or discovering something mysterious.
  2. question (Korean): Ask one narrative question (randomly choose about where, who, what, or why) in **Korean only**, using easy vocabulary suitable for children aged 7–9. The question must clearly continue from the intro and ask what the character sees, chooses, or interacts with next. Avoid repeated questions across outputs.
  3. options (Korean): Provide 3 possible answers in **Korean only**, each as one word concrete object or animal (e.g. "깃털", "다람쥐", "상자"). These should directly relate to the question. Avoid abstract ideas, verbs, or repeated items across outputs. Related to the problem situation at the end of the story.

  Important: Respond using the fields and languages exactly as instructed. Do not include explanations, formatting symbols, or extra text. Respond in Korean only.
  """

  print(responseId)

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput,
      temperature=0.8,
      top_p=0.7
    )

    # 현재 응답 id 저장
    responseId = response.id

    print(response.output_parsed)
    return response.output_parsed, responseId
  
  except Exception as e:
    raise e


# 동화 내용 생성 gpt 호출 - 결말 생성을 위한 질문 생성 프롬프트트
def generateFinalQuestion(choice, charName, responseId): # select: 질문 선택지, charName: 주인공 이름
  
  # 요청 프롬프트
  storyPrompt = f"""The user has selected {choice} as their answer to the previous question.

  Please continue the story in Korean only, writing the next scene.

  This scene must:
  - Clearly reflect the user's selected choice within the narrative flow.
  - Focus on the main character {charName}'s actions and emotions.
  - Lead to a climax or problem situation — something unexpected, tense, or mysterious must happen (e.g. a magical trap, a sudden decision, a strange character appears, a path splits).
  - End with a problem that the character must solve, escape from, or react to.

  After the story, write a narrative question that:
  - Directly relates to the problem situation at the end.
  - Helps the reader make a meaningful choice that could solve or change the outcome.
  - Avoids summarizing what just happened.
  - Uses simple vocabulary appropriate for children aged 7–9.

  Then, provide 3 concrete answer options in Korean only, each as one word (e.g. "망치", "리본", "토끼") that:
  - Could reasonably help solve the problem or affect what happens next.
  - Related to the problem situation at the end of the story.
  - Are not abstract ideas or actions.
  - Are varied across outputs.

  Important: Respond using the fields and languages exactly as instructed. Do not include explanations, formatting symbols, or extra text. Respond in Korean only.
  """
  print(responseId)

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput,
      temperature=0.8,
      top_p=0.7
    )

    # 현재 응답 id 저장
    responseId_new = response.id

    print(response.output_parsed)
    return response.output_parsed, responseId_new
  
  except Exception as e:
    raise e

# 동화 결말부 프롬프트 요청
def generateEnding(choice, charName, responseId):

  # 요청 프롬프트
  storyPrompt = f"""The user has selected "{choice}" as their answer to the previous question.
  Please continue the story in Korean, writing the final scene. It's the end of the story.
  The ending should feel complete and meaningful. It must leave a gentle emotional impact or convey a simple, age-appropriate moral for children between 7 and 9 years old.
  Avoid rushed conclusions or vague endings. Show what the main character experiences or learns through the final event.
  Write the ending in Korean, about 300 characters. Do not include any extra explanations or formatting.
  It should also include the actions of the main character, {charName}, and their surrounding situation."""

  print(responseId)

  # 동화 결말 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": "You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition."},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=endingOutput,
      temperature=0.75,
      top_p=0.7
    )

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e



async def generateStory(story):

  user_content = [{"type": "input_text", "text": scene} for scene in story]

  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      input=[
        {"role": "developer", "content": "You are responsible for refining an array of separated fairytale scenes into a smoothly connected story. The input and output must remain in array format, and both the order and number of scenes must be preserved."+
        "Improve the flow and emotional continuity by adjusting expressions or adding transitional phrases within each scene. Keep the core meaning intact, but feel free to rephrase naturally."+
        "Each scene must be written in Korean and limited to 300 characters or fewer.  Do not include any extra explanations or formatting."},
        {"role": "user", "content": user_content}
      ],
      text_format=renderOutput,
      temperature=0.75,
      top_p=0.7
    )

    print(response.output_parsed)

    return response.output_parsed
  except Exception as e:
    raise e