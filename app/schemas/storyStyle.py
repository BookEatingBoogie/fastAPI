from pydantic import BaseModel

class storyStyle(BaseModel):
    genre: str
    location: str
    mood: str
    helper: str
    villain: str