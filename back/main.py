from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="J-POP 취향 추천 API")


# ----------------------------------------------------------
# 1. 카테고리 정의
# ----------------------------------------------------------
CATEGORIES = ["CP", "RB", "DC", "HH", "AN", "OST", "RK"]

CATEGORY_NAMES = {
    "CP": "시티팝",
    "RB": "R&B",
    "DC": "댄스",
    "HH": "힙합",
    "AN": "애니메이션",
    "OST": "드라마·영화 OST",
    "RK": "락",
}

CATEGORY_DESCRIPTIONS = {
    "CP": "도시의 밤과 노스탤지어가 떠오르는, 여유롭고 그루비한 사운드를 좋아하시는군요... ",
    "RB": "부드럽고 소울풀한 보컬, 감성적인 무드를 즐기시는군요...",
    "DC": "신나는 비트와 화려한 퍼포먼스에 끌리시는군요...",
    "HH": "자유롭고 솔직한 리듬, 톡톡 튀는 플로우를 좋아하시는군요...",
    "AN": "두근거리는 청춘과 감성 스토리를 사랑하시는군요...",
    "OST": "영화 같은 순간, 드라마틱한 스토리텔링을 즐기시는군요...",
    "RK": "강렬한 라이브 사운드와 에너지를 좋아하시는군요...",
}

# 동점 방지를 위한 카테고리별 보정값
#  0.001~0.007의 작은 값은 실제 차이가 있을 때 순위에 영향을 주지 x
#  동점일 때만 보정값으로 순위를 결정함 -> 동점이 절대 발생 x
EPSILON = {
    "CP": 0.001,
    "RB": 0.002,
    "DC": 0.003,
    "HH": 0.004,
    "AN": 0.005,
    "OST": 0.006,
    "RK": 0.007,
}

# ----------------------------------------------------------
# 2. 추천곡 데이터 (카테고리당 2곡)
# ----------------------------------------------------------
SONGS: Dict[str, List[Dict[str, str]]] = {
    "CP": [
        {"title": "Plastic Love", "artist": "타케우치 마리야 (竹内まりや)", "description": "1984년 발표된 시티팝의 상징. 유튜브 알고리즘으로 전 세계에 재조명된 전설의 곡."},
        {"title": "Fantasy", "artist": "나카하라 메이코 (中原めいこ)", "description": "몽환적인 신스팝 사운드로 도시의 밤을 달리는 듯한 그루비한 감성."},
    ],
    "RB": [
        {"title": "Boyfriend", "artist": "크리스탈 케이 (Crystal Kay)", "description": "소울풀한 보컬과 부드러운 그루브가 돋보이는 크리스탈 케이의 대표곡."},
        {"title": "Garden", "artist": "후지이 카제 (藤井 風)", "description": "피아노와 소울풀한 보컬이 어우러진 감성 R&B."},
    ],
    "DC": [
        {"title": "Make Up Day", "artist": "나니와단시 (なにわ男子)", "description": "밝고 경쾌한 아이돌 댄스팝. 화려한 군무와 함께하면 더욱 신나는 곡."},
        {"title": "Drive in My Tokyo", "artist": "ICEx", "description": "도쿄 감성의 세련된 댄스 트랙. ICEx 특유의 퍼포먼스가 돋보임."},
    ],
    "HH": [
        {"title": "Bling-Bang-Bang-Born", "artist": "Creepy Nuts", "description": "애니메이션 '마시로의 창조' OP. 강렬한 비트와 중독성 있는 훅으로 전 세계 챌린지 열풍."},
        {"title": "Uchida 1", "artist": "GINTA & ODAKEi", "description": "독특한 플로우와 비트가 특징인 일본 언더그라운드 힙합."},
    ],
    "AN": [
        {"title": "finale", "artist": "eill", "description": "애니메이션 '체인소 맨' 삽입곡. eill의 섬세한 보컬이 감동적인 엔딩을 완성."},
        {"title": "愛にできることはまだあるかい", "artist": "RADWIMPS", "description": "영화 '날씨의 아이' OST. RADWIMPS 특유의 서정적인 감성이 가득."},
    ],
    "OST": [
        {"title": "初恋", "artist": "우타다 히카루 (宇多田ヒカル)", "description": "Netflix 드라마 '퍼스트 러브 하츠코이' OST. 애절한 보컬이 드라마의 감동을 배가."},
        {"title": "One in a Million -奇跡の夜に-", "artist": "GENERATIONS from EXILE TRIBE", "description": "웅장한 편곡과 파워풀한 퍼포먼스가 인상적인 드라마틱한 OST."},
    ],
    "RK": [
        {"title": "ホワイトノイズ", "artist": "Official髭男dism", "description": "폭발적인 에너지와 감정선이 공존하는 강렬한 록 넘버."},
        {"title": "A Priori", "artist": "Mrs. GREEN APPLE", "description": "세련된 멜로디와 독창적인 세계관이 돋보이는 팝록 트랙."},
    ],
}

# ----------------------------------------------------------
# 3. 질문 + 선택지 + 가중치 데이터
#    (카테고리당 최대 점수가 모두 22점으로 동일)
# ----------------------------------------------------------
QUESTIONS = [
    {
        "question": "음악을 들을 때 가장 끌리는 분위기는?",
        "options": [
            {"key": "A", "label": "노스탤지어한 도시의 밤", "weights": {"CP": 3}},
            {"key": "B", "label": "부드럽고 그루비한 무드", "weights": {"RB": 3}},
            {"key": "C", "label": "신나고 들썩이는 에너지", "weights": {"DC": 2, "HH": 1}},
            {"key": "D", "label": "잔잔하게 마음을 울리는 감성", "weights": {"OST": 2, "AN": 3}},
        ],
    },
    {
        "question": "선호하는 보컬 스타일은?",
        "options": [
            {"key": "A", "label": "허스키하고 소울풀한 보컬", "weights": {"RB": 3}},
            {"key": "B", "label": "파워풀하고 시원시원한 보컬", "weights": {"RK": 3}},
            {"key": "C", "label": "톡톡 튀는 랩/플로우", "weights": {"HH": 3}},
            {"key": "D", "label": "섬세하고 감정선이 풍부한 보컬", "weights": {"OST": 2, "AN": 1}},
        ],
    },
    {
        "question": "평소 즐겨보는 영상 콘텐츠는?",
        "options": [
            {"key": "A", "label": "감성 브이로그/드라이브 영상", "weights": {"CP": 3}},
            {"key": "B", "label": "일본 애니메이션", "weights": {"AN": 3}},
            {"key": "C", "label": "일본 드라마/영화", "weights": {"OST": 3}},
            {"key": "D", "label": "콘서트/밴드 라이브 영상", "weights": {"RK": 3}},
        ],
    },
    {
        "question": "좋아하는 사운드·악기는?",
        "options": [
            {"key": "A", "label": "신디사이저 + 그루비한 베이스라인", "weights": {"CP": 2, "RB": 1}},
            {"key": "B", "label": "강렬한 기타 리프와 드럼", "weights": {"RK": 3}},
            {"key": "C", "label": "비트 중심의 샘플링 사운드", "weights": {"HH": 3}},
            {"key": "D", "label": "화려한 신스/EDM 사운드", "weights": {"DC": 3, "OST": 2}},
        ],
    },
    {
        "question": "가사에서 가장 끌리는 주제는?",
        "options": [
            {"key": "A", "label": "도시의 풍경과 추억", "weights": {"CP": 3}},
            {"key": "B", "label": "사랑과 이별 이야기", "weights": {"OST": 2, "RB": 3}},
            {"key": "C", "label": "청춘과 위로의 메시지", "weights": {"AN": 2, "RK": 1}},
            {"key": "D", "label": "자유롭고 솔직한 라이프스타일", "weights": {"HH": 3, "DC": 2}},
        ],
    },
    {
        "question": "선호하는 템포는?",
        "options": [
            {"key": "A", "label": "느리고 여유로운 템포", "weights": {"CP": 2, "RB": 4}},
            {"key": "B", "label": "중간 템포의 감성적인 흐름", "weights": {"OST": 2, "AN": 4}},
            {"key": "C", "label": "빠르고 신나는 템포", "weights": {"DC": 3, "HH": 1}},
            {"key": "D", "label": "무겁고 파워풀한 템포", "weights": {"RK": 3, "HH": 1}},
        ],
    },
    {
        "question": "좋아하는 무대·퍼포먼스 스타일은?",
        "options": [
            {"key": "A", "label": "화려한 군무와 비주얼", "weights": {"DC": 3}},
            {"key": "B", "label": "랩과 자유로운 무대 매너", "weights": {"HH": 3}},
            {"key": "C", "label": "악기를 직접 연주하는 밴드 라이브", "weights": {"RK": 3}},
            {"key": "D", "label": "잔잔하게 감정을 전달하는 무대", "weights": {"OST": 2, "RB": 1}},
        ],
    },
    {
        "question": "최근 한국에서 유행한 일본 음악 트렌드 중 가장 끌리는 건?",
        "options": [
            {"key": "A", "label": "시티팝 감성 플레이리스트", "weights": {"CP": 3}},
            {"key": "B", "label": "애니메이션 OST 챌린지", "weights": {"AN": 3}},
            {"key": "C", "label": "일본 힙합/랩 챌린지", "weights": {"HH": 3}},
            {"key": "D", "label": "일본 댄스/아이돌 챌린지", "weights": {"DC": 3}},
        ],
    },
    {
        "question": "노래를 들으면 떠오르는 장면은?",
        "options": [
            {"key": "A", "label": "야경 속 드라이브", "weights": {"CP": 2, "RB": 1}},
            {"key": "B", "label": "카페에서의 잔잔한 오후", "weights": {"RB": 3, "OST": 3}},
            {"key": "C", "label": "콘서트장의 떼창", "weights": {"RK": 2, "AN": 2}},
            {"key": "D", "label": "화려한 댄스 챌린지", "weights": {"DC": 2, "HH": 1}},
        ],
    },
    {
        "question": "아래 키워드 중 가장 끌리는 것은?",
        "options": [
            {"key": "A", "label": "노스탤지어", "weights": {"CP": 4}},
            {"key": "B", "label": "소울/그루브", "weights": {"RB": 4}},
            {"key": "C", "label": "퍼포먼스", "weights": {"DC": 4}},
            {"key": "D", "label": "자유로움", "weights": {"HH": 4}},
            {"key": "E", "label": "두근거림", "weights": {"AN": 4}},
            {"key": "F", "label": "영화 같은 순간", "weights": {"OST": 4}},
            {"key": "G", "label": "라이브의 에너지", "weights": {"RK": 4}},
        ],
    },
]


# ----------------------------------------------------------
# 4. 요청 / 응답 모델
# ----------------------------------------------------------
class AnswerRequest(BaseModel):
    answers: List[str]  


class RecommendResponse(BaseModel):
    category: str
    category_name: str
    description: str
    scores: Dict[str, float]
    songs: List[Dict[str, str]]


# ----------------------------------------------------------
# 5. 엔드포인트
# ----------------------------------------------------------
@app.get("/")
def root():
    return {"message": "J-POP 취향 추천 API가 정상적으로 동작 중입니다 🎵"}


@app.get("/questions")
def get_questions():
    #Streamlit에서 질문/선택지 목록을 가져오기 위한 엔드포인트
    return QUESTIONS


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: AnswerRequest):
    """
    답변을 받아서 가중치+고유값 합산,
    가장 점수가 높은 카테고리와 추천곡 2곡 반환
    """
    if len(req.answers) != len(QUESTIONS):
        return {
            "category": "",
            "category_name": "",
            "description": f"{len(QUESTIONS)}개의 답변이 필요합니다. (받은 답변 수: {len(req.answers)})",
            "scores": {},
            "songs": [],
        }

    # 원점수 계산 
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for i, ans in enumerate(req.answers):
        question = QUESTIONS[i]
        option = next((o for o in question["options"] if o["key"] == ans.upper()), None)
        if option is None:
            continue
        for cat, weight in option["weights"].items():
            scores[cat] += weight

    # 동점 방지용 보정값을 더해서 최종 점수 계산
    final_scores = {cat: scores[cat] + EPSILON[cat] for cat in CATEGORIES}

    best_category = max(final_scores, key=lambda c: final_scores[c])

    return {
        "category": best_category,
        "category_name": CATEGORY_NAMES[best_category],
        "description": CATEGORY_DESCRIPTIONS[best_category],
        "scores": scores,
        "songs": SONGS[best_category],
    }