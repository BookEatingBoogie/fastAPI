from pydantic import BaseModel

class endingRequest(BaseModel):
    storyId: str
    charName: str
    choice: str
    story: list[str]
