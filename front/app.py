

import streamlit as st
import os
import sys
import traceback
import time
import pandas as pd

# Configure page
st.set_page_config(
    page_title="FacultyFinder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INITIALIZATION ====================

@st.cache_resource
def get_search_engine():
    """
    Initialize search engine (cached to avoid reloading)
    This replaces the Flask lazy loading pattern
    """
    try:
        # Import here to avoid loading unless needed
        from search_engine_improved import EnhancedFacultySearchEngine
        
        data_file = 'faculty_data.csv'
        if not os.path.exists(data_file):
            st.error(f"Data file not found: {data_file}")
            return None
        
        with st.spinner("🔄 Initializing search engine..."):
            print("Initializing search engine...")
            search_engine = EnhancedFacultySearchEngine(data_file)
            search_engine.initialize(force_rebuild=False, use_multi_field=True)
            print("Search engine initialized!")
        
        return search_engine
        
    except Exception as e:
        st.error(f" Error loading search engine: {e}")
        traceback.print_exc()
        return None


@st.cache_data
def get_statistics(_search_engine):
    """
    Get search engine statistics
    Note: _search_engine with underscore tells Streamlit not to hash this parameter
    """
    if _search_engine:
        return _search_engine.get_statistics()
    return {}


# ==================== PAGES ====================

def home_page():
    """Main landing page"""
    st.title("🔍 FacultyFinder")
    st.markdown("### Find the right faculty for your research")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🎯 **Smart Search**\n\nUse AI-powered semantic search to find faculty")
    
    with col2:
        st.info("📚 **Research Matching**\n\nMatch based on research interests and expertise")
    
    with col3:
        st.info("⚡ **Fast Results**\n\nGet relevant results in milliseconds")
    
    st.markdown("---")
    st.markdown("###  Get Started")
    st.markdown("Click **Search** in the sidebar to begin finding faculty members!")
    
    # Show some stats
    search_engine = get_search_engine()
    if search_engine:
        stats = get_statistics(search_engine)
        
        st.markdown("### Database Statistics")
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.metric("Total Faculty", stats.get('total_faculty', 'N/A'))
        with stat_cols[1]:
            st.metric("Departments", stats.get('total_departments', 'N/A'))
        with stat_cols[2]:
            st.metric("Research Areas", stats.get('total_research_areas', 'N/A'))
        with stat_cols[3]:
            st.metric("Search Ready", "✅" if search_engine else "❌")


def search_page():
    """Search interface page"""
    st.title("🔎 Faculty Search")
    
    # Initialize search engine
    search_engine = get_search_engine()
    
    if not search_engine:
        st.error(" Search engine not initialized. Please check the logs.")
        st.info(" Make sure `faculty_data.csv` and `search_engine_improved.py` are present.")
        return
    
    st.success("Search engine ready!")
    
    # Search form
    st.markdown("### Enter your search query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., machine learning, natural language processing, computer vision...",
            help="Enter keywords, research topics, or expertise areas",
            label_visibility="collapsed"
        )
    
    with col2:
        top_k = st.number_input(
            "Max Results",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )
    
    # Advanced options
    with st.expander(" Advanced Options"):
        use_hybrid = st.checkbox(
            "Use Hybrid Search",
            value=True,
            help="Combine semantic and keyword-based search for better results"
        )
    
    # Search button
    search_button = st.button(" Search Faculty", type="primary", use_container_width=True)
    
    # Perform search
    if search_button or (query and len(query) > 0):
        if not query or len(query.strip()) == 0:
            st.warning("⚠️ Please enter a search query")
        else:
            with st.spinner("🔍 Searching..."):
                try:
                    start_time = time.time()
                    results = search_engine.search(
                        query,
                        top_k=top_k,
                        use_hybrid=use_hybrid
                    )
                    search_time = time.time() - start_time
                    
                    # Display results
                    st.markdown("---")
                    
                    # Results header
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"### 📊 Search Results ({len(results)} found)")
                    with col_b:
                        st.metric("Search Time", f"{search_time:.3f}s")
                    
                    if not results:
                        st.warning("No results found. Try different keywords.")
                    else:
                        # Display each result
                        for idx, result in enumerate(results, 1):
                            with st.expander(
                                f"#{idx} - {result.get('name', 'Unknown')} "
                                f"({result.get('department', 'N/A')}) - "
                                f"Score: {result.get('score', 0):.3f}",
                                expanded=(idx == 1)
                            ):
                                result_col1, result_col2 = st.columns([3, 1])
                                
                                with result_col1:
                                    # Basic info
                                    st.markdown(f"**Name:** {result.get('name', 'N/A')}")
                                    st.markdown(f"**Department:** {result.get('department', 'N/A')}")
                                    st.markdown(f"**Email:** {result.get('email', 'N/A')}")
                                    
                                    # Research interests
                                    if result.get('research_interests'):
                                        st.markdown("**Research Interests:**")
                                        st.write(result['research_interests'])
                                    
                                    # Additional fields
                                    if result.get('expertise'):
                                        st.markdown("**Expertise:**")
                                        st.write(result['expertise'])
                                    
                                    # Profile URL
                                    if result.get('profile_url'):
                                        st.markdown(f"[🔗 View Profile]({result['profile_url']})")
                                
                                with result_col2:
                                    # Score and metrics
                                    st.metric("Match Score", f"{result.get('score', 0):.3f}")
                                    
                                    if result.get('publications'):
                                        st.metric("Publications", result['publications'])
                                    
                                    # Contact button
                                    if result.get('email'):
                                        email = result['email']
                                        st.markdown(
                                            f"[📧 Email]"
                                            f"(mailto:{email}?subject=Research Inquiry from FacultyFinder)"
                                        )
                    
                    # Download results as CSV
                    if results:
                        st.markdown("---")
                        df = pd.DataFrame(results)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv,
                            file_name=f"faculty_search_results_{query[:30]}.csv",
                            mime="text/csv"
                        )
                
                except Exception as e:
                    st.error(f"❌ Search error: {str(e)}")
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())


def about_page():
    """About page"""
    st.title("ℹ️ About FacultyFinder")
    
    st.markdown("""
    ### What is FacultyFinder?
    
    FacultyFinder is an AI-powered search engine designed to help students, researchers, 
    and collaborators find the right faculty members based on research interests and expertise.
    
    ### Features
    
    - 🎯 **Semantic Search**: Uses advanced NLP to understand the meaning of your query
    - 🔍 **Hybrid Search**: Combines semantic and keyword-based approaches
    - ⚡ **Fast Results**: Get relevant matches in milliseconds
    - 📊 **Rich Profiles**: View detailed faculty information and research interests
    - 📧 **Direct Contact**: Easy access to faculty contact information
    
    ### How It Works
    
    1. **Enter Your Query**: Describe your research interests or expertise area
    2. **AI Processing**: Our system uses sentence transformers to understand semantics
    3. **Smart Matching**: Hybrid search combines multiple ranking signals
    4. **Ranked Results**: Get the most relevant faculty members ranked by relevance
    
    ### Technology Stack
    
    - **Frontend**: Streamlit
    - **Search Engine**: Custom enhanced search with multi-field indexing
    - **AI/ML**: Sentence Transformers for semantic embeddings
    - **Hosting**: Hugging Face Spaces
    """)
    
    # Display statistics
    search_engine = get_search_engine()
    if search_engine:
        stats = get_statistics(search_engine)
        
        st.markdown("### 📊 Database Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Faculty", stats.get('total_faculty', 'N/A'))
        
        with col2:
            st.metric("Departments", stats.get('total_departments', 'N/A'))
        
        with col3:
            st.metric("Research Areas", stats.get('total_research_areas', 'N/A'))
        
        # Additional stats if available
        if stats.get('index_ready'):
            st.success("✅ Search index is ready and optimized")
        
        st.markdown("---")
    
    st.markdown("""
    ### Contact
    
    Found a bug or have suggestions? Please let me know!
    
    - 📧 Email: rajvibujad@gmail.com
    """)


# ==================== MAIN APP ====================

def main():
    """Main application"""
    
    # Sidebar navigation
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "🔎 Search"],
        label_visibility="collapsed"
    )
    
    # Add some info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Tips")
    st.sidebar.info(
        "- Be specific with your search terms\n"
        "- Use research keywords, not just field names\n"
        "- Try hybrid search for better results"
    )
    
    # Health check indicator
    st.sidebar.markdown("---")
    search_engine = get_search_engine()
    if search_engine:
        st.sidebar.success("✅ Search Engine: Ready")
    else:
        st.sidebar.error("❌ Search Engine: Not Available")
    
    # Route to appropriate page
    if page == "🏠 Home":
        home_page()
    elif page == "🔎 Search":
        search_page()


# ==================== RUN APP ====================

if __name__ == "__main__":
    # Print startup message
    print("\n" + "="*80)
    print("FacultyFinder Streamlit Application Starting")
    print("Search engine will load on first access")
    print("="*80 + "\n")
    
    # Run the app
    main()
