FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV API_URL=http://backend:8000/summarize

COPY frontend-v2.py .

EXPOSE 8501

CMD [ "streamlit", "run", "frontend-v2.py", \
      "--server.address=0.0.0.0", "--server.port=8501" ]
