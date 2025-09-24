# requirements.txt file content:
"""
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
streamlit>=1.28.0
plotly>=5.0.0
wordcloud>=1.8.0
numpy>=1.21.0
"""

# run_analysis.py - Complete pipeline runner
import os
import sys
import subprocess
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = ['data', 'analysis', 'plots']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created")

def check_dataset():
    """Check if dataset exists"""
    if not Path('metadata.csv').exists() and not Path('data/metadata.csv').exists():
        print("❌ Dataset not found!")
        print("Please download metadata.csv from:")
        print("https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge")
        print("And place it in the current directory or data/ folder")
        return False
    return True

def run_analysis_pipeline():
    """Run the complete analysis pipeline"""
    print("🚀 Starting CORD-19 Analysis Pipeline...")
    
    setup_directories()
    
    if not check_dataset():
        return
    
    scripts = [
        ("Part 1: Data Exploration", "part1_exploration.py"),
        ("Part 2: Data Cleaning", "part2_cleaning.py"), 
        ("Part 3: Analysis & Visualization", "part3_analysis.py")
    ]
    
    for name, script in scripts:
        print(f"\n📊 Running {name}...")
        try:
            exec(open(script).read())
            print(f"✅ {name} completed successfully")
        except FileNotFoundError:
            print(f"⚠️  {script} not found - please ensure all parts are available")
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    
    print("\n🎉 Analysis pipeline completed!")
    print("📁 Check the 'plots/' folder for visualizations")
    print("🚀 Run the dashboard: streamlit run streamlit_app.py")

if __name__ == "__main__":
    run_analysis_pipeline()