import streamlit as st
import pandas as pd
import io
from datetime import datetime
from scraper import scrape_uci_datasets
from utils import filter_datasets, get_dataset_statistics, get_task_types, FavoritesManager, validate_url


@st.cache_data(ttl=3600)  # 1시간 캐싱
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


def get_csv_download(df: pd.DataFrame) -> bytes:
    """DataFrame을 CSV로 변환"""
    return df.to_csv(index=False, encoding='utf-8').encode('utf-8')


def render_export_options(filtered_df):
    """CSV 내보내기 옵션"""
    st.subheader("📥 데이터 내보내기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 전체 데이터 내보내기
        df = load_data()
        csv_all = get_csv_download(df)
        st.download_button(
            label="📊 전체 데이터셋 (CSV)",
            data=csv_all,
            file_name=f"uci_ml_datasets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # 필터링된 데이터 내보내기
        csv_filtered = get_csv_download(filtered_df)
        st.download_button(
            label="🔍 필터링된 데이터셋 (CSV)",
            data=csv_filtered,
            file_name=f"uci_ml_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


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

    # 필터 적용
    task_filter = None if task == "모두" else task
    filtered = filter_datasets(df, search_keyword=search, min_instances=min_instances, task_filter=task_filter)

    # 탭 메뉴
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 홈", "⭐ 즐겨찾기", "📈 통계", "ℹ️ 정보"])

    with tab1:
        # 뷰 모드 선택
        col_view = st.columns([3, 1])[1]
        with col_view:
            view_options = ["📊 테이블", "🗂️ 카드"]
            view_choice = st.radio("보기 방식", view_options, horizontal=True, label_visibility="collapsed")
            st.session_state.view_mode = 'table' if view_choice == "📊 테이블" else 'cards'

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

    with tab2:
        st.subheader("⭐ 즐겨찾기 데이터셋")
        
        if not favorites:
            st.info("즐겨찾기된 데이터셋이 없습니다.")
        else:
            fav_df = df[df['title'].isin(favorites)].reset_index(drop=True)
            
            if fav_df.empty:
                st.warning("즐겨찾기된 데이터셋 중 삭제된 항목이 있습니다.")
            else:
                st.dataframe(fav_df, use_container_width=True, hide_index=True)
                
                # 즐겨찾기 CSV 내보내기
                csv_fav = get_csv_download(fav_df)
                st.download_button(
                    label="⭐ 즐겨찾기 CSV 다운로드",
                    data=csv_fav,
                    file_name=f"favorites_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with tab3:
        st.subheader("📈 데이터셋 통계")
        
        stats = get_dataset_statistics(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📌 전체 데이터셋", stats.get("total_datasets", 0))
        with col2:
            st.metric("📊 총 인스턴스", f"{stats.get('total_instances', 0):,}")
        with col3:
            st.metric("🔢 총 속성", stats.get("total_attributes", 0))
        
        st.divider()
        
        # 작업 유형별 분포
        st.subheader("작업 유형별 분포")
        task_dist = stats.get('task_distribution', {})
        if task_dist:
            task_df = pd.DataFrame(
                list(task_dist.items()),
                columns=['작업 유형', '개수']
            ).sort_values('개수', ascending=False)
            st.bar_chart(task_df.set_index('작업 유형'))
            st.dataframe(task_df, use_container_width=True, hide_index=True)
        else:
            st.info("작업 유형별 통계 데이터 없음")

    with tab4:
        st.subheader("ℹ️ 프로젝트 정보")
        
        st.write("""
        ### UCI ML 데이터셋 탐색기
        
        이 앱은 UCI Machine Learning Repository의 데이터셋을 쉽게 검색하고 탐색할 수 있도록 도와줍니다.
        
        **기능:**
        - 🔍 키워드 검색
        - 📊 작업 유형별 필터링
        - 📈 데이터셋 통계
        - ⭐ 즐겨찾기 관리
        - 📥 CSV 내보내기
        - 🗂️ 테이블/카드 뷰 전환
        
        **기술 스택:**
        - Python
        - Streamlit
        - Pandas
        - BeautifulSoup
        
        **링크:**
        - [UCI ML Repository](https://archive.ics.uci.edu/)
        - [GitHub](https://github.com)
        """)
        
        st.divider()
        
        # 일반 내보내기
        render_export_options(filtered)


if __name__ == "__main__":
    main()
