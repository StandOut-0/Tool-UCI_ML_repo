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
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None
    if 'unavailable_datasets' not in st.session_state:
        st.session_state.unavailable_datasets = set()


def get_csv_download(df: pd.DataFrame) -> bytes:
    """DataFrame을 CSV로 변환"""
    return df.to_csv(index=False, encoding='utf-8').encode('utf-8')


def render_export_options(filtered_df):
    """CSV 내보내기 옵션"""
    export_type = st.selectbox(
        "📥 내보내기 유형",
        ["전체 데이터셋", "필터링된 데이터셋"],
        label_visibility="collapsed"
    )
    
    if export_type == "전체 데이터셋":
        df = load_data()
        csv_data = get_csv_download(df)
        file_name = f"uci_ml_datasets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        csv_data = get_csv_download(filtered_df)
        file_name = f"uci_ml_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    st.download_button(
        label="CSV 다운로드",
        data=csv_data,
        file_name=file_name,
        mime="text/csv",
        width='stretch'
    )


def render_table_view(filtered_df, fav_mgr=None):
    """테이블 뷰 렌더링 with built-in pagination and checkboxes"""
    if filtered_df.empty:
        st.info("검색 결과가 없습니다.")
        return
    
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = set()
    
    # Get favorites list
    favorites = fav_mgr.get_favorites() if fav_mgr else []
    
    # Add checkbox column and star indicator
    display_df = filtered_df.copy()
    display_df = display_df.reset_index(drop=True)
    display_df['선택'] = display_df['title'].apply(lambda x: x in st.session_state.selected_rows)
    
    # Add star and warning emojis
    def add_indicators(title):
        indicators = []
        if title in favorites:
            indicators.append("⭐")
        if title in st.session_state.unavailable_datasets:
            indicators.append("⚠️")
        return f"{title} {' '.join(indicators)}" if indicators else title
    
    display_df['title'] = display_df['title'].apply(add_indicators)
    
    # Display as dataframe with checkbox column using built-in pagination
    edited_df = st.data_editor(
        display_df[['선택', 'title', 'url', 'python_import']],
        column_config={
            '선택': st.column_config.CheckboxColumn("선택", required=False),
            'title': st.column_config.TextColumn('데이터셋 이름'),
            'url': st.column_config.LinkColumn('데이터셋 링크'),
            'python_import': st.column_config.TextColumn('Python Import 코드'),
        },
        width='stretch',
        hide_index=True,
        use_container_width=True
    )
    
    # Update selected rows based on checkbox changes
    selected_titles = edited_df[edited_df['선택'] == True]['title'].tolist()
    st.session_state.selected_rows = set(selected_titles)
    
    # Bulk action buttons below table
    col1, col2 = st.columns([1, 1])
    with col1:
        # 전체 선택 토글 버튼
        all_selected = len(st.session_state.selected_rows) == len(display_df['title'].tolist())
        button_label = "전체 선택 해제" if all_selected else "전체 선택"
        if st.button(button_label, key="select_all_toggle"):
            if all_selected:
                st.session_state.selected_rows.clear()
            else:
                st.session_state.selected_rows.update(display_df['title'].tolist())
            st.rerun()
    with col2:
        if st.button("선택 항목 즐겨찾기 추가", key="bulk_add_fav"):
            for title in st.session_state.selected_rows:
                fav_mgr.add_favorite(title)
            st.session_state.selected_rows.clear()
            st.success(f"{len(st.session_state.selected_rows)}개 항목을 즐겨찾기에 추가했습니다.")
            st.rerun()


def main():
    st.set_page_config(
        page_title="UCI ML 데이터셋 탐색기",
        page_icon="assets/images/logo.png",
        layout="wide"
    )
    init_session_state()
    
    # 로고
    st.logo("assets/images/logo.png", link="https://archive.ics.uci.edu/", icon_image="assets/images/logo.png")
    
    # 헤더
    st.title("🔍 S data - UCI ML 데이터셋 탐색기")
    st.markdown("UCI Machine Learning Repository에서 머신러닝 데이터셋을 찾아보세요.")

    # 데이터 로드
    df = load_data()

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 제어")
        
        # 데이터 통계
        stats = get_dataset_statistics(df)
        st.metric("📌 데이터셋 수", stats.get("total_datasets", 0))
        st.caption(f"⏰ 마지막 업데이트: {stats.get('last_updated', '-')}")
        
        st.divider()
        
        # 새로고침
        if st.button("🔄 실시간 크롤링", width='stretch'):
            with st.spinner("데이터셋 크롤링 중..."):
                # Load existing data to compare
                old_df = load_data()
                old_count = len(old_df)
                
                # Scrape new data
                new_df = scrape_uci_datasets(save_path="data/datasets.csv")
                new_count = len(new_df)
                
                load_data.clear()
                
                if new_count == old_count:
                    st.info("추가/변경된 데이터가 없어 기존 데이터를 유지합니다.")
                else:
                    st.success(f"데이터셋이 업데이트되었습니다! ({old_count}개 → {new_count}개)")
                st.rerun()
        
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

    # 탭 메뉴
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 홈", "⭐ 즐겨찾기", "🧪 테스트", "📈 통계", "ℹ️ 정보"])

    with tab1:
        # 검색 박스
        search = st.text_input(
            "🔎 데이터셋 검색",
            placeholder="데이터셋 이름으로 검색",
            value=st.session_state.get('search', '')
        )
        st.session_state.search = search
        
        # 필터 적용
        filtered = filter_datasets(df, search_keyword=search)
        
        st.divider()
        
        # 데이터 내보내기 (한 줄로)
        col1, col2 = st.columns([2, 1])
        with col1:
            export_type = st.selectbox(
                "📥 내보내기 유형",
                ["전체 데이터셋", "필터링된 데이터셋"],
                label_visibility="collapsed"
            )
        with col2:
            if export_type == "전체 데이터셋":
                csv_data = get_csv_download(df)
                file_name = f"uci_ml_datasets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            else:
                csv_data = get_csv_download(filtered)
                file_name = f"uci_ml_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=file_name,
                mime="text/csv",
                width='stretch'
            )
        
        st.divider()

        # 테이블 뷰 렌더링
        st.subheader("📋 데이터셋 목록")
        render_table_view(filtered, fav_mgr=fav_mgr)

        st.divider()

        # 상세 보기
        if st.session_state.selected_dataset:
            selected_title = st.session_state.selected_dataset
            if selected_title in filtered['title'].values:
                row = filtered[filtered['title'] == selected_title].iloc[0]
                st.subheader(f"📄 상세 정보: {selected_title}")
                
                st.write("**기본 정보**")
                st.write(f"- **제목**: {row['title']}")
                
                # 링크
                url = row.get('url', '')
                if validate_url(url):
                    st.markdown(f"**🔗 [데이터셋 보기]({url})**")
                
                # Python import 코드
                python_code = row.get('python_import', '')
                if python_code:
                    st.write("**Python Import 코드:**")
                    st.code(python_code, language='python')
                
                # 즐겨찾기 버튼
                col_fav, col_close = st.columns([1, 3])
                with col_fav:
                    is_fav = fav_mgr.is_favorite(selected_title)
                    if st.button("⭐ 즐겨찾기 토글", width='stretch'):
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
        st.markdown("### ⭐ 즐겨찾기 데이터셋")
        
        # 즐겨찾기 검색 박스
        fav_search = st.text_input(
            "🔎 즐겨찾기 검색",
            placeholder="즐겨찾기된 데이터셋 검색",
            value=st.session_state.get('fav_search', '')
        )
        st.session_state.fav_search = fav_search
        
        if not favorites:
            st.info("즐겨찾기된 데이터셋이 없습니다.")
        else:
            fav_df = df[df['title'].isin(favorites)].reset_index(drop=True)
            
            # 즐겨찾기 검색 필터
            if fav_search:
                fav_df = fav_df[fav_df['title'].str.contains(fav_search, case=False, na=False)]
            
            if fav_df.empty:
                st.warning("검색 결과가 없습니다.")
            else:
                st.dataframe(fav_df, width='stretch', hide_index=True)
                
                # 즐겨찾기 CSV 내보내기
                csv_fav = get_csv_download(fav_df)
                st.download_button(
                    label="⭐ 즐겨찾기 CSV 다운로드",
                    data=csv_fav,
                    file_name=f"favorites_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )

    with tab3:
        st.subheader("🧪 데이터셋 테스트")
        
        # 데이터셋 선택
        dataset_options = df['title'].tolist()
        # Add warning emoji to unavailable datasets in dropdown
        dataset_options_with_warning = [f"{x} ⚠️" if x in st.session_state.unavailable_datasets else x for x in dataset_options]
        selected_dataset_with_warning = st.selectbox("테스트할 데이터셋 선택", dataset_options_with_warning)
        # Remove warning emoji for processing
        selected_dataset = selected_dataset_with_warning.replace(" ⚠️", "")
        
        if selected_dataset:
            dataset_row = df[df['title'] == selected_dataset].iloc[0]
            
            # Python import 코드 표시
            st.write("**Python Import 코드:**")
            st.code(dataset_row['python_import'], language='python')
            
            st.divider()
            
            # 데이터 로드 시도
            try:
                # ucimlrepo가 설치되어 있는지 확인
                import ucimlrepo
                
                # 데이터셋 ID 추출 (URL에서)
                dataset_id = dataset_row['url'].split('/')[-1]
                
                with st.spinner("데이터 로드 중..."):
                    # ucimlrepo의 올바른 사용법
                    dataset = ucimlrepo.fetch_ucirepo(id=int(dataset_id))
                    
                    # 데이터프레임 표시
                    st.subheader("📊 데이터프레임")
                    if hasattr(dataset, 'data') and hasattr(dataset.data, 'original'):
                        df_test = dataset.data.original
                        st.dataframe(df_test.head(10), width='stretch')
                        st.caption(f"총 {len(df_test)}개 행 중 처음 10개 표시")
                    elif hasattr(dataset, 'data') and hasattr(dataset.data, 'features'):
                        st.info("데이터 구조를 확인할 수 없습니다.")
                    else:
                        st.info("데이터를 로드할 수 없습니다.")
                    
                    # 간단한 그래프
                    st.subheader("📈 데이터 시각화")
                    if hasattr(dataset, 'data') and hasattr(dataset.data, 'original'):
                        df_test = dataset.data.original
                        numeric_cols = df_test.select_dtypes(include=['number']).columns.tolist()
                        
                        if numeric_cols:
                            col_to_plot = st.selectbox("그래프로 표시할 컬럼 선택", numeric_cols)
                            
                            # 데이터 특성 분석
                            col_data = df_test[col_to_plot].head(100)
                            unique_values = col_data.nunique()
                            value_range = col_data.max() - col_data.min()
                            
                            # 시각화 방법 결정
                            if unique_values <= 10:
                                # 범주형 데이터처럼 처리 - 막대 그래프
                                st.bar_chart(col_data.value_counts())
                                st.caption("범주형 데이터: 값 빈도수")
                            elif value_range == 0:
                                st.info("모든 값이 동일하여 시각화할 수 없습니다.")
                            elif col_data.std() == 0:
                                st.info("값의 변화가 없어 시각화할 수 없습니다.")
                            else:
                                # 연속형 데이터 - 라인 차트
                                st.line_chart(col_data)
                                st.caption("연속형 데이터: 값 추이")
                        else:
                            st.info("시각화할 수 있는 숫자형 컬럼이 없습니다.")
                    
            except Exception as e:
                error_msg = str(e)
                if "not available for import" in error_msg:
                    st.error("이 데이터셋은 현재 import 기능을 지원하지 않습니다. 다른 데이터셋을 선택해주세요.")
                    st.info("자세한 내용은 UCI ML Repository에서 확인하세요: https://archive.ics.uci.edu/datasets")
                    # Add to unavailable datasets
                    st.session_state.unavailable_datasets.add(selected_dataset)
                else:
                    st.error(f"데이터 로드 중 오류 발생: {e}")

    with tab4:
        st.subheader("📈 데이터셋 통계")
        
        stats = get_dataset_statistics(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📌 전체 데이터셋", stats.get("total_datasets", 0))
        with col2:
            st.metric("⏰ 마지막 업데이트", stats.get("last_updated", "-"))
        
        st.divider()
        
        # 데이터셋 이름 길이 분포 그래프
        st.subheader("데이터셋 이름 길이 분포")
        df['name_length'] = df['title'].str.len()
        length_dist = df['name_length'].value_counts().sort_index()
        
        if not length_dist.empty:
            st.bar_chart(length_dist, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with tab5:
        st.markdown("### ℹ️ 프로젝트 정보")
        
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
        - Requests
        
        **링크:**
        - [UCI ML Repository](https://archive.ics.uci.edu/)
        - [GitHub](https://github.com)
        """)


if __name__ == "__main__":
    main()
