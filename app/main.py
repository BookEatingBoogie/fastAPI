from fastapi import FastAPI
from app.service.gpt_test import callGPT

app = FastAPI()

@app.get("/openai/gpt/")
def read_root():
    return {"Hello": callGPT()}

@app.get("/")
def start():
    return {"Hello":"World!"}