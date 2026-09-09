FROM huggingface/transformers-torch-light

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

COPY backend.py .

CMD [ "uvicorn", "backend:app", "--host", "0.0.0.0", \
    "--port", "8000" ]
