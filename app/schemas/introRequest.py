from pydantic import BaseModel

class introRequest(BaseModel):
    charName: str
    genre: str
    place: str