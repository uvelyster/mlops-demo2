import os
import streamlit as st
import requests

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000/summarize"
)

st.set_page_config(
    page_title="Hugging Face Summarizer"
)

st.title("Hugging Face 모델 기반 텍스트 요약")

url = st.text_input(
    "기사 URL",
    placeholder="https://..."
)

model = st.selectbox(
    "모델 선택",
    [
        "facebook/bart-large-cnn",
        "google-t5/t5-small",
        "/models/t5-small"
    ]
)

max_length = st.slider(
    "최대 길이",
    50,
    300,
    150
)

min_length = st.slider(
    "최소 길이",
    20,
    100,
    40
)

if st.button("요약하기"):
    if not url:
        st.warning("URL을 입력하세요.")
    else:
        with st.spinner("요약 중입니다..."):
            response = requests.post(
                API_URL,
                json={
                    "url": url,
                    "model": model,
                    "max_length": max_length,
                    "min_length": min_length
                }
            )
            if response.status_code == 200:
                result = response.json()
                st.success("요약 완료")
                st.markdown("### 선택한 모델")
                st.write(result["model"])
                st.markdown("### 요약 결과")
                st.write(result["summary"])
            else:
                st.error(response.text)
