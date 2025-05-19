from pydantic import BaseModel

class contentRequest(BaseModel):
    charName: str
    choice: str
    page: int
    imgUrl: str