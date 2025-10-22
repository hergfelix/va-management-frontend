#!/usr/bin/env python3
"""
VIDEO-TO-REVENUE ATTRIBUTION V2
Correctly distributes subscriber increases across posts
Attribution logic: Subs from day X are distributed across ALL posts from day X-1 weighted by views
"""

import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict

print("🎯 VIDEO-TO-REVENUE ATTRIBUTION V2 (CORRECTED)")
print("=" * 80)

# ============= LOAD TIKTOK MASTER DATABASE =============
print("\n📂 Loading TikTok Master Database...")
tiktok_posts = []

with open('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tiktok_posts.append({
            'date': row['created_date'],
            'time': row['created_time'],
            'account': row['account'].lower(),
            'va': row['va'],
            'post_url': row['post_url'],
            'views': int(row['views'] or 0),
            'likes': int(row['likes'] or 0),
            'comments': int(row['comments'] or 0),
            'shares': int(row['shares'] or 0),
            'engagement': int(row['engagement'] or 0),
            'engagement_rate': float(row['engagement_rate'] or 0),
            'hashtags': row['hashtags'],
            'sound': row['sound'],
            'slides': row['slides'],
            'source': row['source']
        })

print(f"  ✅ Loaded {len(tiktok_posts):,} TikTok posts")

# ============= LOAD ONLYFANS REVENUE DATA =============
print("\n📂 Loading OnlyFans Revenue Data...")

# Map TikTok character names to OnlyFans accounts
# EXCLUDE: gastmiriam (German - Instagram Reels), inkedaurelia (German)
OF_TO_TIKTOK = {
    'miriamgast': 'MIRIAM',      # US TikTok Slideshows
    'aureliavoss': 'AURELIA',    # US TikTok
    'cutie.sofia': 'SOFIA',      # US TikTok
    'naomisspices': 'NAOMI',     # US TikTok
    'maraasynn': 'MARA',         # US TikTok
    'sukiamari': 'SUKI',         # US TikTok
    'nalaniash': 'NALANI',       # US TikTok
    'tyrawolf': 'TYRA',          # US TikTok
    'megan.hailey': 'MEGAN',     # US TikTok
    'aristormm': 'ARIRI',        # US TikTok (assuming ari = ariri)
}

# Load all revenue CSVs
revenue_files = glob.glob('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/OnlyFans_Revenue_Data/**/Detailed Comparison*.csv', recursive=True)

daily_revenue = {}  # date -> {account -> revenue_data}

for file_path in revenue_files:
    import os
    basename = os.path.basename(file_path)

    if "Detailed Comparison, " in basename:
        date_part = basename.replace("Detailed Comparison, ", "").split(" - ")[0]
        try:
            dt = datetime.strptime(date_part, "%b %d %Y")
            date_str = dt.strftime("%Y-%m-%d")

            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    of_name = row.get('OnlyFans Name', '').strip().lower()

                    if of_name in OF_TO_TIKTOK:
                        if date_str not in daily_revenue:
                            daily_revenue[date_str] = {}

                        daily_revenue[date_str][of_name] = {
                            'new_subs': int(row.get('New Subs', 0) or 0),
                            'total_revenue': float(row.get('Total Revenue', 0) or 0),
                        }
        except Exception as e:
            continue

print(f"  ✅ Loaded {len(revenue_files)} revenue CSVs")
print(f"  📅 Revenue data spans {min(daily_revenue.keys())} to {max(daily_revenue.keys())}")

# ============= CALCULATE LTV PER SUB =============
print("\n📊 Calculating LTV per Sub...")

sept_start = datetime(2025, 9, 1).date()
sept_end = datetime(2025, 9, 30).date()

sept_new_subs = 0
sept_total_revenue = 0

current_date = sept_start
while current_date <= sept_end:
    date_str = current_date.strftime("%Y-%m-%d")
    if date_str in daily_revenue:
        for of_account, data in daily_revenue[date_str].items():
            sept_new_subs += data['new_subs']
            sept_total_revenue += data['total_revenue']
    current_date += timedelta(days=1)

if sept_new_subs > 0:
    ltv_per_sub = sept_total_revenue / sept_new_subs
    print(f"  💰 LTV per Sub: ${ltv_per_sub:.2f}")
    print(f"     (Based on Sept 2025: {sept_new_subs:,} subs → ${sept_total_revenue:,.0f} revenue)")
else:
    ltv_per_sub = 59.54
    print(f"  💰 LTV per Sub: ${ltv_per_sub:.2f} (using fallback)")

# ============= CORRECT ATTRIBUTION LOGIC =============
print("\n🔍 Attributing posts to subscriber increases (weighted by views)...")

# Group posts by date and character
posts_by_date_character = defaultdict(list)
for post in tiktok_posts:
    account_name = post['account'].lower()

    # Find matching character
    tiktok_character = None
    for of_account, character in OF_TO_TIKTOK.items():
        if character.lower() in account_name:
            tiktok_character = character
            of_account_name = of_account
            break

    if tiktok_character:
        post['character'] = tiktok_character
        post['of_account'] = of_account_name
        key = (post['date'], of_account_name)
        posts_by_date_character[key].append(post)

# Now attribute subs to posts
attributions = []

for (post_date, of_account), posts in posts_by_date_character.items():
    # Check if there were new subs the next day
    next_day_dt = datetime.strptime(post_date, "%Y-%m-%d") + timedelta(days=1)
    next_day = next_day_dt.strftime("%Y-%m-%d")

    if next_day in daily_revenue and of_account in daily_revenue[next_day]:
        new_subs = daily_revenue[next_day][of_account]['new_subs']

        if new_subs > 0 and len(posts) > 0:
            # Calculate total views for this day/character
            total_views = sum(p['views'] for p in posts)

            if total_views > 0:
                # Distribute subs proportionally by views
                for post in posts:
                    view_share = post['views'] / total_views
                    attributed_subs = new_subs * view_share
                    attributed_revenue = attributed_subs * ltv_per_sub

                    attributions.append({
                        'post_date': post['date'],
                        'post_url': post['post_url'],
                        'account': post['account'],
                        'va': post['va'],
                        'character': post['character'],
                        'views': post['views'],
                        'engagement': post['engagement'],
                        'engagement_rate': post['engagement_rate'],
                        'view_share_pct': view_share * 100,
                        'attributed_subs': attributed_subs,
                        'attributed_revenue': attributed_revenue,
                        'revenue_per_1k_views': (attributed_revenue / post['views'] * 1000) if post['views'] > 0 else 0,
                        'total_day_subs': new_subs,
                        'total_day_views': total_views,
                        'hashtags': post['hashtags'],
                        'slides': post['slides']
                    })

print(f"  ✅ Found {len(attributions):,} posts with subscriber attribution")

# ============= SAVE RESULTS =============
print("\n💾 Saving attribution results...")

output_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/video_revenue_attribution_v2.csv'

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    fieldnames = [
        'post_date', 'character', 'account', 'va', 'post_url',
        'views', 'engagement', 'engagement_rate',
        'view_share_pct', 'attributed_subs', 'attributed_revenue',
        'revenue_per_1k_views', 'total_day_subs', 'total_day_views',
        'hashtags', 'slides'
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    # Sort by attributed revenue (highest first)
    attributions.sort(key=lambda x: x['attributed_revenue'], reverse=True)

    for attr in attributions:
        writer.writerow(attr)

print(f"✅ Saved to: {output_file}")

# ============= STATISTICS =============
print(f"\n" + "=" * 80)
print("📊 ATTRIBUTION STATISTICS (CORRECTED)")
print("=" * 80)

total_attributed_subs = sum(a['attributed_subs'] for a in attributions)
total_attributed_revenue = sum(a['attributed_revenue'] for a in attributions)

print(f"\n💰 Total Attributed:")
print(f"  Subscribers: {total_attributed_subs:,.1f}")
print(f"  Revenue: ${total_attributed_revenue:,.0f}")

# Top 10 posts by revenue
print(f"\n🏆 Top 10 Posts by Attributed Revenue:")
for i, attr in enumerate(attributions[:10], 1):
    print(f"  {i}. {attr['account']} ({attr['post_date']})")
    print(f"     Views: {attr['views']:,} ({attr['view_share_pct']:.1f}% of day)")
    print(f"     Attributed: {attr['attributed_subs']:.1f} subs → ${attr['attributed_revenue']:,.0f}")
    print(f"     ${attr['revenue_per_1k_views']:.2f} per 1k views")

# By character
print(f"\n👥 Attributed Revenue by Character:")
by_character = defaultdict(lambda: {'subs': 0, 'revenue': 0, 'posts': 0})
for attr in attributions:
    by_character[attr['character']]['subs'] += attr['attributed_subs']
    by_character[attr['character']]['revenue'] += attr['attributed_revenue']
    by_character[attr['character']]['posts'] += 1

for character in sorted(by_character.keys(), key=lambda x: by_character[x]['revenue'], reverse=True):
    data = by_character[character]
    print(f"  {character}: ${data['revenue']:,.0f} ({data['subs']:,.0f} subs, {data['posts']} posts)")

# By VA
print(f"\n🎯 Top 10 VAs by Attributed Revenue:")
by_va = defaultdict(lambda: {'subs': 0, 'revenue': 0, 'posts': 0})
for attr in attributions:
    if attr['va']:
        by_va[attr['va']]['subs'] += attr['attributed_subs']
        by_va[attr['va']]['revenue'] += attr['attributed_revenue']
        by_va[attr['va']]['posts'] += 1

va_sorted = sorted(by_va.items(), key=lambda x: x[1]['revenue'], reverse=True)
for i, (va, data) in enumerate(va_sorted[:10], 1):
    print(f"  {i}. {va}: ${data['revenue']:,.0f} ({data['subs']:,.0f} subs, {data['posts']} posts)")

print(f"\n🎯 ATTRIBUTION COMPLETE!")
