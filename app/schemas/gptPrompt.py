from pydantic import BaseModel
from typing import Optional

class gptPrompt(BaseModel):
    userContent: Optional[str] = "The child has come to create a main character! Welcome the child and ask the first question about the character's name to start the story creation."