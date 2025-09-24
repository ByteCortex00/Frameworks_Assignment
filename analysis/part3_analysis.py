# CORD-19 Data Analysis - Part 3: Data Analysis and Visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

print("=== CORD-19 Dataset Analysis ===")
print("Part 3: Data Analysis and Visualization\n")

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

# Load cleaned data
try:
    df_clean = pd.read_csv('data/metadata_cleaned.csv')
    print(f"✅ Loaded cleaned data: {df_clean.shape[0]:,} papers")
except:
    # If cleaned file doesn't exist, load and clean the original
    print("Loading and cleaning original data...")
    df = pd.read_csv('data/metadata.csv')
    df_clean = df.copy()
    df_clean = df_clean.dropna(subset=['title', 'abstract'], how='all')
    df_clean['title'] = df_clean['title'].fillna('Unknown Title')
    df_clean['abstract'] = df_clean['abstract'].fillna('')
    df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')
    df_clean['publish_year'] = df_clean['publish_time'].dt.year
    df_clean = df_clean[(df_clean['publish_year'] >= 1900) & (df_clean['publish_year'] <= 2024)]
    print(f"✅ Cleaned data on-the-fly: {df_clean.shape[0]:,} papers")

# Create output directory for plots
import os
os.makedirs('plots', exist_ok=True)

print("\n=== Analysis 1: Publications Over Time ===")

# Filter for reasonable years and COVID-era focus
covid_years = df_clean[df_clean['publish_year'] >= 2015].copy()
year_counts = covid_years['publish_year'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
bars = plt.bar(year_counts.index, year_counts.values, color='steelblue', alpha=0.7)
plt.title('COVID-19 Research Papers by Publication Year', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number of Papers', fontsize=12)
plt.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 50,
             f'{int(height):,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('plots/publications_by_year.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"Peak year: {year_counts.idxmax()} with {year_counts.max():,} papers")

print("\n=== Analysis 2: Top Publishing Journals ===")

# Analyze top journals
journal_counts = df_clean['journal'].value_counts().head(15)
print("Top 15 journals publishing COVID-19 research:")
for i, (journal, count) in enumerate(journal_counts.items(), 1):
    print(f"{i:2d}. {journal}: {count:,} papers")

# Plot top journals
plt.figure(figsize=(14, 8))
bars = plt.barh(range(len(journal_counts)), journal_counts.values, color='coral', alpha=0.7)
plt.yticks(range(len(journal_counts)), [j[:50] + '...' if len(j) > 50 else j for j in journal_counts.index])
plt.xlabel('Number of Papers', fontsize=12)
plt.title('Top 15 Journals Publishing COVID-19 Research', fontsize=16, fontweight='bold')
plt.grid(axis='x', alpha=0.3)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 10, bar.get_y() + bar.get_height()/2,
             f'{int(width):,}', ha='left', va='center')

plt.tight_layout()
plt.savefig('plots/top_journals.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n=== Analysis 3: Word Frequency in Titles ===")

# Extract and analyze title words
def clean_title_text(text):
    """Clean and prepare text for word frequency analysis"""
    if pd.isna(text):
        return ""
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot'}
    words = [word for word in text.split() if len(word) > 2 and word not in stop_words]
    return ' '.join(words)

# Get all title words
all_titles = ' '.join(df_clean['title'].apply(clean_title_text))
word_freq = Counter(all_titles.split())

# Get top words
top_words = dict(word_freq.most_common(20))
print("Top 20 words in paper titles:")
for i, (word, count) in enumerate(top_words.items(), 1):
    print(f"{i:2d}. '{word}': {count:,} times")

# Plot word frequency
plt.figure(figsize=(14, 8))
words, counts = zip(*list(top_words.items()))
bars = plt.bar(words, counts, color='lightgreen', alpha=0.7)
plt.title('Most Frequent Words in Paper Titles (Top 20)', fontsize=16, fontweight='bold')
plt.xlabel('Words', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 20,
             f'{int(height):,}', ha='center', va='bottom', rotation=90)

plt.tight_layout()
plt.savefig('plots/word_frequency.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n=== Analysis 4: Word Cloud of Titles ===")

# Create word cloud
try:
    wordcloud = WordCloud(width=800, height=400, 
                         background_color='white',
                         max_words=100,
                         colormap='viridis').generate(all_titles)
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Paper Titles', fontsize=20, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('plots/title_wordcloud.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Word cloud created successfully!")
    
except ImportError:
    print("⚠️  WordCloud not installed. Run: pip install wordcloud")
except Exception as e:
    print(f"⚠️  Could not create word cloud: {e}")

print("\n=== Analysis 5: Paper Characteristics ===")

# Abstract length analysis
if 'abstract_word_count' in df_clean.columns:
    abstract_stats = df_clean['abstract_word_count'].describe()
    print("Abstract length statistics:")
    print(f"  Average: {abstract_stats['mean']:.1f} words")
    print(f"  Median: {abstract_stats['50%']:.1f} words")
    print(f"  Max: {abstract_stats['max']:.0f} words")
    
    plt.figure(figsize=(12, 6))
    # Remove outliers for better visualization
    q99 = df_clean['abstract_word_count'].quantile(0.99)
    filtered_abstracts = df_clean[df_clean['abstract_word_count'] <= q99]['abstract_word_count']
    
    plt.hist(filtered_abstracts, bins=50, color='skyblue', alpha=0.7, edgecolor='black')
    plt.title('Distribution of Abstract Lengths (99th percentile)', fontsize=16, fontweight='bold')
    plt.xlabel('Abstract Word Count', fontsize=12)
    plt.ylabel('Number of Papers', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('plots/abstract_length_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

print("\n=== Analysis 6: Source Distribution ===")

# Analyze paper sources
if 'source_x' in df_clean.columns:
    source_col = 'source_x'
elif 'source' in df_clean.columns:
    source_col = 'source'
else:
    source_col = None

if source_col:
    source_counts = df_clean[source_col].value_counts().head(10)
    print(f"Top 10 sources:")
    for i, (source, count) in enumerate(source_counts.items(), 1):
        print(f"{i:2d}. {source}: {count:,} papers")
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(source_counts)), source_counts.values, color='orange', alpha=0.7)
    plt.xticks(range(len(source_counts)), source_counts.index, rotation=45, ha='right')
    plt.title('Papers by Source Database', fontsize=16, fontweight='bold')
    plt.ylabel('Number of Papers', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                 f'{int(height):,}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('plots/source_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
else:
    print("No source column found in the dataset")

print("\n=== Summary of Key Findings ===")
print(f"📊 Total papers analyzed: {len(df_clean):,}")
print(f"📅 Publication years: {df_clean['publish_year'].min():.0f} - {df_clean['publish_year'].max():.0f}")
print(f"📰 Top journal: {journal_counts.index[0]} ({journal_counts.iloc[0]:,} papers)")
print(f"📈 Peak publication year: {year_counts.idxmax()} ({year_counts.max():,} papers)")
print(f"🔤 Most common title word: '{list(top_words.keys())[0]}' ({list(top_words.values())[0]:,} times)")

print("\n" + "="*60)
print("Part 3 Complete! ✅")
print("All visualizations saved in 'plots/' directory")
print("Next: Create the Streamlit application (Part 4)")
print("="*60)