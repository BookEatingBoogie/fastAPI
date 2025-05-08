from pydantic import BaseModel

class imgPrompt(BaseModel):
    scene: str
    charImg: str

class imgUrl(BaseModel):
    imgUrl: str
