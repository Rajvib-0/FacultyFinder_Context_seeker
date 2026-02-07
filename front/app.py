import streamlit as st
import os
import traceback
import time
import pandas as pd

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="FacultyFinder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SEARCH ENGINE INIT ====================

@st.cache_resource
def get_search_engine():
    try:
        from search_engine_improved import EnhancedFacultySearchEngine

        data_file = "faculty_data.csv"
        if not os.path.exists(data_file):
            st.error(f"Data file not found: {data_file}")
            return None

        with st.spinner("🔄 Initializing search engine..."):
            engine = EnhancedFacultySearchEngine(data_file)
            engine.initialize(force_rebuild=False, use_multi_field=True)

        return engine

    except Exception as e:
        st.error(f"❌ Error loading search engine: {e}")
        traceback.print_exc()
        return None


# ==================== PAGES ====================

def home_page():
    st.title("🔍 FacultyFinder")
    st.markdown("### Find the right faculty for your research")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🎯 **Smart Search**\n\nAI-powered semantic matching")
    with c2:
        st.info("📚 **Research Focused**\n\nSearch by specialization & interests")
    with c3:
        st.info("⚡ **Fast Results**\n\nOptimized semantic search")

    st.markdown("---")
    st.markdown("Use **Search** from the sidebar to begin.")


def search_page():
    st.title("🔎 Faculty Search")

    engine = get_search_engine()
    if not engine:
        st.error("Search engine failed to initialize.")
        return

    st.success("✅ Search engine ready")

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="machine learning, NLP, data science...",
            label_visibility="collapsed"
        )
    with col2:
        top_k = st.number_input("Max Results", min_value=1, max_value=50, value=10)

    with st.expander("⚙️ Advanced Options"):
        use_hybrid = st.checkbox("Use Hybrid Search", value=True)

    if st.button("🔍 Search Faculty", type="primary", use_container_width=True):

        if not query.strip():
            st.warning("⚠️ Please enter a search query")
            return

        with st.spinner("Searching faculty..."):
            start = time.time()
            results = engine.search(query, top_k=top_k, use_hybrid=use_hybrid)
            elapsed = time.time() - start

        # ---------- SCORE NORMALIZATION (FIX) ----------
        for r in results:
            r["score"] = (
                r.get("score")
                or r.get("final_score")
                or r.get("hybrid_score")
                or r.get("semantic_score")
                or 0.0
            )
        # ---------------------------------------------

        st.markdown("---")
        st.markdown(f"### 📊 Results Found: {len(results)}")
        st.metric("Search Time", f"{elapsed:.3f}s")

        if not results:
            st.warning("No matching faculty found.")
            return

        for i, r in enumerate(results, 1):
            with st.expander(
                f"#{i} - {r.get('name', 'N/A')} | Score: {r['score']:.3f}",
                expanded=(i == 1)
            ):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.markdown(f"**Name:** {r.get('name', 'N/A')}")
                    st.markdown(f"**Area of Specialization:** {r.get('areaSpecialization', 'N/A')}")
                    st.markdown(f"**Email:** {r.get('email', 'N/A')}")
                    st.markdown(f"**Address:** {r.get('address', 'N/A')}")

                with col_b:
                    st.metric("Match Score", f"{r['score']:.3f}")

        # ---------- DOWNLOAD ----------
        st.markdown("---")
        df = pd.DataFrame(results)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=df.to_csv(index=False),
            file_name=f"faculty_search_{query[:20]}.csv",
            mime="text/csv"
        )
# ==================== MAIN ====================

def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("", ["Home", "Search", "About"])

    st.sidebar.markdown("---")
    engine = get_search_engine()
    if engine:
        st.sidebar.success("✅ Search Engine Ready")
    else:
        st.sidebar.error("❌ Search Engine Not Available")

    if page == "Home":
        home_page()
    elif page == "Search":
        search_page()
    elif page == "About":
        about_page()


if __name__ == "__main__":
    main()
