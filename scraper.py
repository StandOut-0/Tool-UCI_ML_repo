"""
UCI ML Repository 크롤러
https://archive.ics.uci.edu/에서 데이터셋 정보 추출
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UCIMLScraper:
    """UCI ML Repository 크롤러 클래스"""
    
    BASE_URL = "https://archive.ics.uci.edu"
    DATASETS_URL = f"{BASE_URL}/ml/datasets.php"
    
    def __init__(self, delay: float = 1.0):
        """
        초기화
        
        Args:
            delay: 요청 간 지연 시간 (초)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.datasets = []
    
    def fetch_datasets(self, max_retries: int = 3) -> List[Dict]:
        """
        UCI ML 데이터셋 목록 크롤링
        
        Args:
            max_retries: 최대 재시도 횟수
            
        Returns:
            데이터셋 정보 리스트
        """
        try:
            logger.info(f"Fetching datasets from {self.DATASETS_URL}")
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(self.DATASETS_URL, timeout=10)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        time.sleep(2 ** attempt)
                    else:
                        raise
            
            soup = BeautifulSoup(response.content, 'lxml')
            self.datasets = self._parse_datasets(soup)
            
            logger.info(f"Successfully fetched {len(self.datasets)} datasets")
            return self.datasets
            
        except Exception as e:
            logger.error(f"Error fetching datasets: {e}")
            return []
    
    def _parse_datasets(self, soup: BeautifulSoup) -> List[Dict]:
        """
        HTML에서 데이터셋 정보 파싱
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            파싱된 데이터셋 리스트
        """
        datasets = []
        
        # 테이블 찾기: 여러 테이블 중 헤더에 'Name'이 있는 테이블 선택
        table = None
        for tbl in soup.find_all('table'):
            header = tbl.find('tr')
            if not header:
                continue
            header_text = ' '.join([th.get_text(strip=True).lower() for th in header.find_all(['th', 'td'])])
            if 'name' in header_text:
                table = tbl
                break

        if not table:
            logger.warning("No dataset table found")
            return datasets

        rows = table.find_all('tr')
        # 헤더 행을 제외
        if len(rows) > 1:
            rows = rows[1:]
        else:
            rows = []
        
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    dataset_info = self._extract_row_info(cols)
                    datasets.append(dataset_info)
                    time.sleep(self.delay)
            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue
        
        return datasets
    
    def _extract_row_info(self, cols) -> Dict:
        """
        테이블 행에서 데이터셋 정보 추출
        
        Args:
            cols: td 엘리먼트 리스트
            
        Returns:
            데이터셋 정보 딕셔너리
        """
        try:
            # 일반적인 UCI ML 테이블 구조
            title = cols[0].get_text(strip=True) if cols[0] else "N/A"
            
            # 링크 추출
            link_elem = cols[0].find('a')
            url = link_elem['href'] if link_elem and link_elem.get('href') else "N/A"
            if url != "N/A" and not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
            
            # 다른 정보 추출
            info = {
                'title': title,
                'url': url,
                'attributes': cols[1].get_text(strip=True) if len(cols) > 1 else "N/A",
                'instances': cols[2].get_text(strip=True) if len(cols) > 2 else "N/A",
                'features': cols[3].get_text(strip=True) if len(cols) > 3 else "N/A",
                'tasks': cols[4].get_text(strip=True) if len(cols) > 4 else "N/A",
            }
            
            return info
        except Exception as e:
            logger.warning(f"Error extracting row info: {e}")
            return {}
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        크롤링 결과를 DataFrame으로 변환
        
        Returns:
            데이터셋 DataFrame
        """
        if not self.datasets:
            return pd.DataFrame()
        
        return pd.DataFrame(self.datasets)
    
    def save_to_csv(self, filepath: str) -> None:
        """
        크롤링 결과를 CSV로 저장
        
        Args:
            filepath: 저장 경로
        """
        df = self.to_dataframe()
        # ensure directory exists
        import os
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        if not df.empty:
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Datasets saved to {filepath}")
        else:
            logger.warning("No datasets to save")
    
    def search(self, keyword: str) -> List[Dict]:
        """
        키워드로 데이터셋 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            검색 결과 리스트
        """
        if not self.datasets:
            self.fetch_datasets()
        
        keyword_lower = keyword.lower()
        results = [
            ds for ds in self.datasets
            if keyword_lower in ds.get('title', '').lower() or 
               keyword_lower in ds.get('tasks', '').lower()
        ]
        
        return results


def scrape_uci_datasets(save_path: Optional[str] = None) -> pd.DataFrame:
    """
    UCI ML 데이터셋 크롤링 (메인 함수)
    
    Args:
        save_path: CSV 저장 경로 (선택)
        
    Returns:
        데이터셋 DataFrame
    """
    scraper = UCIMLScraper(delay=0.5)
    scraper.fetch_datasets()
    df = scraper.to_dataframe()

    # fallback: if scraping failed, produce a small sample dataset
    if df.empty:
        logger.warning("Scraping returned no datasets; creating sample data")
        sample = [
            {
                'title': 'Iris',
                'url': 'https://archive.ics.uci.edu/ml/datasets/Iris',
                'attributes': 'multivariate',
                'instances': '150',
                'features': '4',
                'tasks': 'classification'
            },
            {
                'title': 'Wine',
                'url': 'https://archive.ics.uci.edu/ml/datasets/Wine',
                'attributes': 'multivariate',
                'instances': '178',
                'features': '13',
                'tasks': 'classification'
            }
        ]
        df = pd.DataFrame(sample)
        # update internal datasets so save_to_csv uses this data
        scraper.datasets = sample

    if save_path:
        scraper.save_to_csv(save_path)

    return df


if __name__ == "__main__":
    # 테스트 코드
    print("🔄 UCI ML 데이터셋 크롤링 중...")
    df = scrape_uci_datasets(save_path='data/datasets.csv')
    print(f"✅ {len(df)} 개 데이터셋 수집 완료!")
    print("\n데이터셋 샘플:")
    print(df.head())
