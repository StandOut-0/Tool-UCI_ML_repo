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


def main():
    st.set_page_config(page_title="UCI ML Datasets", layout="wide")
    st.title("UCI ML Dataset Explorer — MVP")

    # Sidebar controls
    st.sidebar.header("Controls")
    search = st.sidebar.text_input("Search (title or tasks)")
    min_instances = st.sidebar.number_input("Min instances", min_value=0, value=0, step=1)
    df = load_data()
    task_types = ["All"] + get_task_types(df)
    task = st.sidebar.selectbox("Task filter", task_types)

    if st.sidebar.button("Refresh (crawl)"):
        with st.spinner("Running scraper..."):
            scrape_uci_datasets(save_path="data/datasets.csv")
            # clear cache and reload
            load_data.clear()
            df = load_data()
            st.success("Refreshed")

    # Favorites manager
    fav_mgr = FavoritesManager(filepath="cache/favorites.json")

    # Apply filters
    filtered = filter_datasets(df, search_keyword=search, min_instances=min_instances, task_filter=task)

    # Stats
    stats = get_dataset_statistics(filtered)
    col1, col2, col3 = st.columns(3)
    col1.metric("Datasets", stats.get("total_datasets", 0))
    col2.metric("Total Instances", stats.get("total_instances", 0))
    col3.metric("Last Updated", stats.get("last_updated", "-"))

    st.subheader("Datasets")
    st.dataframe(filtered)

    st.subheader("Dataset Actions")
    sel = st.selectbox("Select dataset", options=filtered['title'].tolist() if not filtered.empty else [])
    if sel:
        row = filtered[filtered['title'] == sel].iloc[0]
        st.write(row.to_dict())
        if st.button("Toggle Favorite"):
            if fav_mgr.is_favorite(sel):
                fav_mgr.remove_favorite(sel)
                st.info(f"Removed {sel} from favorites")
            else:
                fav_mgr.add_favorite(sel)
                st.success(f"Added {sel} to favorites")

    st.sidebar.subheader("Favorites")
    for f in fav_mgr.get_favorites():
        st.sidebar.write(f)


if __name__ == "__main__":
    main()
