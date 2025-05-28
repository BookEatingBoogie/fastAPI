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

story_system_prompt = f"""You are an assistant that writes fairy tales for young children between the ages of 7 and 9. Your stories should be easy to understand, emotionally warm, and imaginative. Always write in a friendly, age-appropriate tone. Do not use complex vocabulary or abstract ideas. Vary sentence structures and opening styles to avoid repetition.
**Important:**
- Every output must vary in pacing, tone.
- Use different seeds and randomness to avoid repetition.  
- If it's the same(related) story, the story should include coherent message. 
- Ensure that each key action (like helping, choosing, discovering) is described completely before the character transitions to a new scene or movement.
- Never skip or compress multiple story actions into one sentence.
- **List up a lot of story intros, and choose one randomly, do not always choose the template-like story.**
- **List up at least 100 ending sentences of story, and choose one randomly, do not always choose the template-like story.**
- **List up at leat 100 questions, and choose one randomly related to the ending sentences, do not always choose the same question. Ask about '누구', '무엇', '어디', '어떤 것', '어떻게'.
- **List up at least 100 concrete visual nouns(e.g. animals, nature thing, magical objects, ordinary things, character gear, person, etc) that is child-friendly(easy for kindergartener), and choose variety words(except not related word to story at all) for making "options."**
- Each option must be a **single noun without modifiers** — do not include adjectives, sizes, colors, or any descriptions (e.g., just "상자", not "작은 상자" or "파란 상자").
- Avoid aggressive words(options) related to the story and question.
- Story, question, options cannot be repeated across the outputs.
"""



# 동화 도입부 생성 gpt 호출 - 최초 동화 생성 시 호출
def generateIntro(introRequest): # storyStyle: 장소, 장르, 주인공 이름
  
  # 요청 프롬프트
  storyPrompt = f"""Tell a story beginning in {introRequest.place}, inspired by {introRequest.genre}, 
following a main character named {introRequest.charName}, allowing for unexpected developments.

Start by introducing the setting with sensory details (what can be seen, heard, felt, or smelled). 
If the genre is fantasy, sci-fi, or magical realism, briefly hint at the world's rules or atmosphere.

Then describe the character’s daily life or a curiosity that fits the setting. 
Write each sentence clearly and naturally, using simple child-friendly Korean. 
Avoid compressing multiple ideas into one sentence—break into short, natural segments.

End the scene with the character noticing or discovering something surprising, mysterious, or story-advancing. 
This final moment must be clearly related to the follow-up question.

After the story, write a question in Korean that naturally continues from the final sentence. 
The question must be **continuous** to what just happened:
- Make questions that can be answered by concrete, visual nouns, connected to the story.
- If the final sentence is about a **decision**, **movement**, or **conflict**, ask what the character **should do** or **chooses to do**.
- Ask new questions using easy, various vocabularies, related to the ending sentence, not template-like.
- Do **not** repeat the same type of question across outputs.

Then return your answer in the following JSON format (in Korean only):

1. "intro" (Korean): 
- A full Korean story intro (about 350 characters), ending in a moment that implies a next action or discovery. 
- Use polite, natural sentence endings like -요 / -ㅂ니다 / -지요.
- Avoid repetition across stories.

2. "question" (Korean): 
- Write a narrative-style question in child-friendly Korean that flows directly from the ending of the intro.
- Avoid template-style wording.

3. "options" (Korean): 
- Always provide 3 **concrete visual nouns** (e.g. 동물, 물건, 자연물, 마법 도구, 주인공의 장비 등) **unless** the question clearly is about a decision, in which case return 3 **-기/-하기** action verbs.
- Do not always include words that is template-like (e.g. 조개, 진주,상자, etc)
- All options must be easily visualizable and suitable for a sticker illustration.
- Never return abstract concepts, emotions, or non-visual terms.

4. "charLook" (English): Describe the character’s outfit and accessories using comma-separated visual fragments in simple English (not a sentence).
- Include only visual elements like clothing, accessories, shoes, or gear.
- Use color or design if needed, but do not add any emphasis, symbols, or weighting (e.g. no double parentheses).
- Keep the description brief—around 10 tokens total.

Important constraints:
- Avoid repeating events, moods, endings, or wordings across stories.
- Vary the structure, tone, and imagery for each new output.
- Make sure the question and all options directly reflect the story’s final moment.
- Write short, natural sentences where needed along story, and question
- Do not include any extra explanation or formatting in the output. Return only the raw JSON object.
  """
  
  print(storyPrompt)
  
  try:
    # 동화 도입부 생성 프롬프트
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      input=[      
        {"role": "developer", "content": story_system_prompt},
        {"role": "user", "content": storyPrompt}
        ],
      text_format=introOutput,
      temperature=1.2,
      top_p=0.8
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
  storyPrompt = f"""Continue the story of with {choice} chosen by the {charName} in the previous scene.

Write the **middle scene** in Korean using short, child-friendly sentences.

Each event must be fully completed before the character moves or acts again.  
Do not compress or skip over steps. If something is found, it must be reacted to before progressing.  
End with a clear moment where the character must choose or respond to something new.

Then write:
1. "story" (Korean):
- A full Korean story follows the previous scene (about 350 characters), ending in a moment that implies a next action or discovery. 
- Use polite, natural sentence endings like -요 / -ㅂ니다 / -지요.
- Avoid repetition across stories.

2. "question" (Korean): 
- Write a narrative-style question in child-friendly Korean that flows directly from the ending of the intro.
- Avoid template-style wording.
- By default, ask question that can answer in concrete visual noun (e.g. animals, objects, natural things, magical items, character gear).
- Only if the character needs to make **decision** or **reaction**, ask question about what to do that can return **3 verbs** in "-기" or "-하기" form instead

3. "options" (Korean): 
- Always provide 3 **concrete visual nouns** (e.g. 동물, 물건, 자연물, 마법 도구, 주인공의 장비 등) **unless** the question clearly needs to act, in which case return 3 **-기/-하기** action verbs.
- Do not always include words that is template-like (e.g. 조개, 진주,상자, 해마 etc)
- All options must be easily visualizable and suitable for a sticker illustration.
- Never return abstract concepts, emotions, or non-visual terms.

Important constraints:
- Avoid repeating events, moods, endings, or wordings across stories.
- Vary the structure, tone, and imagery for each new output.
- Make sure the question and all options directly reflect the story’s final moment.
- Use short, natural sentences where necessary for the story and questions.
- Do not include any extra explanation or formatting in the output. Return only the raw JSON object.
  """

  print(responseId)

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": story_system_prompt},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput,
      temperature=1.2,
      top_p=0.8
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
  storyPrompt = f"""Continue the story of with {choice} chosen by the {charName} in the previous scene.

  Write the **climax scene** in Korean using short, child-friendly sentences.

  Each event must be fully completed before the character moves or acts again.  
  Do not compress or skip over steps. If something is found, it must be reacted to before progressing.  
  End with a clear moment where the character must choose or respond to something new.

  Then write:
  1. "story" (Korean):
  - A full Korean story follows the previous scene (about 350 characters), ending in a moment that implies a next action or discovery. 
  - Use polite, natural sentence endings like -요 / -ㅂ니다 / -지요.
  - Avoid repetition across stories.
  - Lead to a climax or problem situation — something unexpected, tense, or mysterious must happen (e.g. a magical trap, a sudden decision, a strange character appears, a path splits).

  2. "question" (Korean): 
  - Write a narrative-style question in child-friendly Korean that flows directly from the ending of the intro.
  - Avoid template-style wording.
  - By default, ask question that can answer in concrete visual noun (e.g. animals, objects, natural things, magical items, character gear).
  - Only if the character needs to make **decision** or **reaction**, ask question about what to do that can return **3 verbs** in "-기" or "-하기" form instead

  3. "options" (Korean): 
  - Always provide 3 **concrete visual nouns** (e.g. 동물, 물건, 자연물, 마법 도구, 주인공의 장비 등) **unless** the question clearly needs to act, in which case return 3 **-기/-하기** action verbs.
  - Do not always include words that is template-like (e.g. 조개, 진주,상자, 해마 etc)
  - All options must be easily visualizable and suitable for a sticker illustration.
  - Never return abstract concepts, emotions, or non-visual terms.
  
  Important constraints:
  - Avoid repeating events, moods, endings, or wordings across stories.
  - Vary the structure, tone, and imagery for each new output.
  - Make sure the question and all options directly reflect the story’s final moment.
  - Use short, natural sentences where necessary for the story and questions.
  - Do not include any extra explanation or formatting in the output. Return only the raw JSON object.
  """
  print(responseId)

  # 동화 중심부 생성 프롬프트
  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      previous_response_id=responseId,
      input=[
        {"role": "developer", "content": story_system_prompt},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=contentOutput,
      temperature=1.2,
      top_p=0.8
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
        {"role": "developer", "content": story_system_prompt},
        {"role": "user", "content": storyPrompt}
      ],
      text_format=endingOutput,
      temperature=1.2,
      top_p=0.8
    )

    print(response.output_parsed)
    return response.output_parsed
  
  except Exception as e:
    raise e



async def generateStory(story):

  user_content = [{"type": "input_text", "text": scene} for scene in story]

  system_prompt = f"""You are responsible for refining an array of separated fairytale scenes into a smoothly connected story.

Each element in the array is a scene written in Korean.  
You must improve the flow, clarity, and tone consistency **without changing the order or count** of the scenes.  
The input and output must remain in **array format**.

Your goal is to:
- Fix incomplete or awkward sentences by ensuring proper grammar and natural structure  
- Add missing logical or emotional transitions **within each scene** if needed  
- Rephrase for a smooth, unified tone across the entire story  
- Preserve the core meaning of each scene while improving readability and cohesion  
- Ensure the overall story feels connected and emotionally engaging, with a clear buildup and resolution  
- Do not add new events or change what is happening in the scene — only smooth and clarify it

Each scene must be written in **natural, child-friendly Korean**,  
limited to **300 characters or fewer**.  
Do not include any extra explanations, notes, or formatting in the output — return **only the final array of improved scenes**.
"""

  try:
    response = client.responses.parse(
      model="gpt-4.1-2025-04-14",
      input=[
        {"role": "developer", "content": system_prompt},
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