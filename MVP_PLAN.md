# UCI ML Dataset 크롤러 & 웹앱 - MVP 계획

## 프로젝트 개요
- **목표**: UCI Machine Learning Repository(https://archive.ics.uci.edu/)에서 데이터셋 정보를 크롤링하고, Streamlit 웹앱으로 시각화 및 관리
- **기술 스택**: Python, Streamlit, BeautifulSoup/Requests, Pandas
- **개발 기간**: 3일 (Day 1-3)

---

## 📅 개발 스케줄

### **Day 1: 기초 설정 & 크롤링 로직 개발**

#### 목표
- 프로젝트 환경 설정
- UCI ML 사이트 크롤링 기본 로직 완성
- 데이터셋 정보 추출 테스트

#### 세부 작업
1. **프로젝트 초기화** (1h)
   - 가상환경 생성 (`venv` 또는 `conda`)
   - requirements.txt 생성 및 필수 패키지 설치
     - `streamlit`
     - `requests`
     - `beautifulsoup4`
     - `pandas`
     - `lxml`

2. **크롤링 함수 개발** (2h)
   - `scraper.py` 작성
   - UCI 사이트 구조 분석
   - 데이터셋 제목, URL, 설명, 속성(feature) 수 등 추출
   - 에러 핸들링 (타임아웃, 네트워크 오류)

3. **로컬 테스트** (1h)
   - 크롤링 결과 검증
   - CSV로 저장 테스트
   - 샘플 데이터 확인

#### 📊 산출물
- `requirements.txt`
- `scraper.py` (크롤링 함수)
- `sample_data.csv` (테스트 데이터)

---

### **Day 2: Streamlit 기본 앱 구축**

#### 목표
- Streamlit 앱 프레임워크 완성
- 기본 UI/UX 구현
- 크롤링 데이터 표시

#### 세부 작업
1. **Streamlit 앱 구조 설계** (1h)
   - `app.py` 작성
   - 페이지 레이아웃 (헤더, 사이드바, 메인 콘텐츠)
   - 세션 상태 관리

2. **주요 기능 구현** (2h)
   - 📌 데이터셋 목록 표시 (테이블)
   - 🔍 검색 기능 (제목, 설명)
   - 📊 필터링 (속성 수, 데이터 크기 등)
   - 🔄 "새로고침" 버튼 (실시간 크롤링)

3. **UI 개선** (1h)
   - 대시보드 스타일 적용
   - 데이터셋 카드 디자인
   - 반응형 레이아웃

#### 📊 산출물
- `app.py` (Streamlit 메인 앱)
- `utils.py` (헬퍼 함수)

---

### **Day 3: 고급 기능 & 배포 준비**

#### 목표
- 사용자 경험 최적화
- 캐싱 및 성능 개선
- 배포 가능 상태

#### 세부 작업
1. **캐싱 및 성능 개선** (1h)
   - `@st.cache_data` 데코레이터로 크롤링 결과 캐싱
   - 로딩 시간 단축

2. **추가 기능** (1.5h)
   - 📥 데이터셋 다운로드 링크 제공
   - ⭐ 즐겨찾기 기능 (로컬 저장)
   - 📈 통계 대시보드 (데이터셋 개수, 최신 추가 데이터 등)
   - 🏷️ 태그/카테고리별 분류

3. **배포 준비** (1.5h)
   - README.md 작성
   - `.gitignore` 설정
   - Git 커밋
   - Streamlit Cloud 또는 로컬 서버 테스트

#### 📊 산출물
- 최종 `app.py` (모든 기능 포함)
- `README.md`
- `.gitignore`

---

## 🎯 MVP 핵심 기능

| 기능 | 우선순위 | 예상 시간 | 상태 |
|------|---------|---------|------|
| 크롤링 로직 | 🔴 필수 | 3h | Day 1 |
| 기본 Streamlit 앱 | 🔴 필수 | 4h | Day 2 |
| 데이터셋 테이블 표시 | 🔴 필수 | 2h | Day 2 |
| 검색/필터링 | 🟠 중요 | 2h | Day 2 |
| 캐싱 | 🟠 중요 | 1h | Day 3 |
| 다운로드 링크 | 🟡 선택 | 1h | Day 3 |
| 즐겨찾기 | 🟡 선택 | 1h | Day 3 |

---

## 📂 프로젝트 구조 (최종)

```
Tool-UCI_ML_repo/
├── MVP_PLAN.md          # 이 파일
├── README.md            # 프로젝트 설명
├── requirements.txt     # 의존성
├── .gitignore          # Git 제외 파일
├── app.py              # Streamlit 메인 앱
├── scraper.py          # 크롤링 로직
├── utils.py            # 헬퍼 함수
├── data/               # 저장된 데이터
│   └── datasets.csv
└── cache/              # 캐시 파일 (선택)
    └── favorites.json
```

---

## ✅ 완료 기준

- [ ] Day 1: 크롤링 함수 완성 & 테스트 성공
- [ ] Day 2: Streamlit 앱 실행 & 기본 기능 작동
- [ ] Day 3: 모든 기능 통합 & 배포 준비 완료

---

## 🚀 배포 옵션

1. **Streamlit Cloud** (무료)
   - GitHub 연동 후 간단히 배포
   
2. **로컬 서버** 
   - `streamlit run app.py`로 실행

3. **Docker** (선택)
   - 컨테이너화로 어디서나 실행 가능

---

## 📝 참고사항

- UCI ML 사이트의 robots.txt 확인 필수 (크롤링 정책)
- 요청 간 지연 추가 (서버 부하 방지)
- 정기적인 캐시 업데이트 (신규 데이터셋 반영)
