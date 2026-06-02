# UCI ML Dataset Explorer (MVP)

간단한 UCI Machine Learning Repository 데이터셋 크롤러 및 Streamlit 기반 탐색기입니다.

Usage:

1. 설치

```bash
python -m pip install -r requirements.txt
```

2. 로컬에서 실행

```bash
streamlit run app.py
```

3. 개발
- 크롤링: `python scraper.py` (결과는 `data/datasets.csv`에 저장됩니다)
- 즐겨찾기: `cache/favorites.json`
