#!/usr/bin/env python3
"""
Quick test script - analyze just 20 posts to verify OCR pipeline works
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from october_content_quality_analysis import ContentQualityAnalyzer

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     🧪 OCR TEST - 20 Posts Only                               ║
╚════════════════════════════════════════════════════════════════╝
    """)

    database_path = Path(__file__).parent.parent / "MASTER_TIKTOK_DATABASE.csv"
    output_dir = Path(__file__).parent.parent / "analysis_reports" / "test_run"
    output_dir.mkdir(exist_ok=True, parents=True)

    analyzer = ContentQualityAnalyzer(database_path, output_dir)

    # Load October data
    print("📊 Loading October data...")
    df = analyzer.load_october_data(start_date='2025-10-01', end_date='2025-10-16')

    # Take only first 20 posts for testing
    print(f"\n🧪 Testing with first 20 posts only...")
    analyzer.df = df.head(20)

    # Process
    analyzer.process_all_posts()

    # Analyze
    analyzer.detect_reposts_and_patterns()

    # Generate reports
    analyzer.generate_reports()

    print("\n✅ Test complete!")
    print(f"   Results: {output_dir}")
    print("\nIf this works, run the full script: october_content_quality_analysis.py\n")


if __name__ == "__main__":
    main()
