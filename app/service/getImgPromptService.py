from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# 캐릭터 이미지 생성 프롬프트 요청
def createCharacter(charImg):
  
  response = client.responses.create(
    model="gpt-4o-2024-11-20",
    input=[
      {"role":"developer", "content":"You are an assistant that generates image generation prompts from portrait photos. Analyze visible features—hairstyle, no facial expression—and describe them in a clear, natural English sentence starts with 'A young child with'. In a second sentence starts with 'Wearing', describe the outfit and inferred lower-body clothing  (pants or shoes). In a third sentence, describe the overall mood based on facial expression, posture, and lighting. Ensure the character is holding nothing in their hands. Keep the total response concise (200–300 characters), focused, and free from unnecessary adjectives or embellishments."},
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
      {"role":"developer", "content":"You are an assistant that generates image generation prompts for fairytale-style illustrations. Based on a short scene describing the character’s behavior, generate a concise sequence of descriptive phrases."+
       "Do not write full sentences. Do not begin with phrases like “Illustrate a figure” or include any subject like “she” or “a person.” Instead, start directly with action, expression, posture, and magical or whimsical background elements."+
       "Do not include any description of appearance, clothing, or name. Keep the output between 200 and 300 characters. Use clear and natural English. Focusing on vivid, fragment-style visual descriptions."},
      {"role":"user", "content": scene} # 캐릭터 외형 묘사 추가 고려.
    ]
  )
  print(response.output_text)

  return response.output_text

