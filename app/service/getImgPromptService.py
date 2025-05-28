from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# 캐릭터 이미지 생성 프롬프트 요청
def createCharacter(charImg):
  
  response = client.responses.create(
    model="gpt-4.1-2025-04-14",
    input=[
      {"role":"developer", "content":"You are an assistant that generates image generation prompts from portrait photos. Analyze visible features—hairstyle, no facial expression—and describe them in a clear, natural English sentence starts with 'A young child with'. In a second sentence starts with 'Wearing', describe the outfit and inferred lower-body clothing  (pants or shoes). In a third sentence, describe the overall mood based on facial expression, posture, and lighting. Ensure the character is holding nothing in their hands. Keep the total response concise (200–300 characters), focused, and free from unnecessary adjectives or embellishments."},
      {"role":"user", "content": [{"type": "input_image", "image_url": charImg}]}
    ]
  )
  print(response.output_text)

  return response.output_text

def createBackgroundImage(scene):

  response = client.responses.create(
    model="gpt-4.1-2025-04-14",
    input=[
      {"role":"developer", "content":"You are an assistant that generates short, vivid scene descriptions in a soft anime or fairytale style. You will receive a short scene of story, written in Korean. Write in simple, clear English. Use easy, usable words. Limit the output to 100 characters (including commas and spaces). Use fragment-style phrases separated by commas. No full sentences. Describe only the background: environment, objects, lighting, textures, and atmosphere. Return only the prompt. No explanations or formatting."},
      {"role":"user", "content": scene}
    ]
  )

  return response.output_text

# 동화 삽화 생성 프롬프트 요청
def createStoryImage(scene):

  response = client.responses.create(
    model="gpt-4.1-2025-04-14",
    input=[
      {"role":"developer", "content":"You are an assistant that generates short, vivid scene descriptions in a soft anime or fairytale style."+
       "You will receive a short scene in Korean describing background or character behavior. Do not describe names, appearance, or clothing."+
       "Write in simple, clear English using 15 to 40 tokens only. Use fragment-style phrases separated by commas. No full sentences."+
       "Do not use “as,” “while,” or “when.”"+
       "Focus on posture, lighting, motion, atmosphere, nature, or magical objects."+
       "Use ((double parentheses)) to highlight key visual elements like magical items, glowing effects, or strong moods."+
       "Do not include any sound."+
       "If the focus is a character’s action, begin with person,"+
       "If the focus is the setting or mood, begin with background,"+
       "Respond only in English."},
      {"role":"user", "content": scene} # 캐릭터 외형 묘사 추가 고려.
    ]
  )
  print(response.output_text)

  return response.output_text