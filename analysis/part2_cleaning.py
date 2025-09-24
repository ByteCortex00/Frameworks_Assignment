# CORD-19 Data Analysis - Part 2: Data Cleaning and Preparation
import pandas as pd
import numpy as np
from datetime import datetime
import re

print("=== CORD-19 Dataset Analysis ===")
print("Part 2: Data Cleaning and Preparation\n")

# Load the data (assuming Part 1 was run or data is already loaded)
try:
    df = pd.read_csv('data/metadata.csv')
    print(f"✅ Data loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
except:
    print("❌ Please ensure metadata.csv is available and Part 1 was completed")
    exit()

# Step 1: Identify columns with many missing values
print("\n=== Missing Data Analysis ===")
missing_threshold = 0.5  # 50% threshold
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100

high_missing = missing_percent[missing_percent > missing_threshold * 100]
print(f"Columns with more than {missing_threshold*100}% missing data:")
for col, pct in high_missing.items():
    print(f"  {col}: {pct:.1f}% missing")

# Step 2: Create a cleaned dataset
print("\n=== Creating Cleaned Dataset ===")

# Start with a copy of the original data
df_clean = df.copy()

# Remove rows where both title and abstract are missing (no useful content)
initial_rows = len(df_clean)
df_clean = df_clean.dropna(subset=['title', 'abstract'], how='all')
rows_after_cleanup = len(df_clean)
print(f"Removed {initial_rows - rows_after_cleanup:,} rows with no title or abstract")

# Fill missing titles with "Unknown Title"
df_clean['title'] = df_clean['title'].fillna('Unknown Title')

# Fill missing abstracts with empty string for processing
df_clean['abstract'] = df_clean['abstract'].fillna('')

print(f"Final cleaned dataset: {len(df_clean):,} rows")

# Step 3: Handle date columns
print("\n=== Processing Dates ===")
if 'publish_time' in df_clean.columns:
    # Convert publish_time to datetime
    try:
        df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')
        
        # Extract year from publication date
        df_clean['publish_year'] = df_clean['publish_time'].dt.year
        
        # Remove obviously incorrect years (before 1900 or future years)
        current_year = datetime.now().year
        df_clean = df_clean[
            (df_clean['publish_year'] >= 1900) & 
            (df_clean['publish_year'] <= current_year)
        ]
        
        valid_dates = df_clean['publish_time'].notna().sum()
        print(f"✅ Processed dates successfully")
        print(f"Papers with valid publication dates: {valid_dates:,}")
        print(f"Date range: {df_clean['publish_year'].min():.0f} - {df_clean['publish_year'].max():.0f}")
        
    except Exception as e:
        print(f"❌ Error processing dates: {e}")

# Step 4: Create new useful columns
print("\n=== Creating New Features ===")

# Abstract word count
df_clean['abstract_word_count'] = df_clean['abstract'].apply(
    lambda x: len(str(x).split()) if pd.notna(x) else 0
)

# Title word count
df_clean['title_word_count'] = df_clean['title'].apply(
    lambda x: len(str(x).split()) if pd.notna(x) else 0
)

# Has abstract flag
df_clean['has_abstract'] = df_clean['abstract_word_count'] > 0

# Simple author count (counting semicolons and commas as separators)
def count_authors(author_string):
    if pd.isna(author_string) or author_string == '':
        return 0
    # Count both semicolons and commas as author separators
    separators = author_string.count(';') + author_string.count(',')
    return max(1, separators + 1)  # At least 1 author if string exists

df_clean['author_count'] = df_clean['authors'].apply(count_authors)

print("New columns created:")
print(f"  - abstract_word_count: avg {df_clean['abstract_word_count'].mean():.1f} words")
print(f"  - title_word_count: avg {df_clean['title_word_count'].mean():.1f} words") 
print(f"  - has_abstract: {df_clean['has_abstract'].sum():,} papers have abstracts")
print(f"  - author_count: avg {df_clean['author_count'].mean():.1f} authors per paper")

# Step 5: Summary of cleaned data
print("\n=== Cleaned Dataset Summary ===")
print(f"Final dataset dimensions: {df_clean.shape}")
print(f"Papers with titles: {df_clean['title'].notna().sum():,}")
print(f"Papers with abstracts: {(df_clean['abstract_word_count'] > 0).sum():,}")
print(f"Papers with valid dates: {df_clean['publish_time'].notna().sum():,}")
print(f"Papers with journal info: {df_clean['journal'].notna().sum():,}")

# Save cleaned dataset
try:
    df_clean.to_csv('data/metadata_cleaned.csv', index=False)
    print(f"✅ Cleaned dataset saved as 'metadata_cleaned.csv'")
except Exception as e:
    print(f"⚠️  Could not save cleaned dataset: {e}")

# Quick preview of the cleaned data
print("\n=== Sample of Cleaned Data ===")
sample_cols = ['title', 'abstract_word_count', 'title_word_count', 'publish_year', 'author_count']
available_cols = [col for col in sample_cols if col in df_clean.columns]
print(df_clean[available_cols].head())

print("\n" + "="*50)
print("Part 2 Complete! ✅")
print("Next: Run Part 3 for Data Analysis and Visualization")

# Make cleaned data available for next parts
print(f"\nCleaned dataset ready with {len(df_clean):,} papers")