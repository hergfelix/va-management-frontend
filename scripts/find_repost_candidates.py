#!/usr/bin/env python3
"""
Repost Candidate Finder
Identifies top viral posts worth reposting based on:
- View count (high performers)
- OCR text availability
- Repost type (same account vs cross-creator)
- Account/VA performance
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class RepostCandidateFinder:
    def __init__(self, database_csv, ocr_data_dir):
        self.database_csv = Path(database_csv)
        self.ocr_data_dir = Path(ocr_data_dir)

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

        # Load OCR results
        self.ocr_data = self.load_ocr_data()

    def load_ocr_data(self):
        """Load all OCR results"""
        ocr_results = {}

        all_results_file = self.ocr_data_dir / "all_results.json"
        if all_results_file.exists():
            with open(all_results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
                for post in results:
                    ocr_results[post['post_url']] = post

        print(f"✅ Loaded OCR data for {len(ocr_results)} posts")
        return ocr_results

    def find_candidates(self, min_views=10000, max_candidates=100):
        """
        Find top repost candidates

        Criteria:
        1. Views >= min_views (viral threshold)
        2. Has OCR text (for content recycling)
        3. Recent (October 2025)
        4. Account performance considered
        """

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🔍 REPOST CANDIDATE FINDER                           ║
║          Minimum Views: {min_views:,}                                 ║
║          Max Candidates: {max_candidates}                               ║
╚════════════════════════════════════════════════════════════════╝
        """)

        # Filter viral posts
        viral_posts = self.oct_df[self.oct_df['views'] >= min_views].copy()
        print(f"📊 Found {len(viral_posts)} viral posts (≥{min_views:,} views)")

        # Enrich with OCR data
        candidates = []

        for _, post in viral_posts.iterrows():
            post_url = post['post_url']
            ocr_info = self.ocr_data.get(post_url, {})

            # Build candidate record
            candidate = {
                'post_url': post_url,
                'account': post['account'],
                'va': post['va'],
                'views': int(post['views']),
                'likes': int(post['likes']),
                'comments': int(post['comments']),
                'shares': int(post['shares']),
                'created_date': post['created_date'].strftime('%Y-%m-%d'),
                'sound': post.get('sound', ''),
                'ocr_text': ocr_info.get('ocr_text', ''),
                'has_text': bool(ocr_info.get('ocr_text')),
                'slides': post.get('slides', ''),
                'hashtags': post.get('hashtags', ''),
                # Repost analysis
                'repost_type': self.classify_repost_type(post, viral_posts),
                'engagement_rate': self.calculate_engagement_rate(post),
                'viral_score': self.calculate_viral_score(post)
            }

            candidates.append(candidate)

        # Sort by viral score
        candidates.sort(key=lambda x: x['viral_score'], reverse=True)

        # Take top N
        top_candidates = candidates[:max_candidates]

        print(f"✅ Selected {len(top_candidates)} top candidates")

        return top_candidates

    def classify_repost_type(self, post, all_viral_posts):
        """
        Classify repost opportunity type:
        - "same_account": Repost on same account (proven winner)
        - "same_va": Repost on different account managed by same VA
        - "cross_creator": Repost on account with similar creator type
        """

        # Check if same account has other viral posts
        same_account_virals = all_viral_posts[
            all_viral_posts['account'] == post['account']
        ]

        if len(same_account_virals) > 1:
            return "same_account"

        # Check if same VA has viral posts on other accounts
        same_va_virals = all_viral_posts[
            (all_viral_posts['va'] == post['va']) &
            (all_viral_posts['account'] != post['account'])
        ]

        if len(same_va_virals) > 0:
            return "same_va"

        return "cross_creator"

    def calculate_engagement_rate(self, post):
        """Calculate engagement rate (likes + comments + shares) / views"""
        views = post['views']
        if views == 0:
            return 0

        engagement = post['likes'] + post['comments'] + post['shares']
        return round(engagement / views * 100, 2)

    def calculate_viral_score(self, post):
        """
        Calculate viral score based on:
        - Views (60%)
        - Engagement rate (30%)
        - Recency (10%)
        """

        # Normalize views (assume max 1M)
        views_score = min(post['views'] / 1000000, 1) * 60

        # Engagement rate (assume max 20%)
        engagement_rate = self.calculate_engagement_rate(post)
        engagement_score = min(engagement_rate / 20, 1) * 30

        # Recency (newer = better, max 16 days)
        post_date = pd.to_datetime(post['created_date'])
        days_old = (pd.Timestamp('2025-10-16') - post_date).days
        recency_score = (1 - days_old / 16) * 10 if days_old <= 16 else 0

        return round(views_score + engagement_score + recency_score, 2)

    def generate_report(self, candidates):
        """Generate repost candidates report"""

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'breakdown': {
                'same_account': sum(1 for c in candidates if c['repost_type'] == 'same_account'),
                'same_va': sum(1 for c in candidates if c['repost_type'] == 'same_va'),
                'cross_creator': sum(1 for c in candidates if c['repost_type'] == 'cross_creator'),
                'with_text': sum(1 for c in candidates if c['has_text']),
                'without_text': sum(1 for c in candidates if not c['has_text'])
            },
            'candidates': candidates
        }

        # Save report
        report_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports')
        report_file = report_dir / "05_REPOST_CANDIDATES.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report saved: {report_file}")

        # Generate CSV for Google Sheets
        df = pd.DataFrame(candidates)
        csv_file = report_dir / "05_REPOST_CANDIDATES.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')

        print(f"💾 CSV export: {csv_file}")

        # Print summary
        print("\n" + "="*70)
        print("REPOST CANDIDATE SUMMARY")
        print("="*70)
        print(f"Total Candidates: {report['total_candidates']}")
        print(f"\nBreakdown by Type:")
        print(f"  Same Account:   {report['breakdown']['same_account']}")
        print(f"  Same VA:        {report['breakdown']['same_va']}")
        print(f"  Cross-Creator:  {report['breakdown']['cross_creator']}")
        print(f"\nOCR Text Available:")
        print(f"  With Text:      {report['breakdown']['with_text']}")
        print(f"  Without Text:   {report['breakdown']['without_text']}")

        # Show top 10
        print("\n" + "="*70)
        print("TOP 10 CANDIDATES")
        print("="*70)
        print(f"{'Rank':<6} {'Views':<12} {'Score':<8} {'Type':<15} {'Account':<20}")
        print("-" * 70)

        for i, c in enumerate(candidates[:10], 1):
            print(f"{i:<6} {c['views']:>10,}  {c['viral_score']:<8.1f} "
                  f"{c['repost_type']:<15} {c['account']:<20}")

        return report


def main():
    """Find repost candidates"""

    finder = RepostCandidateFinder(
        database_csv='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
        ocr_data_dir='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/october_ocr_data'
    )

    # Find top 100 candidates
    candidates = finder.find_candidates(min_views=10000, max_candidates=100)

    # Generate report
    report = finder.generate_report(candidates)

    print("\n✅ Repost candidate analysis complete!\n")


if __name__ == "__main__":
    main()
