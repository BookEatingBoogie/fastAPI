from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# 캐릭터 이미지 생성 프롬프트 요청
def createCharacter(charImg):
  
  response = client.responses.create(
    model="gpt-4o-2024-11-20",
    input=[
      {"role":"developer", "content":"You are an assistant that generates image generation prompts from portrait photos. Analyze visible features—hairstyle and facial expression—and describe them in a clear, natural English sentence starts with 'A young child with'. In a second sentence starts with 'Wearing', describe the outfit and inferred lower-body clothing  (pants or shoes). In a third sentence, describe the overall mood based on facial expression, posture, and lighting. Ensure the character is holding nothing in their hands. Keep the total response concise (200–300 characters), focused, and free from unnecessary adjectives or embellishments."},
      {"role":"user", "content": [{"type": "input_image", "image_url": charImg}]}
    ]
  )
  print(response.output_text)

  return response.output_text


# 동화 삽화 생성 프롬프트 요청
def createStoryImage(scene):

  response = client.responses.create(
    model="gpt-4o-2024-11-20",
    input=[
      {"role":"developer", "content":"You are an assistant that generates image generation prompts for fairytale-style illustrations based on a short scene and character description."+
       "Describe the character’s actions, facial expression, and posture. If appropriate, create and include an object they are holding. Include a magical or whimsical background with setting and atmosphere, inferring missing details when needed."+
       "Use clear, natural English. Do not describe the character’s clothing or outfit. Avoid using the character’s name. Keep the output concise (200–300 characters), focused, and free from unnecessary adjectives or embellishments."},
      {"role":"user", "content": scene} # 캐릭터 외형 묘사 추가 고려.
    ]
  )
  print(response.output_text)

  return response.output_text

