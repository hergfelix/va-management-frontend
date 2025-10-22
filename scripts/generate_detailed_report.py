#!/usr/bin/env python3
"""
Generate detailed VA report from post_metadata.json
Shows exact posts, URLs, texts found, duplicates
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    # Load post metadata
    metadata_file = Path("/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/test_run/post_metadata.json")

    with open(metadata_file, 'r') as f:
        posts = json.load(f)

    print("="*80)
    print("DETAILED VA CONTENT ANALYSIS REPORT")
    print("="*80)

    # Group by VA
    va_posts = defaultdict(list)
    for post in posts:
        va = post.get('va', 'Unknown')
        va_posts[va].append(post)

    # Analyze each VA
    for va in sorted(va_posts.keys()):
        posts_list = va_posts[va]
        print(f"\n{'='*80}")
        print(f"VA: {va} ({len(posts_list)} posts)")
        print(f"{'='*80}")

        # Track text hashes for duplicate detection
        text_hashes = defaultdict(list)

        for i, post in enumerate(posts_list, 1):
            print(f"\n  [{i}] {post['post_url']}")
            print(f"      Account: {post['account']}")
            print(f"      Date: {post['created_date']}")
            print(f"      Views: {post['views']:,}")
            print(f"      Engagement: {post.get('engagement_rate', 0)}%")
            print(f"      Sound: {post.get('sound', 'N/A')[:80]}...")

            # Slides info
            slides = post.get('slides', [])
            print(f"      Slides: {len(slides)} images")

            if len(slides) > 0:
                for j, slide in enumerate(slides, 1):
                    text = slide.get('text', '').strip()
                    if text:
                        print(f"        Slide {j} Text: \"{text[:80]}...\"")
                    else:
                        print(f"        Slide {j}: No text detected")

            # Combined text
            combined_text = post.get('combined_text', '').strip()
            if combined_text:
                print(f"      Combined Text: \"{combined_text[:100]}...\"")
            else:
                print(f"      Combined Text: EMPTY (no OCR results)")

            # Track for duplicates
            text_hash = post.get('text_hash')
            if text_hash:
                text_hashes[text_hash].append((i, post))

        # Show duplicates
        print(f"\n  DUPLICATE ANALYSIS:")
        duplicates_found = False
        for text_hash, duplicate_posts in text_hashes.items():
            if len(duplicate_posts) > 1:
                duplicates_found = True
                print(f"\n    🔄 DUPLICATE SET ({len(duplicate_posts)} posts):")
                for post_num, post in duplicate_posts:
                    print(f"       [{post_num}] {post['post_url']} ({post['views']:,} views)")
                    if post.get('combined_text'):
                        print(f"           Text: \"{post['combined_text'][:60]}...\"")

        if not duplicates_found:
            print(f"    ✅ No duplicates found (all posts unique)")

        print()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total VAs: {len(va_posts)}")
    print(f"Total Posts: {len(posts)}")
    print(f"Posts with slides: {sum(1 for p in posts if len(p.get('slides', [])) > 0)}")
    print(f"Posts with OCR text: {sum(1 for p in posts if p.get('combined_text', '').strip() != '')}")
    print()


if __name__ == "__main__":
    main()
