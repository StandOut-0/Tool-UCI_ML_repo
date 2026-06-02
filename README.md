# 🔍 UCI ML 데이터셋 탐색기

UCI Machine Learning Repository의 머신러닝 데이터셋을 쉽게 검색, 탐색, 관리할 수 있는 Streamlit 기반 웹 애플리케이션입니다.

## 🎯 주요 기능

### 홈 탭
- 📊 데이터셋 검색 및 필터링
- 🗂️ 테이블 / 카드 이중 뷰
- 📈 실시간 통계 대시보드
- 📄 상세 정보 페이지

### 즐겨찾기 탭
- ⭐ 저장된 데이터셋 관리
- 📥 즐겨찾기 CSV 내보내기

### 통계 탭
- 📊 전체 데이터셋 통계
- 📈 작업 유형별 분포 시각화

### 정보 탭
- ℹ️ 프로젝트 설명 및 기술 스택
- 🔗 유용한 링크

## 🚀 빠른 시작

### 1️⃣ 환경 설정

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (Batch):**
```batch
setup_venv.bat
```

**Unix/macOS:**
```bash
bash setup_venv.sh
```

### 2️⃣ 로컬 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 열립니다 (http://localhost:8501)

### 3️⃣ Docker로 실행 (선택사항)

```bash
docker-compose up
```

## 📦 기술 스택

- **Python 3.9+**
- **Streamlit** - 웹 프레임워크
- **Pandas** - 데이터 처리
- **BeautifulSoup4** - 웹 크롤링
- **Requests** - HTTP 요청

## 📂 프로젝트 구조

```
Tool-UCI_ML_repo/
├── app.py                    # Streamlit 메인 애플리케이션
├── scraper.py               # 데이터셋 크롤러
├── utils.py                 # 유틸리티 함수
├── requirements.txt         # 의존성
├── README.md               # 이 파일
├── Dockerfile              # Docker 설정
├── docker-compose.yml      # Docker Compose 설정
├── setup_venv.bat          # Windows venv 스크립트
├── setup_venv.sh           # Unix/Mac venv 스크립트
├── .gitignore              # Git 제외 파일
├── .streamlit/
│   └── config.toml         # Streamlit 설정
├── data/
│   └── datasets.csv        # 크롤링된 데이터셋
├── cache/
│   └── favorites.json      # 즐겨찾기 저장소
└── docs/
    ├── VENV_SETUP.md       # venv 설정 가이드
    ├── DAY2_FEATURES.md    # Day2 기능 문서
    └── DAY3_FEATURES.md    # Day3 고급 기능 문서
```

## 💡 사용 예시

### 데이터셋 검색
1. 검색창에 키워드 입력
2. 작업 유형별로 필터링
3. 최소 인스턴스 수 설정

### 즐겨찾기 추가
1. 데이터셋 상세 보기
2. "⭐ 즐겨찾기 토글" 클릭
3. 즐겨찾기 탭에서 확인

### 데이터 내보내기
1. 정보 탭의 "데이터 내보내기" 섹션
2. 전체 또는 필터링된 데이터셋 선택
3. CSV 파일 다운로드

## 🔧 주요 기능 상세

### 캐싱
- 1시간 TTL로 데이터셋 캐싱
- "실시간 크롤링" 버튼으로 수동 새로고침 가능

### 다중 탭 페이지
- 홈: 주요 검색 및 탐색 기능
- 즐겨찾기: 저장된 데이터셋 관리
- 통계: 데이터 시각화
- 정보: 프로젝트 설명

### 세션 상태 관리
- 뷰 모드 유지
- 선택된 데이터셋 추적
- 상태 기반 UI 렌더링

## 📊 통계 정보

앱은 다음 통계를 제공합니다:
- 📌 전체 데이터셋 수
- 📊 총 인스턴스 수
- 🔢 총 속성 수
- 📈 작업 유형별 분포

## 🌐 배포

### Streamlit Cloud (권장)
1. GitHub에 저장소 push
2. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
3. 새 앱 연결
4. GitHub 저장소 선택
5. `app.py` 파일 지정

### Docker / Kubernetes
```bash
docker build -t uci-ml-explorer .
docker run -p 8501:8501 uci-ml-explorer
```

또는 Docker Compose:
```bash
docker-compose up -d
```

## 📝 개발 노트

### Day 1: 기초 설정 & 크롤링
- venv 환경 설정
- 크롤링 로직 개발
- 샘플 데이터 생성

### Day 2: 웹앱 UI/UX
- Streamlit 기본 앱 구조
- 세션 상태 관리
- 테이블/카드 이중 뷰
- 향상된 필터링

### Day 3: 고급 기능 & 배포
- 캐싱 최적화
- 다중 탭 페이지
- CSV 내보내기
- Docker/Streamlit 배포 설정

## 📄 라이센스

MIT License - 자유로이 사용, 수정, 배포 가능합니다.

## 🔗 링크

- [UCI ML Repository](https://archive.ics.uci.edu/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Streamlit Cloud](https://streamlit.io/cloud)

---

**개발 기간**: 3일 (Day 1-3)  
**마지막 업데이트**: 2026-06-02

