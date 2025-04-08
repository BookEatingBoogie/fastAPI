import requests

API_KEY = "sk_5cda08065959ceec0d77987df2c82a3ed06b3f9a93cbadc9"
VOICE_ID = "Mmepzv6cBqMI22R2YaXy" 
TEXT = "안녕 서영아 만나서 반가워! 나랑 같이 만들어보자"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": API_KEY
}

data = {
    "text": TEXT,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)

# 결과 저장
with open("output.mp3", "wb") as f:
    f.write(response.content)
