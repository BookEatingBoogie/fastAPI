from pydantic import BaseModel

class renderOutput(BaseModel):
    paragraphs: list[str]


