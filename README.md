# 📚 Multimodal RAG

> 텍스트 · 표 · 이미지가 뒤섞인 PDF를, **그림까지 읽고 답하는** 검색 증강 생성(RAG) 파이프라인

PDF 한 권을 통째로 질문에 답할 수 있는 지식원으로 바꿉니다. 문서에서 **텍스트 · 표 · 그림(figure)** 을 각각 뽑아내고, 요약으로 색인한 뒤, **멀티모달 LLM** 이 원본(이미지 포함)을 직접 보고 답을 생성합니다.

---

## 🎯 문제 정의

일반적인 텍스트 전용 RAG는 PDF를 글자로만 읽습니다. 그래서 다음을 놓칩니다.

| 구분 | 텍스트 전용 RAG | 이 프로젝트 |
| :--- | :--- | :--- |
| 📊 **표(Table)** | 줄바꿈이 깨져 숫자·구조 유실 | 표 구조를 보존해 추출·요약 |
| 🖼️ **그림(Figure)** | 아예 읽지 못함 | 비전 모델이 이미지를 설명·검색 |
| 🔍 **검색 품질** | 원문 그대로 임베딩 → 노이즈 | 요약본으로 색인 → 핵심만 검색 |
| 💬 **답변 근거** | 텍스트 조각만 참고 | 원본 이미지를 LLM에 직접 전달 |

> **핵심 질문** — *"그림과 표가 많은 문서에서, 모델이 실제로 그 그림을 보고 답하게 하려면 어떻게 구성해야 하는가?"*

이를 풀기 위해 **요약으로 찾고(index) 원본으로 답하는(answer)** 다중 벡터(Multi-Vector) 구조를 사용합니다.

---

## 🏗️ 시스템 구조

```
            ┌──────────────┐
  PDF ─────▶│ ① 추출       │  텍스트 · 표 · 그림(figure) 분리
            │  extract.py  │  (unstructured)
            └──────┬───────┘
                   │
            ┌──────▼───────┐
            │ ② 요약       │  텍스트·표 → LLM 요약
            │ summarize.py │  이미지 → 비전 모델 설명
            └──────┬───────┘
                   │
            ┌──────▼─────────────────────────────┐
            │ ③ 다중 벡터 검색기                  │
            │  retriever.py                       │
            │                                     │
            │  요약본  ──▶ VectorStore (색인 카드) │
            │  원본    ──▶ DocStore   (진짜 책)    │
            └──────┬─────────────────────────────┘
                   │
   질문 ──▶ 요약으로 검색 ──▶ 원본 꺼내기 ──▶ 멀티모달 LLM ──▶ 답변
            (색인 카드)       (서가의 원본)    (눈 달린 모델)
```

| 단계 | 모듈 | 하는 일 |
| :-- | :-- | :-- |
| ① 추출 | [`src/extract.py`](src/extract.py) | PDF를 파싱해 텍스트·표·이미지로 분리 |
| ② 요약 | [`src/summarize.py`](src/summarize.py) | 각 요소를 **검색에 최적화된** 요약으로 변환 |
| ③ 검색·생성 | [`src/retriever.py`](src/retriever.py) | 요약으로 검색하고 **원본을 반환**하는 검색기 구성 |

**핵심 아이디어** — 요약본은 가볍고 핵심만 담아 *검색 정확도*를 높이고, 답변 생성 단계에서는 *정보 손실이 없는 원본*(표·이미지 포함)을 LLM에 넘깁니다.

---

## ❓ 예시 질문

이 파이프라인이 답할 수 있는 질문의 형태입니다.

- 📈 *"○○ 그래프에서 가장 높은 값을 보인 구간은 어디인가요?"* — **그림**을 보고 답변
- 📊 *"표에 정리된 항목별 수치를 요약해 주세요."* — **표** 구조를 이해해 답변
- 📝 *"이 문서의 핵심 주장을 3줄로 정리해 주세요."* — **텍스트** 기반 답변
- 🔗 *"본문 설명과 그림이 말하는 내용이 일치하나요?"* — **텍스트 + 이미지** 교차 확인

---

## 🚀 설치 및 실행

```bash
git clone <저장소 주소>
cd multimodal-rag

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate          # 윈도우: .venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt     # 또는 requirements.lock.txt

# 커널 등록
python -m ipykernel install --user --name multimodal-rag

# .env 작성
cp .env.example .env                # 윈도우: copy .env.example .env
# .env 파일을 열어 실제 API 키를 입력
```

> 💡 PDF 파싱에는 OS 패키지 **Poppler** 와 **Tesseract** 가 필요합니다. 설치 여부는 [`notebooks/Multi_modal_RAG.ipynb`](notebooks/Multi_modal_RAG.ipynb) 첫 셀에서 확인할 수 있습니다.

---

## 📂 프로젝트 구조

```
multimodal-rag/
├── src/
│   ├── extract.py       # ① PDF → 텍스트·표·이미지 추출
│   ├── summarize.py     # ② 요소별 요약 (텍스트·표·이미지)
│   └── retriever.py     # ③ 다중 벡터 검색기
├── notebooks/           # 단계별 실습 노트북
├── data/
│   ├── figures/         # 추출된 그림(figure) 이미지
│   └── processed/       # 추출·요약 중간 결과물(pkl)
└── requirements.txt
```
