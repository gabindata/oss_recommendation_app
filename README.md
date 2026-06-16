# 🎵 J-POP 장르 추천 앱

Streamlit + FastAPI + Docker 기반의 J-POP 장르 추천 웹 애플리케이션입니다.  
10가지 질문에 답하면, 당신에게 어울리는 J-POP 장르와 대표곡 2곡을 추천해 드립니다.

---

## 📁 프로젝트 구조

```
oss_recommendation_app/
├── front/
│   ├── app.py              # Streamlit 프론트엔드
│   ├── Dockerfile
│   └── requirements.txt
├── back/
│   ├── main.py             # FastAPI 백엔드
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .gitignore
```

---

## 🔧 기술 스택

| 역할 | 기술 |
|------|------|
| 프론트엔드 | Streamlit |
| 백엔드 | FastAPI |
| 컨테이너 | Docker / Docker Compose |
| 배포 환경 | AWS EC2 |

---

## 🚀 실행 방법

### 실행

- Docker 및 Docker Compose 설치 필요

```bash
git clone https://github.com/gabindata/oss_recommendation_app.git
cd oss_recommendation_app
docker compose up --build
```

### 접속

| 서비스 | 주소 |
|--------|------|
| Streamlit (프론트엔드) | http://localhost:8501 |
| FastAPI (백엔드) | http://localhost:8000 |
| FastAPI 문서 (Swagger) | http://localhost:8000/docs |

---

## 🎯 서비스 흐름

```
사용자 입력 → Streamlit → FastAPI 호출 → 추천 결과 반환 → Streamlit 화면 표시
```

1. Streamlit이 시작 시 FastAPI `/questions` 엔드포인트에서 질문 목록을 불러옵니다.
2. 사용자가 10개의 질문에 답하고 **추천 받기** 버튼을 클릭합니다.
3. Streamlit이 FastAPI `/recommend`에 답변 목록을 POST 요청으로 전송합니다.
4. FastAPI가 rule-based 가중치 합산으로 J-POP 장르를 분석하고 JSON으로 반환합니다.
5. Streamlit이 결과를 받아 장르명, 취향 설명, 추천곡 2곡(제목·아티스트·곡 설명)을 화면에 표시합니다.

---

## 🎶 추천 장르 목록

| 코드 | 장르 |
|------|------|
| CP | 시티팝 |
| RB | R&B |
| DC | 댄스 |
| HH | 힙합 |
| AN | 애니메이션 |
| OST | 드라마·영화 OST |
| RK | 락 |

> 동점일 경우 락, 드라마·영화 OST, 애니메이션, 힙합, 댄스, R&B, 시티팝 순으로 우선 결정됩니다.

---

## 📡 API 엔드포인트

### `GET /questions`
질문 및 선택지 목록 반환

### `POST /recommend`
**Request Body**
```json
{
  "answers": ["A", "C", "B", "D", "A", "B", "C", "A", "D", "G"]
}
```
**Response**
```json
{
  "category": "CP",
  "category_name": "시티팝",
  "description": "도시의 밤과 노스탤지어가 떠오르는, 여유롭고 그루비한 사운드를 좋아하시는군요...",
  "scores": { "CP": 10, "RB": 3, "...": "..." },
  "songs": [
    {
      "title": "Plastic Love",
      "artist": "타케우치 마리야 (竹内まりや)",
      "description": "1984년 발표된 시티팝의 상징. 유튜브 알고리즘으로 전 세계에 재조명된 전설의 곡."
    },
    {
      "title": "Fantasy",
      "artist": "나카하라 메이코 (中原めいこ)",
      "description": "몽환적인 신스팝 사운드로 도시의 밤을 달리는 듯한 그루비한 감성."
    }
  ]
}
```
