from pydantic import BaseModel

class StickerRequest(BaseModel):
    prompt: str
