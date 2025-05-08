from pydantic import BaseModel

class contentOutput(BaseModel):
    story: str
    question: str
    options: list[str]