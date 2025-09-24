# CORD-19 Data Analysis - Part 1: Data Loading and Basic Exploration
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

print("=== CORD-19 Dataset Analysis ===")
print("Part 1: Loading and Basic Exploration\n")

# Step 1: Load the data
# Note: Make sure you have downloaded metadata.csv from the CORD-19 dataset
try:
    # Load the metadata file
    df = pd.read_csv('data/metadata.csv')
    print("✅ Data loaded successfully!")
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    
except FileNotFoundError:
    print("❌ metadata.csv not found!")
    print("Please download the metadata.csv file from:")
    print("https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge")
    print("And place it in the same directory as this script.")
    exit()

# Step 2: Examine the first few rows
print("=== First 5 rows of the dataset ===")
print(df.head())
print("\n")

# Step 3: Check the data structure
print("=== Dataset Information ===")
print(f"Total rows: {df.shape[0]:,}")
print(f"Total columns: {df.shape[1]}")
print("\nColumn names:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")
print("\n")

# Step 4: Data types
print("=== Data Types ===")
print(df.dtypes)
print("\n")

# Step 5: Check for missing values
print("=== Missing Values Analysis ===")
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100

# Create a summary of missing values
missing_summary = pd.DataFrame({
    'Column': missing_data.index,
    'Missing_Count': missing_data.values,
    'Missing_Percentage': missing_percent.values
}).sort_values('Missing_Percentage', ascending=False)

print("Top 10 columns with most missing values:")
print(missing_summary.head(10))
print("\n")

# Step 6: Basic statistics for important text columns
print("=== Basic Statistics ===")
print("Non-null counts for key columns:")
key_columns = ['title', 'abstract', 'authors', 'journal', 'publish_time']
for col in key_columns:
    if col in df.columns:
        non_null_count = df[col].notna().sum()
        print(f"{col}: {non_null_count:,} ({non_null_count/len(df)*100:.1f}%)")

print("\n")

# Step 7: Preview some sample data
print("=== Sample Paper Titles ===")
if 'title' in df.columns:
    sample_titles = df['title'].dropna().head(10)
    for i, title in enumerate(sample_titles, 1):
        print(f"{i:2d}. {title}")

print("\n" + "="*50)
print("Part 1 Complete! ✅")
print("Next: Run Part 2 for Data Cleaning and Preparation")