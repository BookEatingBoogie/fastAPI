import requests

API_KEY = "sk_5cda08065959ceec0d77987df2c82a3ed06b3f9a93cbadc9"  # 여기만 바꿔주세요

url = "https://api.elevenlabs.io/v1/voices"

headers = {
    "xi-api-key": API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    voices = response.json()["voices"]
    for voice in voices:
        print(f"📢 이름: {voice['name']}, 🔑 voice_id: {voice['voice_id']}")
else:
    print("❌ 오류 발생:")
    print(response.text)
