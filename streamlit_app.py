import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="CORD-19 Research Explorer",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #666666;
    margin-bottom: 1rem;
}
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the dataset"""
    try:
        # Try to load cleaned data first
        df = pd.read_csv('data/metadata_cleaned.csv')
        st.success("✅ Loaded cleaned dataset")
    except:
        try:
            # Load original data and clean it
            df = pd.read_csv('metadata.csv')
            df = df.dropna(subset=['title', 'abstract'], how='all')
            df['title'] = df['title'].fillna('Unknown Title')
            df['abstract'] = df['abstract'].fillna('')
            df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
            df['publish_year'] = df['publish_time'].dt.year
            df = df[(df['publish_year'] >= 1900) & (df['publish_year'] <= datetime.now().year)]
            
            # Create additional features
            df['abstract_word_count'] = df['abstract'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
            df['title_word_count'] = df['title'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
            df['has_abstract'] = df['abstract_word_count'] > 0
            
            st.success("✅ Loaded and cleaned original dataset")
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.stop()
    
    return df

def clean_text_for_wordfreq(text):
    """Clean text for word frequency analysis"""
    if pd.isna(text):
        return ""
    text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = [word for word in text.split() if len(word) > 2 and word not in stop_words]
    return ' '.join(words)

def main():
    # Header
    st.markdown('<h1 class="main-header">🦠 CORD-19 Research Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Analysis of COVID-19 Research Papers</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("📊 Data Filters")
    
    # Year range filter
    if 'publish_year' in df.columns:
        min_year = int(df['publish_year'].min())
        max_year = int(df['publish_year'].max())
        year_range = st.sidebar.slider(
            "Select Year Range",
            min_year, max_year,
            (max(2015, min_year), max_year),
            help="Filter papers by publication year"
        )
        df_filtered = df[df['publish_year'].between(year_range[0], year_range[1])]
    else:
        df_filtered = df
        st.sidebar.warning("No date information available")
    
    # Journal filter
    if 'journal' in df.columns:
        top_journals = df['journal'].value_counts().head(20).index.tolist()
        selected_journals = st.sidebar.multiselect(
            "Select Journals (optional)",
            options=top_journals,
            help="Leave empty to include all journals"
        )
        if selected_journals:
            df_filtered = df_filtered[df_filtered['journal'].isin(selected_journals)]
    
    # Abstract filter
    if 'has_abstract' in df_filtered.columns:
        include_no_abstract = st.sidebar.checkbox(
            "Include papers without abstracts",
            value=True,
            help="Uncheck to show only papers with abstracts"
        )
        if not include_no_abstract:
            df_filtered = df_filtered[df_filtered['has_abstract'] == True]
    
    # Display key metrics
    st.subheader("📈 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Papers", f"{len(df_filtered):,}")
    
    with col2:
        if 'has_abstract' in df_filtered.columns:
            papers_with_abstracts = df_filtered['has_abstract'].sum()
            st.metric("Papers with Abstracts", f"{papers_with_abstracts:,}")
        else:
            st.metric("Papers with Abstracts", "N/A")
    
    with col3:
        if 'journal' in df_filtered.columns:
            unique_journals = df_filtered['journal'].nunique()
            st.metric("Unique Journals", f"{unique_journals:,}")
        else:
            st.metric("Unique Journals", "N/A")
    
    with col4:
        if 'publish_year' in df_filtered.columns:
            year_span = df_filtered['publish_year'].max() - df_filtered['publish_year'].min() + 1
            st.metric("Year Span", f"{int(year_span)} years")
        else:
            st.metric("Year Span", "N/A")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Timeline Analysis", 
        "📰 Journal Analysis", 
        "🔤 Word Analysis", 
        "📄 Paper Characteristics",
        "🔍 Data Explorer"
    ])
    
    with tab1:
        st.subheader("Publications Over Time")
        
        if 'publish_year' in df_filtered.columns:
            year_counts = df_filtered['publish_year'].value_counts().sort_index()
            
            # Interactive plotly chart
            fig = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                title="Number of Publications by Year",
                labels={'x': 'Year', 'y': 'Number of Papers'},
                color=year_counts.values,
                color_continuous_scale='viridis'
            )
            fig.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show peak year
            peak_year = year_counts.idxmax()
            peak_count = year_counts.max()
            st.info(f"🎯 Peak publication year: **{peak_year}** with **{peak_count:,}** papers")
            
            # Year-over-year growth
            st.subheader("Year-over-Year Growth")
            yoy_growth = year_counts.pct_change() * 100
            fig2 = px.line(
                x=yoy_growth.index,
                y=yoy_growth.values,
                title="Year-over-Year Growth Rate (%)",
                labels={'x': 'Year', 'y': 'Growth Rate (%)'}
            )
            fig2.update_traces(line_color='red')
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No publication date information available")
    
    with tab2:
        st.subheader("Journal Analysis")
        
        if 'journal' in df_filtered.columns:
            # Top journals
            n_journals = st.slider("Number of top journals to display", 5, 30, 15)
            journal_counts = df_filtered['journal'].value_counts().head(n_journals)
            
            # Horizontal bar chart
            fig = px.bar(
                x=journal_counts.values,
                y=journal_counts.index,
                orientation='h',
                title=f"Top {n_journals} Journals by Number of Publications",
                labels={'x': 'Number of Papers', 'y': 'Journal'}
            )
            fig.update_layout(height=max(400, n_journals * 25))
            st.plotly_chart(fig, use_container_width=True)
            
            # Journal statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Most Productive Journal", journal_counts.index[0])
                st.metric("Papers from Top Journal", f"{journal_counts.iloc[0]:,}")
            with col2:
                st.metric("Total Unique Journals", f"{len(journal_counts):,}")
                avg_papers = journal_counts.mean()
                st.metric("Average Papers per Journal", f"{avg_papers:.1f}")
        else:
            st.warning("No journal information available")
    
    with tab3:
        st.subheader("Word Frequency Analysis")
        
        # Word frequency in titles
        if 'title' in df_filtered.columns:
            st.write("**Most Common Words in Paper Titles**")
            
            # Clean and analyze titles
            all_titles = ' '.join(df_filtered['title'].apply(clean_text_for_wordfreq))
            word_freq = Counter(all_titles.split())
            
            # Number of words to show
            n_words = st.slider("Number of top words to display", 10, 50, 20)
            top_words = dict(word_freq.most_common(n_words))
            
            # Create bar chart
            fig = px.bar(
                x=list(top_words.values()),
                y=list(top_words.keys()),
                orientation='h',
                title=f"Top {n_words} Words in Paper Titles",
                labels={'x': 'Frequency', 'y': 'Words'},
                color=list(top_words.values()),
                color_continuous_scale='plasma'
            )
            fig.update_layout(height=max(500, n_words * 20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Word statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Most Common Word", f'"{list(top_words.keys())[0]}"')
            with col2:
                st.metric("Frequency", f"{list(top_words.values())[0]:,}")
            with col3:
                st.metric("Unique Words", f"{len(word_freq):,}")
        else:
            st.warning("No title information available")
    
    with tab4:
        st.subheader("Paper Characteristics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Abstract length analysis
            if 'abstract_word_count' in df_filtered.columns:
                st.write("**Abstract Length Distribution**")
                
                # Remove extreme outliers for better visualization
                q99 = df_filtered['abstract_word_count'].quantile(0.99)
                filtered_abstracts = df_filtered[df_filtered['abstract_word_count'] <= q99]['abstract_word_count']
                
                fig = px.histogram(
                    filtered_abstracts,
                    nbins=30,
                    title="Distribution of Abstract Lengths (99th percentile)",
                    labels={'value': 'Abstract Word Count', 'count': 'Number of Papers'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                mean_length = df_filtered['abstract_word_count'].mean()
                median_length = df_filtered['abstract_word_count'].median()
                st.write(f"Average: **{mean_length:.1f}** words")
                st.write(f"Median: **{median_length:.1f}** words")
        
        with col2:
            # Title length analysis
            if 'title_word_count' in df_filtered.columns:
                st.write("**Title Length Distribution**")
                
                fig = px.histogram(
                    df_filtered['title_word_count'],
                    nbins=20,
                    title="Distribution of Title Lengths",
                    labels={'value': 'Title Word Count', 'count': 'Number of Papers'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                mean_title_length = df_filtered['title_word_count'].mean()
                median_title_length = df_filtered['title_word_count'].median()
                st.write(f"Average: **{mean_title_length:.1f}** words")
                st.write(f"Median: **{median_title_length:.1f}** words")
    
    with tab5:
        st.subheader("Data Explorer")
        st.write("Browse the actual research papers in your filtered dataset:")
        
        # Search functionality
        search_term = st.text_input("🔍 Search in titles:", placeholder="Enter keywords...")
        
        # Apply search filter
        display_df = df_filtered.copy()
        if search_term:
            mask = display_df['title'].str.contains(search_term, case=False, na=False)
            display_df = display_df[mask]
            st.info(f"Found {len(display_df):,} papers matching '{search_term}'")
        
        # Select columns to display
        available_cols = ['title', 'authors', 'journal', 'publish_year', 'abstract_word_count']
        display_cols = [col for col in available_cols if col in display_df.columns]
        
        if display_cols:
            # Show sample of papers
            n_papers = st.slider("Number of papers to display", 10, 100, 20)
            st.dataframe(
                display_df[display_cols].head(n_papers),
                use_container_width=True,
                height=400
            )
            
            # Download filtered data
            if st.button("📥 Download Filtered Data as CSV"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"cord19_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No displayable columns available")
    
    # Footer
    st.markdown("---")
    st.markdown("### About this Dashboard")
    st.markdown("""
    Analyzes the CORD-19 dataset of COVID-19 research papers. 
    Use the filters in the sidebar to explore different subsets of the data, and navigate 
    through the tabs to discover insights about publication trends, journal preferences, 
    and research characteristics.
    
    **Data Source**: [CORD-19 Dataset](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge)
    """)

if __name__ == "__main__":
    main()