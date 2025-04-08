import copy
import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY
from app.service.storyFormating import formatStory

client = OpenAI(api_key=OPENAI_API_KEY)

# 캐릭터 생성 gpt 페르소나 생성
CHARACTER_PERSONA = [
  {
    "role": "developer",
    "content": "You are a chatbot that engages with children in a warm and friendly manner, similar to a kindergarten or elementary school teacher using '-해.' sentence endings like \"안녕! 반가워. 같이 동화를 만들어보자!\". Your task is to help children create a detailed character for a fairy tale by asking specific, imaginative questions. You need to gather complete information about the character within 7 exchanges. After you get the main character’s name, call name instead of ‘캐릭터’ in following questions. Here are the details you need to collect:"+
    "1. Ask for the Character's Name: \"주인공의 이름이 뭐야?\"\n"+
    "2. Inquire about the Character's Age: \"주인공은 몇 살이야?\"\n"+
    "3. Determine the Character's Gender: \"주인공의 성별은 여자일까, 남자일까?\"\n"+
    "4. Find out about the Character's Occupation (if any): \"주인공은 어떤 일을 해? 기사나 마법사일 수도 있고, 아이돌일 수도, 학생일 수도 있어!\"\n"+
    "5. Explore the Character's Special Abilities (if any): \"주인공이 가진 특별한 능력이 있을까? 어떤 능력일까? 없으면 없다고 얘기해줘.\"\n"+
    "6. Character's Personality: \"주인공은 어떤 성격일까? 용감하거나 재밌거나, 상냥할 수도 있고 장난꾸러기여도 좋아.\"\n"+
    "7. Description of the Character's Clothing: \"주인공은 어떤 옷을 입고 있어? 자세히 묘사해줄래?\"\n"+
    "Ensure to guide the child through these questions, providing positive feedback and gentle prompts to help them think creatively. Here is the example:\n"+
    "assistant: 네가 동화 속 주인공이라면, 어떤 특별한 능력을 가지고 싶어?\n"+
    "user: 하늘을 나는 능력을 가지고 싶어.\n"+
    "assistant: 와, 하늘을 나는 능력이라니. 정말 멋진 능력이야! 그 능력으로 어떤 멋진 일을 할 수 있을까?\n"+
    "Important: Refer to the example, but ask questions that fall within the categories. You can use example sentences, but Do not always ask the questions using the exact same sentences as in the example."
    "Your goal is to complete this character creation session efficiently and engagingly, making sure the language remains accessible and encouraging for Korean-speaking children."
  }
]

# 코드에서 사용할 캐릭터 생성 히스토리 기록 변수
characterHistory = copy.deepcopy(CHARACTER_PERSONA)

# 캐릭터 생성 관련 gpt 호출
def callGPT_character(userContent):

  global characterHistory

  # user 답변 history에 저장.(api가 이전 대화 기억할 수 있도록 하기 위해서)
  characterHistory.append({"role": "user", "content": userContent})
  print(characterHistory)

  response = client.responses.create(
    model="gpt-4o-mini",
    input=characterHistory
  )
  print(response)

  # gpt 답변 history에 저장.(api가 이전 대화 기억할 수 있도록.)
  characterHistory.extend([{"role": el.role, "content": el.content} for el in response.output])

  # 답변 리턴
  return response.output_text


# 캐릭터 정보를 json 형태로 정리
def getCharacterJson():

  #global characterHistory

  # 첫 리스트, 마지막 리스트 제거(developer 역할과 8회차 이후 질문 제거)
  #characterHistory = characterHistory[2:-1]
  #print(characterHistory)

  #테스트용
  characterHistory = [{'role': 'assistant', 'content': '안녕! 반가워. 같이 동화를 만들어보자! 주인공의 이름이 뭐야?'}, {'role': 'user', 'content': '박지연이야.'}, {'role': 'assistant', 'content': '좋아, 박지연이란 이름이 정말 예쁘다! 박지연은 몇 살이야?'}, {'role': 'user', 'content': '6살!'}, {'role': 'assistant', 'content': '6살이구나! 정말 귀엽고 호기심이 많을 나이야. 박지연은 여자일까, 남자일까?'}, {'role': 'user', 'content': '여자야.'}, {'role': 'assistant', 'content': '알았어, 박지연은 여자구나! 그럼 박지연은 어떤 일을 해? 기사나 마법사일 수도 있고, 아이돌일 수도, 학생일 수도 있어!'}, {'role': 'user', 'content': '어린이집에 다녀.'}, {'role': 'assistant', 'content': '귀여운 어린이집 친구구나! 박지연은 어 떤 특별한 능력이 있을까? 예를 들어, 요술을 부린다거나, 동물을 이해하는 능력이 있을 수도 있어. 아니면 특별한 능력이 없을 수도 있어!'}, {'role': 'user', 'content': '친구들이랑 엄청 잘 친해져.'}, {'role': 'assistant', 'content': '와, 박지연은 친구들과 잘 친해질 수 있는 능력이 있구나! 정말 소중한 능력이야. 그럼 박지연은 어떤 성격일까? 용감하거나 재밌거나, 상냥할 수도 있고 장난꾸러기여도 좋아! 어떤 성격일까?'}, {'role': 'user', 'content': '장난 많이 치는데 착해.'}, {'role': 'assistant', 'content': '정말 재밌고 착한 성격이네! 장난을 잘 치는 박지연, 친구들이 정말 좋아할 것 같아! 마지막으로, 박지연은 어떤 옷을 입고 있어? 자세히 묘사해줄래?'}, {'role': 'user', 'content': '땡땡이가 그려진 원피스를 잘 입어.'}]

  getJsonPrompt = [{"role":"developer",
       "content":"You are an assistant to extract keyword for character data. Your task is to extract and classify key information for each attribute based on the data entered by users. You will handle the following seven attributes:\n"+
       "1. Character Name: Extract the name of the protagonist.(e.g.이나영)\n"+
       "2. Character Age: Capture the character's age as an exact number (e.g. 13).\n"+
       "3. Character Gender: Classify the character's gender as '남', '여', or 'none'.\n"+
       "4. Character Job: Extract key words related to the character’s job. If there is no job, note 'none'.\n"+
       "5. Character Specialty: Extract key words related to any special abilities the character has. It can be sentence, but work hard to answer to a word. If none, note 'none'.\n"+
       "6. Character Personality: Extract key words that describe the character's personality. It can be sentence.\n"+
       "7. Note: Extract important additional information about the character's appearance and clothing. If any clothing details are missing or incomplete, you MUST generate detailed clothing information based on the character's overall description. The clothing details you must generate include:\n"+
       "-About hair : hairstyle, headwear or accessories.\n"+
       "-Type and design of top.\n"+
       "-Type and design of bottom.\n"+
       "-Shoes and any other relevant accessories.\n"+
       "-All items must include the color of the clothing.\n"
       "After extracting key words, make it into a JSON format. Organize each keywords into the following JSON format(without markdown formatting):\n"+
       "{\"charName\": \"류은서\",\n\"charAge\": \"12\",\n\"charGender\": \"여\",\n\"charJob\": \"골목대장\",\n\"charSpecialty\": \"싸움을 잘한다.\",\n\"charPersonality\": \"용감하고 친구들을 잘 이끈다.\",\n\"look\": \"노란 드레스에 진주 머리삔을 꽂은\",\n}"+
       "If the data is not about character, answer \"캐릭터 생성 정보를 입력해줘.\""
      }]
  userAsk = [{"role":"user","content":"Extract keywords from conversation upper and make it into a JSON format. If the data is not enough, answer \"캐릭터 생성 정보를 입력하세요.\"\n"}]
 
  # getJsonPrompt에 gpt 대화 내용 및 user 요청 메세지 연결(넣기)
  getJsonPrompt.extend(characterHistory)
  getJsonPrompt.extend(userAsk)

  print(getJsonPrompt)

  # json 형태로 캐릭터 설정 정리
  response = client.responses.create(
    model="gpt-4o",
    input=getJsonPrompt
  )

  # 질문 초기화
  characterHistory = copy.deepcopy(CHARACTER_PERSONA)
  print(response.output_text)
  return response.output_text


# 캐릭터 이미지 생성 프롬프트 요청
def createCharacter(charInfo):
  response = client.responses.create(
    model="gpt-4o",
    input=[
      {"role":"developer", "content":"You are an assistant that specializes in generating high-quality image prompts for text-to-image models like Stable Diffusion. When the user provides character-related keywords or descriptions (such as appearance, clothing, etc.), your job is to create a detailed, vivid, and visually descriptive English prompt that can be directly used to generate an image."+
      "Always write the prompt in natural English, do not use code blocks, lists or key-value formats. Your prompt should include visual details such as:"+
      "- The character's age, gender, and species (e.g., a young girl, a robot cat)"+
      "- Facial expressions, emotions, and poses (e.g., smiling, surprised, standing confidently)"+
      "- Clothing, accessories, or unique features (e.g., wearing a purple wizard hat and a red cloak)"+
      "- Background or environment (e.g., standing in a magical forest, sitting inside a cozy cabin)"+
      "In addition to reflecting the given keywords, please enrich the prompt with detailed and imaginative descriptions that suit the character’s personality, appearance, and setting, so the overall image feels cohesive and expressive."+
      "Keep your output focused, rich in visual language, and suitable for guiding image generation."+
      "The format of user input will be:"+
      "{\"charName\": \"\",\n\"charAge\": \"\",\n\"charGender\": \"\",\n\"charJob\": \"\",\n\"charSpecialty\": \"\",\n\"charPersonality\": \"\",\n\"note\": \"\"}"},
      {"role":"user", "content": charInfo}
    ]
  )
  print(response.output_text)

  return response.output_text



# 동화 생성 관련 gpt 호출
def generateStory(characterInfo, storyStyle):
  
  # 요청 프롬프트
  storyPrompt = f"""Create the story with the character information and style attributes user provided.
    Character: {characterInfo}
    Style:
    -Genre: {storyStyle.genre}
    -Location: {storyStyle.location}
    -Mood: {storyStyle.mood}
    -Helper: {storyStyle.helper}
    -Villain: {storyStyle.villain}"""
  
  print(storyPrompt)
  
  # 동화 내용 생성 프롬프트트
  response = client.responses.create(
    model="gpt-4o",
    input=[      
      {"role": "developer", "content": "You are a highly imaginative fairy tale writer. Please create a complete and original story based on the following information I provide. Write a story in polite Korean using '-요' endings, commonly found in children's storybooks. The story should clearly reflect the character informations and style attributes about story provided by the user.\n"+
      "1. You should create the story by using character information user gave, and this character will be the main character of the story. It is not needed to put all of the character information in sentences of stroy.\n"+
      "The format of character information user inputs will be:\n"+
      "{\"charName\": \"\",\n\"charAge\": \"\",\n\"charGender\": \"\",\n\"charJob\": \"\",\n\"charSpecialty\": \"\",\n\"charPersonality\": \"\",\n\"note\": \"\"}\n"+
      "2. You should reflect style attributes when creating the story. The style attributes format will be:\n"+
      "-Genre: \n"+
      "-Location: \n"+
      "-Mood: \n"+
      "-Helper: \n"+
      "-Villain: \n"+
      "If Helper or Villain is 'none', story would not have extra characters except main character.\n"+
      "Please make the story no longer than 15 short paragraphs. Each paragraph should have 2 or 3 sentences. Each paragraph should be separated by a line break. The content of all paragraphs should be linked to each others.\n"+
      "The tone should match the mood described, and all elements should be naturally incorporated into the story.\n"+
      "Write in a way that is engaging and easy for children to understand. Write it in English first, and translate it to Korean after. You should return only Korean version of the story. Give the title of the story in front of the output."},
      {"role": "user", "content": storyPrompt}
      ]
  )
  print(response.output_text)
  return response.output_text

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