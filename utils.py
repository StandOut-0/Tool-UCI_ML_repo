"""
유틸리티 함수 모음
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd


class FavoritesManager:
    """즐겨찾기 관리 클래스"""
    
    def __init__(self, filepath: str = "cache/favorites.json"):
        """
        초기화
        
        Args:
            filepath: 즐겨찾기 파일 경로
        """
        self.filepath = filepath
        self.favorites = self._load_favorites()
    
    def _load_favorites(self) -> List[str]:
        """즐겨찾기 로드"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading favorites: {e}")
                return []
        return []
    
    def add_favorite(self, dataset_title: str) -> bool:
        """즐겨찾기 추가"""
        if dataset_title not in self.favorites:
            self.favorites.append(dataset_title)
            self._save_favorites()
            return True
        return False
    
    def remove_favorite(self, dataset_title: str) -> bool:
        """즐겨찾기 제거"""
        if dataset_title in self.favorites:
            self.favorites.remove(dataset_title)
            self._save_favorites()
            return True
        return False
    
    def is_favorite(self, dataset_title: str) -> bool:
        """즐겨찾기 여부 확인"""
        return dataset_title in self.favorites
    
    def get_favorites(self) -> List[str]:
        """모든 즐겨찾기 반환"""
        return self.favorites.copy()
    
    def _save_favorites(self) -> None:
        """즐겨찾기 저장"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)


def filter_datasets(
    df: pd.DataFrame,
    search_keyword: Optional[str] = None
) -> pd.DataFrame:
    """
    데이터셋 필터링
    
    Args:
        df: 데이터셋 DataFrame
        search_keyword: 검색 키워드
        
    Returns:
        필터링된 DataFrame
    """
    result = df.copy()
    
    if search_keyword:
        result = result[
            result['title'].str.contains(search_keyword, case=False, na=False)
        ]
    
    return result.reset_index(drop=True)


def get_dataset_statistics(df: pd.DataFrame) -> Dict:
    """
    데이터셋 통계 계산
    
    Args:
        df: 데이터셋 DataFrame
        
    Returns:
        통계 딕셔너리
    """
    stats = {
        'total_datasets': len(df),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return stats


def get_task_types(df: pd.DataFrame) -> List[str]:
    """
    고유한 작업 유형 추출 (deprecated)
    
    Args:
        df: 데이터셋 DataFrame
        
    Returns:
        작업 유형 리스트
    """
    return []


def format_number(num) -> str:
    """
    숫자를 포맷팅 (1000 -> 1K)
    
    Args:
        num: 숫자
        
    Returns:
        포맷팅된 문자열
    """
    try:
        num = float(num)
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(int(num))
    except:
        return str(num)


def validate_url(url: str) -> bool:
    """
    URL 유효성 확인
    
    Args:
        url: URL 문자열
        
    Returns:
        유효 여부
    """
    return url.startswith('http://') or url.startswith('https://')


if __name__ == "__main__":
    # 테스트 코드
    print("✅ Utils 모듈 테스트")
    
    # 즐겨찾기 테스트
    fav = FavoritesManager()
    fav.add_favorite("Dataset 1")
    fav.add_favorite("Dataset 2")
    print(f"즐겨찾기: {fav.get_favorites()}")
