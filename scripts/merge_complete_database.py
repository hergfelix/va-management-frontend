#!/usr/bin/env python3
"""
MASTER DATABASE CREATION
Merges all TikTok data sources into one complete timeline
Mai 9, 2025 → Oct 18, 2025
"""

import csv
import json
from datetime import datetime

print("🔥 CREATING MASTER TIKTOK DATABASE")
print("=" * 80)

# ============= LOAD ALL DATA SOURCES =============
all_posts = []

# 1. OLD CLEAN DATA (Mai 9 - Sept 15)
print("\n📂 Loading old clean data (Mai-Sept)...")
with open('/Users/felixhergenroeder/Downloads/Master-Proof-Log - clean_old.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row.get('createTimeISO'):
            continue

        # Extract slideshow links (slide1_link through slide12_link)
        slides = []
        for i in range(1, 13):
            slide_link = row.get(f'slide{i}_link', '')
            if slide_link and slide_link.strip():
                slides.append(slide_link.strip())

        all_posts.append({
            'post_url': row.get('post_url', ''),
            'account': row.get('author', ''),
            'views': int(row.get('playCount', 0) or 0),
            'likes': int(row.get('diggCount', 0) or 0),
            'comments': int(row.get('commentCount', 0) or 0),
            'shares': int(row.get('shareCount', 0) or 0),
            'created': row.get('createTimeISO', ''),
            'hashtags': row.get('hashtags', ''),
            'sound_link': row.get('sound_link', ''),
            'slides': slides,
            'source': 'old_clean'
        })

print(f"  ✅ Loaded {len(all_posts)} posts from old_clean")

# 2. SEPT 23-29 SCRAPE
print("\n📂 Loading Sept 23-29 scrape...")
sept_start = len(all_posts)
with open('/Users/felixhergenroeder/Downloads/dataset_tiktok-scraper_2025-10-18_19-45-32-750.json', 'r') as f:
    sept_data = json.load(f)
    for item in sept_data:
        if 'error' in item or 'createTimeISO' not in item:
            continue

        # Extract slideshow images from imagePost.images
        slides = []
        if 'imagePost' in item and 'images' in item['imagePost']:
            for img in item['imagePost']['images']:
                if 'imageURL' in img and 'imageUrlList' in img['imageURL']:
                    url_list = img['imageURL']['imageUrlList']
                    if url_list and len(url_list) > 0:
                        slides.append(url_list[0])  # Use first URL from list

        all_posts.append({
            'post_url': item.get('webVideoUrl', ''),
            'account': item.get('authorMeta.name', ''),
            'views': int(item.get('playCount', 0) or 0),
            'likes': int(item.get('diggCount', 0) or 0),
            'comments': int(item.get('commentCount', 0) or 0),
            'shares': int(item.get('shareCount', 0) or 0),
            'created': item.get('createTimeISO', ''),
            'hashtags': item.get('text', ''),
            'sound_link': item.get('musicMeta.musicName', ''),
            'slides': slides,
            'source': 'sept_scrape'
        })

print(f"  ✅ Loaded {len(all_posts) - sept_start} posts from Sept scrape")

# 3. OCT 12-13 MERGED (includes test)
print("\n📂 Loading Oct 12-13 scrape (merged)...")
oct_start = len(all_posts)
with open('/Users/felixhergenroeder/oct_12-13_complete.json', 'r') as f:
    oct_data = json.load(f)
    for item in oct_data:
        if 'error' in item or 'createTimeISO' not in item:
            continue

        # Extract slideshow images from imagePost.images
        slides = []
        if 'imagePost' in item and 'images' in item['imagePost']:
            for img in item['imagePost']['images']:
                if 'imageURL' in img and 'imageUrlList' in img['imageURL']:
                    url_list = img['imageURL']['imageUrlList']
                    if url_list and len(url_list) > 0:
                        slides.append(url_list[0])  # Use first URL from list

        all_posts.append({
            'post_url': item.get('webVideoUrl', ''),
            'account': item.get('authorMeta.name', ''),
            'views': int(item.get('playCount', 0) or 0),
            'likes': int(item.get('diggCount', 0) or 0),
            'comments': int(item.get('commentCount', 0) or 0),
            'shares': int(item.get('shareCount', 0) or 0),
            'created': item.get('createTimeISO', ''),
            'hashtags': item.get('text', ''),
            'sound_link': item.get('musicMeta.musicName', ''),
            'slides': slides,
            'source': 'oct_scrape'
        })

print(f"  ✅ Loaded {len(all_posts) - oct_start} posts from Oct scrape")

# 4. CURRENT METRICS LOG (Sept 15 - Oct 18)
print("\n📂 Loading current metrics log...")
current_start = len(all_posts)
with open('/Users/felixhergenroeder/Downloads/Master-Proof-Log - Metrics_Log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row.get('createTimeISO'):
            continue

        # Extract slideshow links (slide1_link through slide12_link)
        slides = []
        for i in range(1, 13):
            slide_link = row.get(f'slide{i}_link', '')
            if slide_link and slide_link.strip():
                slides.append(slide_link.strip())

        all_posts.append({
            'post_url': row.get('post_url', ''),
            'account': row.get('author', ''),
            'views': int(row.get('playCount', 0) or 0),
            'likes': int(row.get('diggCount', 0) or 0),
            'comments': int(row.get('commentCount', 0) or 0),
            'shares': int(row.get('shareCount', 0) or 0),
            'created': row.get('createTimeISO', ''),
            'hashtags': row.get('hashtags', ''),
            'sound_link': row.get('sound_link', ''),
            'slides': slides,
            'source': 'current_metrics'
        })

print(f"  ✅ Loaded {len(all_posts) - current_start} posts from current metrics")

# ============= DEDUPLICATE =============
print(f"\n🔄 Deduplicating...")
print(f"  Before: {len(all_posts)} posts")

# Remove duplicates by post_url
seen_urls = set()
unique_posts = []

for post in all_posts:
    url = post['post_url']
    if url and url not in seen_urls:
        seen_urls.add(url)
        unique_posts.append(post)

print(f"  After: {len(unique_posts)} unique posts")
print(f"  Removed: {len(all_posts) - len(unique_posts)} duplicates")

# ============= SORT BY DATE =============
print(f"\n📅 Sorting by createTime...")
unique_posts.sort(key=lambda x: x['created'])

# ============= ADD VA MAPPING =============
print(f"\n👥 Adding VA mapping from current metrics...")

# Build account -> VA mapping from current metrics
account_to_va = {}
with open('/Users/felixhergenroeder/Downloads/Master-Proof-Log - Metrics_Log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        account = row.get('author', '').strip().lower()
        va = row.get('va', '').strip()
        if account and va:
            account_to_va[account] = va

# Add VA to all posts
for post in unique_posts:
    account_lower = post['account'].lower()
    post['va'] = account_to_va.get(account_lower, '')

# ============= SAVE MASTER DATABASE =============
print(f"\n💾 Saving Master Database...")

output_file = '/Users/felixhergenroeder/MASTER_TIKTOK_DATABASE.csv'

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    fieldnames = [
        'created_date',
        'created_time',
        'account',
        'va',
        'post_url',
        'views',
        'likes',
        'comments',
        'shares',
        'engagement',
        'engagement_rate',
        'hashtags',
        'sound',
        'slides',
        'source'
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for post in unique_posts:
        # Parse date
        created_iso = post['created']
        try:
            dt = datetime.fromisoformat(created_iso.replace('Z', '+00:00'))
            created_date = dt.strftime('%Y-%m-%d')
            created_time = dt.strftime('%H:%M:%S')
        except:
            created_date = created_iso[:10] if created_iso else ''
            created_time = created_iso[11:19] if len(created_iso) > 11 else ''

        engagement = post['likes'] + post['comments'] + post['shares']
        engagement_rate = (engagement / post['views'] * 100) if post['views'] > 0 else 0

        # Format slides as pipe-separated URLs (klein & unauffällig)
        slides_str = '|'.join(post.get('slides', [])) if post.get('slides') else ''

        writer.writerow({
            'created_date': created_date,
            'created_time': created_time,
            'account': post['account'],
            'va': post['va'],
            'post_url': post['post_url'],
            'views': post['views'],
            'likes': post['likes'],
            'comments': post['comments'],
            'shares': post['shares'],
            'engagement': engagement,
            'engagement_rate': f"{engagement_rate:.2f}",
            'hashtags': post['hashtags'],
            'sound': post['sound_link'],
            'slides': slides_str,
            'source': post['source']
        })

print(f"✅ Saved to: {output_file}")

# ============= STATISTICS =============
print(f"\n" + "=" * 80)
print("📊 MASTER DATABASE STATISTICS")
print("=" * 80)

# Date range
dates = [p['created'][:10] for p in unique_posts if p['created']]
print(f"\n📅 Date Range:")
print(f"  First post: {min(dates)}")
print(f"  Last post: {max(dates)}")
print(f"  Total days: {(datetime.fromisoformat(max(dates)) - datetime.fromisoformat(min(dates))).days + 1}")

# Posts by source
from collections import Counter
sources = Counter(p['source'] for p in unique_posts)
print(f"\n📂 Posts by Source:")
for source, count in sources.most_common():
    print(f"  {source}: {count:,} posts")

# Posts by VA
vas = Counter(p['va'] for p in unique_posts if p['va'])
print(f"\n👥 Posts by VA (Top 10):")
for va, count in vas.most_common(10):
    print(f"  {va}: {count:,} posts")

# Total metrics
total_views = sum(p['views'] for p in unique_posts)
total_engagement = sum(p['likes'] + p['comments'] + p['shares'] for p in unique_posts)
print(f"\n📈 Total Metrics:")
print(f"  Posts: {len(unique_posts):,}")
print(f"  Views: {total_views:,}")
print(f"  Engagement: {total_engagement:,}")
print(f"  Avg Views/Post: {total_views/len(unique_posts):,.0f}")

# Slideshow coverage
posts_with_slides = sum(1 for p in unique_posts if p.get('slides'))
total_slides = sum(len(p.get('slides', [])) for p in unique_posts)
print(f"\n🖼️  Slideshow Coverage:")
print(f"  Posts with slides: {posts_with_slides:,} ({posts_with_slides/len(unique_posts)*100:.1f}%)")
print(f"  Total slide images: {total_slides:,}")
print(f"  Avg slides/post: {total_slides/posts_with_slides:.1f}" if posts_with_slides > 0 else "  Avg slides/post: N/A")

print(f"\n🎯 MASTER DATABASE READY FOR ANALYSIS!")