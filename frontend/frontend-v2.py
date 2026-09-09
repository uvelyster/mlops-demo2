import os
import sqlite3
from datetime import datetime

import requests
import streamlit as st


# ============================================================
# 설정
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000/summarize"
)

DB_PATH = os.getenv(
    "DB_PATH",
    "summaries.db"
)


# ============================================================
# DB 함수
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            model TEXT NOT NULL,
            max_length INTEGER NOT NULL,
            min_length INTEGER NOT NULL,
            summary TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def save_summary(
    url,
    model,
    max_length,
    min_length,
    summary
):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO summaries (
            url,
            model,
            max_length,
            min_length,
            summary,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            url,
            model,
            max_length,
            min_length,
            summary,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    summary_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return summary_id


def get_summaries(
    query="",
    model="전체",
    limit=100
):
    conn = get_connection()

    sql = """
        SELECT
            id,
            url,
            model,
            max_length,
            min_length,
            summary,
            created_at
        FROM summaries
        WHERE 1=1
    """

    params = []

    # 검색어
    if query:
        sql += """
            AND (
                url LIKE ?
                OR summary LIKE ?
                OR model LIKE ?
            )
        """

        search = f"%{query}%"

        params.extend([
            search,
            search,
            search
        ])

    # 모델 필터
    if model != "전체":
        sql += " AND model = ?"
        params.append(model)

    sql += """
        ORDER BY id DESC
        LIMIT ?
    """

    params.append(limit)

    rows = conn.execute(
        sql,
        params
    ).fetchall()

    conn.close()

    return rows


def delete_summary(summary_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM summaries WHERE id = ?",
        (summary_id,)
    )

    conn.commit()
    conn.close()


# ============================================================
# DB 초기화
# ============================================================

init_db()


# ============================================================
# Session State
# ============================================================

if "summary_result" not in st.session_state:
    st.session_state.summary_result = None

if "summary_url" not in st.session_state:
    st.session_state.summary_url = ""

if "summary_model" not in st.session_state:
    st.session_state.summary_model = ""

if "summary_max_length" not in st.session_state:
    st.session_state.summary_max_length = 150

if "summary_min_length" not in st.session_state:
    st.session_state.summary_min_length = 40


# ============================================================
# 페이지
# ============================================================

st.set_page_config(
    page_title="Hugging Face Summarizer",
    layout="wide"
)

page = st.sidebar.radio(
    "페이지",
    [
        "요약하기",
        "히스토리"
    ]
)


# ============================================================
# 요약하기 페이지
# ============================================================

if page == "요약하기":

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

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # 요약하기
    # --------------------------------------------------------

    with col1:

        if st.button(
            "요약하기",
            type="primary",
            use_container_width=True
        ):

            if not url:
                st.warning("URL을 입력하세요.")

            else:

                with st.spinner("요약 중입니다..."):

                    try:

                        response = requests.post(
                            API_URL,
                            json={
                                "url": url,
                                "model": model,
                                "max_length": max_length,
                                "min_length": min_length
                            },
                            timeout=120
                        )

                        if response.status_code == 200:

                            result = response.json()

                            st.session_state.summary_result = result["summary"]
                            st.session_state.summary_url = url
                            st.session_state.summary_model = result.get(
                                "model",
                                model
                            )
                            st.session_state.summary_max_length = max_length
                            st.session_state.summary_min_length = min_length

                            st.success("요약 완료")

                        else:

                            st.error(
                                f"API 오류: {response.status_code}\n\n"
                                f"{response.text}"
                            )

                    except requests.RequestException as e:

                        st.error(
                            f"API 요청 중 오류가 발생했습니다.\n\n{e}"
                        )


    # --------------------------------------------------------
    # DB 저장
    # --------------------------------------------------------

    with col2:

        if st.button(
            "현재 요약 DB 저장",
            use_container_width=True
        ):

            if not st.session_state.summary_result:

                st.warning(
                    "먼저 요약을 실행하세요."
                )

            else:

                summary_id = save_summary(
                    url=st.session_state.summary_url,
                    model=st.session_state.summary_model,
                    max_length=st.session_state.summary_max_length,
                    min_length=st.session_state.summary_min_length,
                    summary=st.session_state.summary_result
                )

                st.success(
                    f"DB에 저장되었습니다. ID: {summary_id}"
                )


    # --------------------------------------------------------
    # 요약 결과
    # --------------------------------------------------------

    if st.session_state.summary_result:

        st.markdown("---")

        st.markdown("### 선택한 모델")

        st.write(
            st.session_state.summary_model
        )

        st.markdown("### 기사 URL")

        st.write(
            st.session_state.summary_url
        )

        st.markdown("### 요약 결과")

        st.write(
            st.session_state.summary_result
        )


# ============================================================
# 히스토리 페이지
# ============================================================

elif page == "히스토리":

    st.title("요약 히스토리")

    st.caption(
        "DB에 저장된 요약 결과를 검색하고 확인할 수 있습니다."
    )

    # --------------------------------------------------------
    # 검색 영역
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        [2, 1, 1]
    )

    with col1:

        query = st.text_input(
            "검색",
            placeholder="URL, 모델명, 요약 내용 검색..."
        )

    with col2:

        history_model = st.selectbox(
            "모델",
            [
                "전체",
                "facebook/bart-large-cnn",
                "google-t5/t5-small"
            ]
        )

    with col3:

        limit = st.number_input(
            "조회 개수",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )

    # --------------------------------------------------------
    # 검색 버튼
    # --------------------------------------------------------

    if st.button(
        "검색 / 조회",
        type="primary"
    ):

        st.session_state.history_query = query
        st.session_state.history_model = history_model

    # session state 기본값
    if "history_query" not in st.session_state:
        st.session_state.history_query = ""

    if "history_model" not in st.session_state:
        st.session_state.history_model = "전체"

    # --------------------------------------------------------
    # DB 조회
    # --------------------------------------------------------

    rows = get_summaries(
        query=st.session_state.history_query,
        model=st.session_state.history_model,
        limit=limit
    )

    st.markdown("---")

    st.write(
        f"검색 결과: **{len(rows)}건**"
    )

    # --------------------------------------------------------
    # 결과 출력
    # --------------------------------------------------------

    if not rows:

        st.info(
            "저장된 요약 결과가 없습니다."
        )

    else:

        for row in rows:

            with st.expander(
                f"[{row['id']}] "
                f"{row['created_at']} - "
                f"{row['model']}"
            ):

                st.markdown("**기사 URL**")

                st.write(
                    row["url"]
                )

                st.markdown("**모델**")

                st.write(
                    row["model"]
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"최대 길이: {row['max_length']}"
                    )

                with col2:
                    st.write(
                        f"최소 길이: {row['min_length']}"
                    )

                st.markdown("**요약 내용**")

                st.write(
                    row["summary"]
                )

                st.markdown(
                    f"저장 시간: {row['created_at']}"
                )

                # 삭제
                if st.button(
                    "삭제",
                    key=f"delete_{row['id']}"
                ):

                    delete_summary(
                        row["id"]
                    )

                    st.success(
                        "삭제되었습니다."
                    )

                    st.rerun()

