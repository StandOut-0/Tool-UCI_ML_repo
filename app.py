import streamlit as st
import pandas as pd
from scraper import scrape_uci_datasets
from utils import filter_datasets, get_dataset_statistics, get_task_types, FavoritesManager, validate_url


@st.cache_data
def load_data(path: str = "data/datasets.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        # fallback to running scraper
        return scrape_uci_datasets(save_path=path)


def init_session_state():
    """세션 상태 초기화"""
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'table'  # 'table' 또는 'cards'
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None


def render_dataset_card(dataset_row, fav_mgr, col):
    """데이터셋 카드 렌더링"""
    with col:
        with st.container(border=True):
            st.markdown(f"### {dataset_row['title']}")
            st.caption(f"📝 {dataset_row.get('tasks', 'N/A')}")
            
            # 메트릭
            c1, c2, c3 = st.columns(3)
            c1.metric("속성", dataset_row.get('attributes', 'N/A'))
            c2.metric("인스턴스", dataset_row.get('instances', 'N/A'))
            c3.metric("특성", dataset_row.get('features', 'N/A'))
            
            # 링크
            url = dataset_row.get('url', '')
            if validate_url(url):
                st.markdown(f"[🔗 데이터셋 보기]({url})")
            
            # 선택 버튼
            if st.button("상세 보기", key=f"select_{dataset_row['title']}"):
                st.session_state.selected_dataset = dataset_row['title']
                st.rerun()


def render_table_view(filtered_df):
    """테이블 뷰 렌더링"""
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'url': st.column_config.LinkColumn('데이터셋 링크'),
        }
    )


def render_cards_view(filtered_df, fav_mgr):
    """카드 뷰 렌더링"""
    if filtered_df.empty:
        st.info("검색 결과가 없습니다.")
        return
    
    # 3열로 나누어 표시
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        col = cols[idx % 3]
        render_dataset_card(row, fav_mgr, col)


def main():
    st.set_page_config(page_title="UCI ML 데이터셋 탐색기", layout="wide")
    init_session_state()
    
    # 헤더
    st.title("🔍 UCI ML 데이터셋 탐색기")
    st.markdown("UCI Machine Learning Repository에서 머신러닝 데이터셋을 찾아보세요.")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 필터 & 제어")
        
        # 새로고침
        if st.button("🔄 실시간 크롤링", use_container_width=True):
            with st.spinner("데이터셋 크롤링 중..."):
                scrape_uci_datasets(save_path="data/datasets.csv")
                load_data.clear()
                st.success("데이터셋이 업데이트되었습니다!")
                st.rerun()
        
        st.divider()
        
        # 검색
        search = st.text_input(
            "🔎 검색",
            placeholder="데이터셋 이름 또는 작업 유형으로 검색"
        )
        
        # 필터
        df = load_data()
        task_types = ["모두"] + get_task_types(df)
        task = st.selectbox("📊 작업 유형", task_types)
        
        min_instances = st.slider("📈 최소 인스턴스 수", 0, 10000, 0, 100)
        
        st.divider()
        
        # 즐겨찾기
        fav_mgr = FavoritesManager(filepath="cache/favorites.json")
        favorites = fav_mgr.get_favorites()
        
        if favorites:
            st.subheader("⭐ 즐겨찾기")
            for fav in favorites:
                st.caption(f"• {fav}")
        else:
            st.caption("즐겨찾기가 없습니다.")

    # 메인 콘텐츠
    col_title, col_view = st.columns([3, 1])
    with col_title:
        pass  # 제목은 위에서 처리
    
    with col_view:
        # 뷰 모드 선택
        view_options = ["📊 테이블", "🗂️ 카드"]
        view_choice = st.radio("보기 방식", view_options, horizontal=True, label_visibility="collapsed")
        st.session_state.view_mode = 'table' if view_choice == "📊 테이블" else 'cards'

    # 필터 적용
    # task 필터 처리: "모두"는 None으로
    task_filter = None if task == "모두" else task
    filtered = filter_datasets(df, search_keyword=search, min_instances=min_instances, task_filter=task_filter)

    # 통계
    stats = get_dataset_statistics(filtered)
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric("📌 데이터셋 수", stats.get("total_datasets", 0))
    with stat_col2:
        st.metric("📊 총 인스턴스", f"{stats.get('total_instances', 0):,}")
    with stat_col3:
        st.metric("🔢 총 속성", stats.get("total_attributes", 0))
    with stat_col4:
        st.metric("⏰ 마지막 업데이트", stats.get("last_updated", "-"))

    st.divider()

    # 뷰 모드별 렌더링
    if st.session_state.view_mode == 'table':
        st.subheader("📋 데이터셋 목록")
        render_table_view(filtered)
    else:
        st.subheader("🗂️ 데이터셋 카드")
        render_cards_view(filtered, fav_mgr)

    st.divider()

    # 상세 보기
    if st.session_state.selected_dataset:
        selected_title = st.session_state.selected_dataset
        if selected_title in filtered['title'].values:
            row = filtered[filtered['title'] == selected_title].iloc[0]
            st.subheader(f"📄 상세 정보: {selected_title}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**기본 정보**")
                st.write(f"- **제목**: {row['title']}")
                st.write(f"- **작업**: {row.get('tasks', 'N/A')}")
                st.write(f"- **속성**: {row.get('attributes', 'N/A')}")
            
            with col2:
                st.write("**크기**")
                st.write(f"- **인스턴스**: {row.get('instances', 'N/A')}")
                st.write(f"- **특성**: {row.get('features', 'N/A')}")
            
            # 링크
            url = row.get('url', '')
            if validate_url(url):
                st.markdown(f"**🔗 [데이터셋 다운로드]({url})**")
            
            # 즐겨찾기 버튼
            col_fav, col_close = st.columns([1, 3])
            with col_fav:
                is_fav = fav_mgr.is_favorite(selected_title)
                if st.button("⭐ 즐겨찾기 토글", use_container_width=True):
                    if is_fav:
                        fav_mgr.remove_favorite(selected_title)
                        st.info(f"✅ '{selected_title}'를 즐겨찾기에서 제거했습니다.")
                    else:
                        fav_mgr.add_favorite(selected_title)
                        st.success(f"✅ '{selected_title}'를 즐겨찾기에 추가했습니다.")
            
            with col_close:
                if st.button("닫기"):
                    st.session_state.selected_dataset = None
                    st.rerun()


if __name__ == "__main__":
    main()
