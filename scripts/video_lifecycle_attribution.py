#!/usr/bin/env python3
"""
VIDEO LIFECYCLE ATTRIBUTION
Tracks video performance over time and attributes revenue based on:
- Time from posting to scraping (video age)
- View velocity and viral lifecycle
- Character-level competition (multiple viral videos at once)
- Time-window attribution (7-14 day windows)
"""

import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict

print("🎯 VIDEO LIFECYCLE ATTRIBUTION")
print("=" * 80)

# ============= LOAD TIKTOK MASTER DATABASE =============
print("\n📂 Loading TikTok Master Database...")
tiktok_posts = []

# Scraping dates by source
SCRAPING_DATES = {
    'old_clean': datetime(2025, 9, 15).date(),
    'sept_scrape': datetime(2025, 10, 18).date(),
    'oct_scrape': datetime(2025, 10, 18).date(),
    'current_metrics': datetime(2025, 10, 18).date(),  # Approximate (daily scraping)
}

with open('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        post_date = datetime.strptime(row['created_date'], "%Y-%m-%d").date()
        source = row['source']
        scraped_date = SCRAPING_DATES.get(source)

        # Calculate days from posting to scraping
        if scraped_date:
            days_to_scrape = (scraped_date - post_date).days
        else:
            days_to_scrape = None

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
            'source': row['source'],
            'scraped_date': scraped_date.strftime("%Y-%m-%d") if scraped_date else '',
            'days_to_scrape': days_to_scrape
        })

print(f"  ✅ Loaded {len(tiktok_posts):,} TikTok posts")

# ============= VIEW BRACKETS =============
print("\n📊 Categorizing posts by view brackets...")

VIEW_BRACKETS = [
    (0, 1000, "0-1k"),
    (1000, 5000, "1k-5k"),
    (5000, 10000, "5k-10k"),
    (10000, 50000, "10k-50k"),
    (50000, 100000, "50k-100k"),
    (100000, 500000, "100k-500k"),
    (500000, 1000000, "500k-1M"),
    (1000000, 10000000, "1M+"),
]

def get_view_bracket(views):
    for min_v, max_v, label in VIEW_BRACKETS:
        if min_v <= views < max_v:
            return label
    return "1M+"

for post in tiktok_posts:
    post['view_bracket'] = get_view_bracket(post['views'])

# ============= LOAD ONLYFANS REVENUE DATA =============
print("\n📂 Loading OnlyFans Revenue Data...")

OF_TO_TIKTOK = {
    'miriamgast': 'MIRIAM',
    'aureliavoss': 'AURELIA',
    'cutie.sofia': 'SOFIA',
    'naomisspices': 'NAOMI',
    'maraasynn': 'MARA',
    'sukiamari': 'SUKI',
    'nalaniash': 'NALANI',
    'tyrawolf': 'TYRA',
    'megan.hailey': 'MEGAN',
    'aristormm': 'ARIRI',
}

revenue_files = glob.glob('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/OnlyFans_Revenue_Data/**/Detailed Comparison*.csv', recursive=True)

daily_revenue = {}

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

# ============= CALCULATE LTV =============
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

ltv_per_sub = sept_total_revenue / sept_new_subs if sept_new_subs > 0 else 22.89
print(f"  💰 LTV per Sub: ${ltv_per_sub:.2f}")

# ============= MAP POSTS TO CHARACTERS =============
print("\n🔗 Mapping posts to characters...")

for post in tiktok_posts:
    account_name = post['account'].lower()

    post['character'] = None
    post['of_account'] = None

    for of_account, character in OF_TO_TIKTOK.items():
        if character.lower() in account_name:
            post['character'] = character
            post['of_account'] = of_account
            break

posts_with_character = [p for p in tiktok_posts if p['character']]
print(f"  ✅ Mapped {len(posts_with_character):,} posts to characters")

# ============= TIME-WINDOW ATTRIBUTION =============
print("\n🔍 Performing time-window attribution (14-day windows)...")

ATTRIBUTION_WINDOW_DAYS = 14

attributions = []

for post in posts_with_character:
    post_date = datetime.strptime(post['date'], "%Y-%m-%d").date()
    of_account = post['of_account']
    character = post['character']

    # Collect subs in the next 14 days
    window_subs = 0
    window_revenue_total = 0

    for day_offset in range(1, ATTRIBUTION_WINDOW_DAYS + 1):
        target_date = (post_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        if target_date in daily_revenue and of_account in daily_revenue[target_date]:
            window_subs += daily_revenue[target_date][of_account]['new_subs']
            window_revenue_total += daily_revenue[target_date][of_account]['total_revenue']

    # Find competing posts from same character in same window
    window_start = post_date
    window_end = post_date + timedelta(days=ATTRIBUTION_WINDOW_DAYS)

    competing_posts = []
    for other_post in posts_with_character:
        other_date = datetime.strptime(other_post['date'], "%Y-%m-%d").date()

        if (other_post['character'] == character and
            window_start <= other_date <= window_end and
            other_post['post_url'] != post['post_url']):
            competing_posts.append(other_post)

    # Calculate share based on views (weighted attribution)
    total_window_views = post['views']
    for comp_post in competing_posts:
        total_window_views += comp_post['views']

    if total_window_views > 0:
        view_share = post['views'] / total_window_views
    else:
        view_share = 1.0

    attributed_subs = window_subs * view_share
    attributed_revenue = attributed_subs * ltv_per_sub

    attributions.append({
        'post_date': post['date'],
        'scraped_date': post['scraped_date'],
        'days_to_scrape': post['days_to_scrape'],
        'post_url': post['post_url'],
        'account': post['account'],
        'va': post['va'],
        'character': character,
        'views': post['views'],
        'view_bracket': post['view_bracket'],
        'engagement': post['engagement'],
        'engagement_rate': post['engagement_rate'],
        'window_total_subs': window_subs,
        'competing_posts_count': len(competing_posts),
        'view_share_pct': view_share * 100,
        'attributed_subs': attributed_subs,
        'attributed_revenue': attributed_revenue,
        'revenue_per_1k_views': (attributed_revenue / post['views'] * 1000) if post['views'] > 0 else 0,
        'hashtags': post['hashtags'],
        'slides': post['slides'],
    })

print(f"  ✅ Attributed {len(attributions):,} posts")

# ============= SAVE RESULTS =============
print("\n💾 Saving lifecycle attribution results...")

output_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/video_lifecycle_attribution.csv'

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    fieldnames = [
        'post_date', 'scraped_date', 'days_to_scrape',
        'character', 'account', 'va', 'post_url',
        'views', 'view_bracket', 'engagement', 'engagement_rate',
        'window_total_subs', 'competing_posts_count', 'view_share_pct',
        'attributed_subs', 'attributed_revenue', 'revenue_per_1k_views',
        'hashtags', 'slides'
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    attributions.sort(key=lambda x: x['attributed_revenue'], reverse=True)

    for attr in attributions:
        writer.writerow(attr)

print(f"✅ Saved to: {output_file}")

# ============= STATISTICS =============
print(f"\n" + "=" * 80)
print("📊 LIFECYCLE ATTRIBUTION STATISTICS")
print("=" * 80)

total_attributed_subs = sum(a['attributed_subs'] for a in attributions)
total_attributed_revenue = sum(a['attributed_revenue'] for a in attributions)

print(f"\n💰 Total Attributed (14-day windows):")
print(f"  Subscribers: {total_attributed_subs:,.1f}")
print(f"  Revenue: ${total_attributed_revenue:,.0f}")

# Top 10 by revenue
print(f"\n🏆 Top 10 Posts by Attributed Revenue:")
for i, attr in enumerate(attributions[:10], 1):
    print(f"\n  {i}. {attr['account']} ({attr['post_date']})")
    print(f"     Views: {attr['views']:,} ({attr['view_bracket']})")
    print(f"     Scraped: {attr['days_to_scrape']} days after posting")
    print(f"     Competing posts: {attr['competing_posts_count']}")
    print(f"     Share: {attr['view_share_pct']:.1f}% of character's window views")
    print(f"     → {attr['attributed_subs']:.1f} subs = ${attr['attributed_revenue']:,.0f}")
    print(f"     ${attr['revenue_per_1k_views']:.2f} per 1k views")

# By view bracket
print(f"\n📊 Revenue by View Bracket:")
by_bracket = defaultdict(lambda: {'subs': 0, 'revenue': 0, 'posts': 0})
for attr in attributions:
    by_bracket[attr['view_bracket']]['subs'] += attr['attributed_subs']
    by_bracket[attr['view_bracket']]['revenue'] += attr['attributed_revenue']
    by_bracket[attr['view_bracket']]['posts'] += 1

bracket_order = ["0-1k", "1k-5k", "5k-10k", "10k-50k", "50k-100k", "100k-500k", "500k-1M", "1M+"]
for bracket in bracket_order:
    if bracket in by_bracket:
        data = by_bracket[bracket]
        avg_revenue = data['revenue'] / data['posts'] if data['posts'] > 0 else 0
        print(f"  {bracket:>12}: ${data['revenue']:>10,.0f} ({data['posts']:>5} posts, avg ${avg_revenue:>6,.0f}/post)")

# By character
print(f"\n👥 Revenue by Character:")
by_character = defaultdict(lambda: {'subs': 0, 'revenue': 0, 'posts': 0})
for attr in attributions:
    by_character[attr['character']]['subs'] += attr['attributed_subs']
    by_character[attr['character']]['revenue'] += attr['attributed_revenue']
    by_character[attr['character']]['posts'] += 1

for character in sorted(by_character.keys(), key=lambda x: by_character[x]['revenue'], reverse=True):
    data = by_character[character]
    print(f"  {character:>8}: ${data['revenue']:>10,.0f} ({data['subs']:>6,.0f} subs, {data['posts']:>5,} posts)")

# Top VAs
print(f"\n🎯 Top 10 VAs by Attributed Revenue:")
by_va = defaultdict(lambda: {'subs': 0, 'revenue': 0, 'posts': 0})
for attr in attributions:
    if attr['va']:
        by_va[attr['va']]['subs'] += attr['attributed_subs']
        by_va[attr['va']]['revenue'] += attr['attributed_revenue']
        by_va[attr['va']]['posts'] += 1

va_sorted = sorted(by_va.items(), key=lambda x: x[1]['revenue'], reverse=True)
for i, (va, data) in enumerate(va_sorted[:10], 1):
    print(f"  {i:>2}. {va:>15}: ${data['revenue']:>10,.0f} ({data['subs']:>6,.0f} subs, {data['posts']:>5,} posts)")

print(f"\n🎯 LIFECYCLE ATTRIBUTION COMPLETE!")
