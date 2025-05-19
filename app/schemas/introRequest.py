from pydantic import BaseModel

class introRequest(BaseModel):
    charName: str
    charLook: str
    genre: str
    place: str
    imgUrl: str