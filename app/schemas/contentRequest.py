from pydantic import BaseModel

class contentRequest(BaseModel):
    requestId: str
    charName: str
    choice: str
    page: int
    imgUrl: str