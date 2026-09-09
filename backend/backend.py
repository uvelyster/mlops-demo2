from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
from transformers import pipeline
import requests

app = FastAPI()

class SummarizeRequest(BaseModel):

    url: str
    model: str
    max_length: int = 150
    min_length: int = 40

# 모델 캐시
MODEL_CACHE = {}


def get_model(model_name):
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = pipeline(
            task="summarization",
            model=model_name,
            tokenizer=model_name,
            framework="pt"
        )
    return MODEL_CACHE[model_name]

def extract_url(url):
    headers = {
        "User-Agent":"Mozilla/5.0"
    }
    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )
    paragraphs = [
        p.get_text(" ", strip=True)
        for p in soup.find_all("p")
    ]
    return "\n".join(paragraphs)

@app.post("/summarize")

def summarize(req: SummarizeRequest):
    try:
        text = extract_url(req.url)
        if len(text) == 0:
            raise HTTPException(
                status_code=400,
                detail="본문을 추출할 수 없습니다."
            )
        summarizer = get_model(req.model)
        result = summarizer(
            text,
            max_length=req.max_length,
            min_length=req.min_length,
            truncation=True
        )
        return {
            "model": req.model,
            "summary": result[0]["summary_text"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
