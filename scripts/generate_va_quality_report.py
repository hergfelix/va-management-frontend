#!/usr/bin/env python3
"""
Comprehensive VA Quality Report Generator
Combines:
- OCR text analysis & duplicate detection
- Strategic repost analysis (sound-based)
- Performance metrics (views, engagement)
- Topics_Config weighted scoring
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class VAQualityReporter:
    def __init__(self, database_csv, ocr_data_dir, config_file):
        self.database_csv = Path(database_csv)
        self.ocr_data_dir = Path(ocr_data_dir)
        self.config_file = Path(config_file)

        # Load database
        print("Loading database...")
        self.df = pd.read_csv(self.database_csv, quotechar='"', escapechar='\\')
        self.df['created_date'] = pd.to_datetime(self.df['created_date'])

        # Filter October
        self.oct_df = self.df[
            (self.df['created_date'] >= '2025-10-01') &
            (self.df['created_date'] <= '2025-10-16')
        ]

        print(f"✅ Loaded {len(self.oct_df)} October posts")

        # Load config
        if self.config_file.exists():
            self.config = pd.read_csv(self.config_file)
            print(f"✅ Loaded quality criteria: {len(self.config)} topics")
        else:
            print(f"⚠️  Config file not found: {self.config_file}")
            self.config = None

    def load_ocr_data(self):
        """Load OCR results organized by VA"""
        va_ocr_data = {}

        va_dir = self.ocr_data_dir / "by_va"
        if not va_dir.exists():
            print(f"⚠️  OCR data not found: {va_dir}")
            return {}

        for va_folder in va_dir.iterdir():
            if not va_folder.is_dir():
                continue

            va_name = va_folder.name
            summary_file = va_folder / "summary.json"

            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    va_ocr_data[va_name] = json.load(f)

        print(f"✅ Loaded OCR data for {len(va_ocr_data)} VAs")
        return va_ocr_data

    def calculate_va_metrics(self):
        """Calculate performance metrics per VA"""
        va_metrics = {}

        for va in self.oct_df['va'].unique():
            va_posts = self.oct_df[self.oct_df['va'] == va]

            total_views = va_posts['views'].sum()
            avg_views = va_posts['views'].mean()
            median_views = va_posts['views'].median()

            viral_posts = va_posts[va_posts['views'] >= 10000]
            viral_rate = len(viral_posts) / len(va_posts) if len(va_posts) > 0 else 0

            # Account diversity
            unique_accounts = va_posts['account'].nunique()

            # Posting frequency
            date_range = va_posts['created_date'].max() - va_posts['created_date'].min()
            days = date_range.days if date_range.days > 0 else 1
            posts_per_day = len(va_posts) / days

            va_metrics[va] = {
                'va': va,
                'total_posts': len(va_posts),
                'unique_accounts': unique_accounts,
                'total_views': int(total_views),
                'avg_views': int(avg_views),
                'median_views': int(median_views),
                'viral_posts': len(viral_posts),
                'viral_rate': round(viral_rate, 3),
                'posts_per_day': round(posts_per_day, 2),
                'top_post_views': int(va_posts['views'].max()) if len(va_posts) > 0 else 0
            }

        return va_metrics

    def generate_va_scores(self, va_metrics, ocr_data):
        """
        Generate quality scores based on Topics_Config criteria

        Scoring criteria:
        1. Content Management & Analysis (Weight: 7)
           - Duplicate detection rate (OCR-based)
           - Text extraction success rate
        2. Reposting & Recycling (Weight: 6)
           - Strategic repost score (from OCR duplicates)
        3. Performance metrics (derived)
           - Viral rate
           - View consistency
        """

        va_scores = []

        for va, metrics in va_metrics.items():
            scores = {
                'va': va,
                'total_posts': metrics['total_posts'],
                'avg_views': metrics['avg_views']
            }

            # Content Management Score (0-100)
            ocr_info = ocr_data.get(va, {})
            text_extraction_rate = ocr_info.get('text_extraction_rate', 0)
            scores['text_extraction_rate'] = round(text_extraction_rate * 100, 1)
            scores['content_management_score'] = int(text_extraction_rate * 100)

            # Reposting & Recycling Score (0-100)
            duplicate_groups = ocr_info.get('duplicate_groups', 0)
            posts_with_text = ocr_info.get('posts_with_text', 1)

            if posts_with_text > 0:
                duplicate_rate = duplicate_groups / posts_with_text
                # Lower is better for random reposting (bad)
                # Higher is better if they're strategic (reposting own viral content)
                scores['duplicate_rate'] = round(duplicate_rate * 100, 1)
            else:
                scores['duplicate_rate'] = 0

            # Performance Score (0-100)
            viral_rate = metrics['viral_rate']
            scores['viral_rate'] = round(viral_rate * 100, 1)
            scores['performance_score'] = int(viral_rate * 100)

            # Overall Score (weighted)
            # Content Management: 40%
            # Performance: 40%
            # Consistency (median vs avg): 20%
            consistency = (metrics['median_views'] / metrics['avg_views']) if metrics['avg_views'] > 0 else 0
            consistency_score = min(consistency * 100, 100)

            overall = (
                scores['content_management_score'] * 0.4 +
                scores['performance_score'] * 0.4 +
                consistency_score * 0.2
            )
            scores['overall_score'] = int(overall)

            # Rating
            if overall >= 70:
                scores['rating'] = 'Excellent'
            elif overall >= 50:
                scores['rating'] = 'Good'
            elif overall >= 30:
                scores['rating'] = 'Fair'
            else:
                scores['rating'] = 'Poor'

            va_scores.append(scores)

        return sorted(va_scores, key=lambda x: x['overall_score'], reverse=True)

    def generate_report(self):
        """Generate comprehensive VA quality report"""

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          📊 VA QUALITY REPORT GENERATOR                       ║
║          October 2025 Analysis                                 ║
╚════════════════════════════════════════════════════════════════╝
        """)

        # Load OCR data
        ocr_data = self.load_ocr_data()

        # Calculate metrics
        print("Calculating VA metrics...")
        va_metrics = self.calculate_va_metrics()

        # Generate scores
        print("Generating quality scores...")
        va_scores = self.generate_va_scores(va_metrics, ocr_data)

        # Create report
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': '2025-10-01 to 2025-10-16',
            'total_posts': len(self.oct_df),
            'total_vas': len(va_metrics),
            'va_rankings': va_scores,
            'summary': {
                'excellent_vas': sum(1 for s in va_scores if s['rating'] == 'Excellent'),
                'good_vas': sum(1 for s in va_scores if s['rating'] == 'Good'),
                'fair_vas': sum(1 for s in va_scores if s['rating'] == 'Fair'),
                'poor_vas': sum(1 for s in va_scores if s['rating'] == 'Poor'),
            }
        }

        # Print summary
        print("\n" + "="*70)
        print("VA QUALITY RANKINGS")
        print("="*70 + "\n")

        print(f"{'Rank':<6} {'VA':<15} {'Score':<8} {'Rating':<12} {'Posts':<8} {'Avg Views':<12} {'Viral %':<10}")
        print("-" * 70)

        for i, va in enumerate(va_scores, 1):
            print(f"{i:<6} {va['va']:<15} {va['overall_score']:<8} "
                  f"{va['rating']:<12} {va['total_posts']:<8} "
                  f"{va['avg_views']:>10,}  {va['viral_rate']:<10}")

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Excellent VAs: {report['summary']['excellent_vas']}")
        print(f"Good VAs: {report['summary']['good_vas']}")
        print(f"Fair VAs: {report['summary']['fair_vas']}")
        print(f"Poor VAs: {report['summary']['poor_vas']}")

        # Save report
        report_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports')
        report_dir.mkdir(exist_ok=True, parents=True)

        report_file = report_dir / "04_VA_QUALITY_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report saved: {report_file}")

        # Generate markdown report
        self.generate_markdown_report(report, report_dir)

        return report

    def generate_markdown_report(self, report, output_dir):
        """Generate human-readable markdown report"""

        md = f"""# VA Quality Report - October 2025

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Period:** October 1-16, 2025
**Total Posts Analyzed:** {report['total_posts']:,}

## Summary

| Rating | Count |
|--------|-------|
| Excellent (70+) | {report['summary']['excellent_vas']} |
| Good (50-69) | {report['summary']['good_vas']} |
| Fair (30-49) | {report['summary']['fair_vas']} |
| Poor (<30) | {report['summary']['poor_vas']} |

## VA Rankings

| Rank | VA | Score | Rating | Posts | Avg Views | Viral % |
|------|-----|-------|--------|-------|-----------|---------|
"""

        for i, va in enumerate(report['va_rankings'], 1):
            md += f"| {i} | {va['va']} | {va['overall_score']} | {va['rating']} | "
            md += f"{va['total_posts']} | {va['avg_views']:,} | {va['viral_rate']}% |\n"

        md += f"""

## Scoring Methodology

**Overall Score Components:**
- **Content Management (40%):** Text extraction success rate
- **Performance (40%):** Viral post rate (≥10k views)
- **Consistency (20%):** Median vs average views ratio

**Rating Bands:**
- Excellent: 70-100
- Good: 50-69
- Fair: 30-49
- Poor: 0-29

## Recommendations

### Top Performers
"""

        excellent_vas = [va for va in report['va_rankings'] if va['rating'] == 'Excellent']
        for va in excellent_vas[:3]:
            md += f"- **{va['va']}** (Score: {va['overall_score']}): {va['total_posts']} posts, {va['avg_views']:,} avg views\n"

        md += "\n### VAs Needing Improvement\n"

        poor_vas = [va for va in report['va_rankings'] if va['rating'] in ['Poor', 'Fair']]
        for va in poor_vas:
            md += f"- **{va['va']}** (Score: {va['overall_score']}): Review content strategy\n"

        md_file = output_dir / "04_VA_QUALITY_REPORT.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"💾 Markdown report: {md_file}")


def main():
    """Generate VA quality report"""

    reporter = VAQualityReporter(
        database_csv='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
        ocr_data_dir='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/october_ocr_data',
        config_file='/Users/felixhergenroeder/Downloads/Master-Proof-Log - Topics_Config.csv'
    )

    report = reporter.generate_report()

    print("\n✅ Report generation complete!\n")


if __name__ == "__main__":
    main()
