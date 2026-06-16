import os

import requests
import streamlit as st

# 같은 docker-compose 네트워크에서는 서비스명(back)으로 접근,
# 로컬에서 따로 실행할 때는 localhost:8000 사용
API_URL = os.environ.get("API_URL", "http://localhost:8000")

CATEGORY_NAMES = {
    "CP": "시티팝",
    "RB": "R&B",
    "DC": "댄스",
    "HH": "힙합",
    "AN": "애니메이션",
    "OST": "드라마·영화 OST",
    "RK": "락",
}

st.set_page_config(page_title="J-POP 취향 추천", page_icon="🎵")

st.title("🎵 J-POP 취향 추천 테스트")
st.write(
    "10가지 질문에 답하면, 당신에게 어울리는 J-POP 장르와 "
    "대표곡 2곡을 추천해 드려요!"
)

st.divider()


@st.cache_data(ttl=60)
def load_questions():
    res = requests.get(f"{API_URL}/questions", timeout=5)
    res.raise_for_status()
    return res.json()


# FastAPI에서 질문 목록 가져오기
try:
    questions = load_questions()
except Exception as e:
    st.error(f"FastAPI 서버에 연결할 수 없습니다. (API_URL={API_URL})\n\n{e}")
    st.stop()

# ----------------------------------------------------------
# 사용자 입력 받기
# ----------------------------------------------------------
answers = []

for i, q in enumerate(questions):
    st.subheader(f"Q{i + 1}. {q['question']}")

    options = q["options"]
    labels = [f"{o['key']}. {o['label']}" for o in options]
    keys = [o["key"] for o in options]

    selected_label = st.radio(
        label=f"질문 {i + 1} 선택지",
        options=labels,
        key=f"q_{i}",
        label_visibility="collapsed",
    )

    selected_key = keys[labels.index(selected_label)]
    answers.append(selected_key)

st.divider()

# ----------------------------------------------------------
# 추천 요청 -> FastAPI 호출 -> 결과 표시
# ----------------------------------------------------------
if st.button("🎧 추천 받기", type="primary", use_container_width=True):
    with st.spinner("당신의 취향을 분석하는 중..."):
        try:
            res = requests.post(
                f"{API_URL}/recommend",
                json={"answers": answers},
                timeout=5,
            )
            res.raise_for_status()
            result = res.json()
        except Exception as e:
            st.error(f"추천 요청 중 오류가 발생했습니다: {e}")
            st.stop()

    if not result.get("category"):
        st.error(result.get("description", "알 수 없는 오류가 발생했습니다."))
        st.stop()

    st.write(result["description"])
    st.success(f"당신의 J-POP 취향은 **{result['category_name']}** 입니다!")

    st.write("### 🎶 추천곡")
    for song in result["songs"]:
        st.markdown(f"- **{song['title']}** — {song['artist']}")

    with st.expander("카테고리별 점수 자세히 보기"):
        named_scores = {
            CATEGORY_NAMES.get(code, code): score
            for code, score in result["scores"].items()
        }
        st.json(named_scores)
