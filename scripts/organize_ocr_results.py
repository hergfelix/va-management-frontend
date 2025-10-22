#!/usr/bin/env python3
"""
Organize OCR Results by VA
Creates well-structured folders with:
- OCR results per VA
- Duplicate detection per VA
- Performance metrics per VA
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import shutil

class OCROrganizer:
    def __init__(self, ocr_results_file, output_base_dir):
        self.ocr_results_file = Path(ocr_results_file)
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True, parents=True)

        # Load OCR results
        with open(self.ocr_results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)

    def organize_by_va(self):
        """
        Organize OCR results into folders by VA

        Structure:
        october_ocr_data/
        ├── by_va/
        │   ├── Dianne/
        │   │   ├── ocr_posts.json
        │   │   ├── duplicates.json
        │   │   └── summary.json
        │   ├── Pilar/
        │   └── ...
        ├── all_results.json
        └── overall_summary.json
        """
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          📁 ORGANIZING OCR RESULTS BY VA                      ║
╚════════════════════════════════════════════════════════════════╝

Total posts: {len(self.results)}
        """)

        # Group by VA
        va_groups = defaultdict(list)
        for result in self.results:
            va = result['va']
            va_groups[va].append(result)

        print(f"VAs found: {len(va_groups)}\n")

        # Create VA folders
        va_dir = self.output_base_dir / "by_va"
        va_dir.mkdir(exist_ok=True)

        for va, posts in va_groups.items():
            print(f"📊 {va}: {len(posts)} posts")

            # Create VA folder
            va_folder = va_dir / va
            va_folder.mkdir(exist_ok=True)

            # Save posts
            posts_file = va_folder / "ocr_posts.json"
            with open(posts_file, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)

            # Find duplicates within this VA
            duplicates = self.find_duplicates_in_posts(posts)

            # Save duplicates
            dup_file = va_folder / "duplicates.json"
            with open(dup_file, 'w', encoding='utf-8') as f:
                json.dump(duplicates, f, indent=2, ensure_ascii=False)

            # Generate summary
            summary = self.generate_va_summary(va, posts, duplicates)

            # Save summary
            summary_file = va_folder / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            if duplicates['duplicate_groups'] > 0:
                print(f"   ⚠️  {duplicates['duplicate_groups']} duplicate groups found")

        # Save overall results
        all_results_file = self.output_base_dir / "all_results.json"
        shutil.copy(self.ocr_results_file, all_results_file)

        # Generate overall summary
        overall_summary = self.generate_overall_summary(va_groups)
        summary_file = self.output_base_dir / "overall_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(overall_summary, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Organization complete!")
        print(f"   Output directory: {self.output_base_dir}")
        print(f"   VA folders: {len(va_groups)}")

        return va_groups

    def find_duplicates_in_posts(self, posts):
        """Find duplicate content within a set of posts"""
        hash_groups = defaultdict(list)

        for post in posts:
            if post['ocr_text']:  # Only posts with text
                hash_groups[post['text_hash']].append(post)

        duplicates = {h: p for h, p in hash_groups.items() if len(p) > 1}

        return {
            'total_posts': len(posts),
            'posts_with_text': sum(1 for p in posts if p['ocr_text']),
            'unique_patterns': len(hash_groups),
            'duplicate_groups': len(duplicates),
            'duplicates': [
                {
                    'text_hash': text_hash,
                    'text_preview': posts[0]['ocr_text'][:100],
                    'count': len(posts),
                    'posts': [
                        {
                            'account': p['account'],
                            'views': p['views'],
                            'date': p['created_date'][:10],
                            'url': p['post_url']
                        }
                        for p in posts
                    ]
                }
                for text_hash, posts in duplicates.items()
            ]
        }

    def generate_va_summary(self, va, posts, duplicates):
        """Generate summary statistics for a VA"""
        posts_with_text = [p for p in posts if p['ocr_text']]

        total_views = sum(p['views'] for p in posts)
        avg_views = total_views / len(posts) if posts else 0

        viral_posts = [p for p in posts if p['views'] >= 10000]

        return {
            'va': va,
            'total_posts': len(posts),
            'posts_with_text': len(posts_with_text),
            'posts_without_text': len(posts) - len(posts_with_text),
            'text_extraction_rate': len(posts_with_text) / len(posts) if posts else 0,
            'total_views': total_views,
            'avg_views': int(avg_views),
            'viral_posts': len(viral_posts),
            'viral_rate': len(viral_posts) / len(posts) if posts else 0,
            'duplicate_groups': duplicates['duplicate_groups'],
            'accounts': list(set(p['account'] for p in posts))
        }

    def generate_overall_summary(self, va_groups):
        """Generate overall summary across all VAs"""
        total_posts = sum(len(posts) for posts in va_groups.values())
        total_with_text = sum(
            sum(1 for p in posts if p['ocr_text'])
            for posts in va_groups.values()
        )

        va_summaries = []
        for va, posts in va_groups.items():
            duplicates = self.find_duplicates_in_posts(posts)
            summary = self.generate_va_summary(va, posts, duplicates)
            va_summaries.append(summary)

        # Sort by total posts
        va_summaries.sort(key=lambda x: x['total_posts'], reverse=True)

        return {
            'total_posts': total_posts,
            'total_posts_with_text': total_with_text,
            'text_extraction_rate': total_with_text / total_posts if total_posts else 0,
            'total_vas': len(va_groups),
            'va_summaries': va_summaries
        }


def main():
    """Organize OCR results"""

    ocr_results_file = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/bulk_video_ocr/bulk_video_ocr_results.json')
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/october_ocr_data')

    if not ocr_results_file.exists():
        print(f"❌ Results file not found: {ocr_results_file}")
        print("   Run bulk_video_ocr.py first!")
        return

    organizer = OCROrganizer(ocr_results_file, output_dir)
    va_groups = organizer.organize_by_va()

    print("\n📊 VA BREAKDOWN:")
    print("=" * 70)

    for va, posts in sorted(va_groups.items(), key=lambda x: len(x[1]), reverse=True):
        posts_with_text = sum(1 for p in posts if p['ocr_text'])
        total_views = sum(p['views'] for p in posts)
        avg_views = total_views / len(posts)

        print(f"\n{va}:")
        print(f"  Posts: {len(posts)} ({posts_with_text} with text)")
        print(f"  Avg views: {avg_views:,.0f}")
        print(f"  Accounts: {len(set(p['account'] for p in posts))}")

    print("\n✅ Complete!\n")


if __name__ == "__main__":
    main()
