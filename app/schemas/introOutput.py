from pydantic import BaseModel

class introOutput(BaseModel):
    intro: str
    question: str
    options: list[str]
    charLook: str