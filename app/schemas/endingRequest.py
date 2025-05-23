from pydantic import BaseModel

class endingRequest(BaseModel):
    requestId: str
    page: int
    storyId: str
    charName: str
    choice: str
    story: list[str]
    imgUrl: str