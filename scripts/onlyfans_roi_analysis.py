#!/usr/bin/env python3
"""
ULTIMATE ROI ANALYSIS: TikTok Performance → OnlyFans Revenue
Identifiziert welche TikTok Accounts/VAs wirklich Geld bringen
"""

import csv
from collections import defaultdict
import statistics

print("🔥 ULTIMATE ROI ANALYSIS: TikTok → OnlyFans Revenue")
print("=" * 100)

# ============= ONLYFANS MAPPING =============
# Mapping: OnlyFans Name → TikTok Character (für Dashboard matching)
OF_TO_TIKTOK = {
    # Miriam Accounts (RELEVANT: miriamgast - US Slideshows)
    'miriamgast': 'MIRIAM',  # US Slideshow Account (RELEVANT)
    'gastmiriam': 'MIRIAM_DE',  # German Account (separieren)

    # Aurelia Accounts (RELEVANT: aureliavoss - US TikToks)
    'aureliavoss': 'AURELIA',  # US TikTok Account (RELEVANT)
    'inkedaurelia': 'AURELIA_DE',  # German Account (separieren)

    # Other Accounts
    'maraasynn': 'MARA',
    'naomisspices': 'NAOMI',
    'megan.hailey': 'MEGAN',
    'cutie.sofia': 'SOFIA',
    'tyrawolf': 'TYRA',
    'sukiamari': 'SUKI',
    'aristormm': 'ARI',
    'nalaniash': 'NALANI',
}

# ============= LOAD ONLYFANS REVENUE DATA =============
print("\n💰 Loading OnlyFans Revenue Data (Oct 1-16, 2025)...")

of_files = [
    ('Oct 1', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 1 2025 - Oct 1 2025.csv'),
    ('Oct 3', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 3 2025 - Oct 3 2025.csv'),
    ('Oct 5', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 5 2025 - Oct 5 2025.csv'),
    ('Oct 7', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 7 2025 - Oct 7 2025.csv'),
    ('Oct 8', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 8 2025 - Oct 8 2025.csv'),
    ('Oct 10', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 10 2025 - Oct 10 2025.csv'),
    ('Oct 12', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 12 2025 - Oct 12 2025.csv'),
    ('Oct 14', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 14 2025 - Oct 14 2025.csv'),
    ('Oct 16', '/Users/felixhergenroeder/Downloads/Detailed Comparison, Oct 16 2025 - Oct 16 2025.csv'),
]

of_data = defaultdict(lambda: {
    'total_revenue': 0,
    'total_subs': 0,
    'daily_data': [],
    'character': None
})

for date, filepath in of_files:
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            of_name = row.get('OnlyFans Name', '').strip()

            if of_name not in OF_TO_TIKTOK:
                continue

            character = OF_TO_TIKTOK[of_name]

            try:
                revenue = float(row.get('Total Revenue', 0) or 0)
                new_subs = int(row.get('New Subs', 0) or 0)
                avg_fan_spend = float(row.get('Average Fan Spend', 0) or 0)

                of_data[of_name]['total_revenue'] += revenue
                of_data[of_name]['total_subs'] += new_subs
                of_data[of_name]['character'] = character
                of_data[of_name]['daily_data'].append({
                    'date': date,
                    'revenue': revenue,
                    'subs': new_subs,
                    'avg_spend': avg_fan_spend
                })
            except:
                continue

print(f"✅ Loaded OnlyFans data for {len(of_data)} accounts")
for of_name, data in sorted(of_data.items(), key=lambda x: x[1]['total_revenue'], reverse=True):
    print(f"  {of_name:<20} → {data['character']:<12} ${data['total_revenue']:>8,.2f} ({data['total_subs']:>3d} subs)")

# ============= LOAD TIKTOK DASHBOARD DATA =============
print("\n📊 Loading TikTok Dashboard Data...")
dashboard = {}
with open('/Users/felixhergenroeder/Downloads/TT-Check 16_10 - TikTok Analytics Dashboard (1).csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    current_va = None

    for line in lines:
        parts = [p.strip() for p in line.strip().split(',')]

        # VA Header
        if len(parts) > 2 and "Accounts" in parts[1]:
            va_name = parts[0]
            if va_name and va_name not in ['TIKTOK ANALYTICS DASHBOARD', 'GOAL', 'Run refreshDashboard', 'OVERVIEW', 'TEAM TOTAL']:
                current_va = va_name
                male_avg = 0
                us_avg = 0
                daily_avg = 0

                for part in parts:
                    if "Avg Male:" in part:
                        try:
                            male_avg = float(part.split(':')[1].strip().replace('%', '')) / 100
                        except:
                            pass
                    if "Avg US:" in part:
                        try:
                            us_avg = float(part.split(':')[1].strip().replace('%', '')) / 100
                        except:
                            pass

                if current_va:
                    dashboard[current_va] = {
                        'male_avg': male_avg,
                        'us_avg': us_avg,
                        'accounts': []
                    }

print(f"✅ Loaded {len(dashboard)} VAs from dashboard")

# ============= LOAD TIKTOK METRICS LOG =============
print("\n📈 Loading TikTok Metrics Log...")
va_posts = defaultdict(list)
account_to_va = {}  # Map account name to VA

with open('/Users/felixhergenroeder/Downloads/Master-Proof-Log - Metrics_Log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        va = row.get('va', '').strip().upper()
        account = row.get('author', '').strip().lower()

        if not va or not account:
            continue

        account_to_va[account] = va

        try:
            post = {
                'account': account,
                'views': int(row.get('playCount', 0) or 0),
                'likes': int(row.get('diggCount', 0) or 0),
                'comments': int(row.get('commentCount', 0) or 0),
                'shares': int(row.get('shareCount', 0) or 0),
                'created': row.get('createTimeISO', ''),
            }
            post['engagement'] = post['likes'] + post['comments'] + post['shares']
            va_posts[va].append(post)
        except:
            continue

print(f"✅ Loaded posts from {len(va_posts)} VAs")

# ============= CHARACTER TO VA MAPPING =============
# Find which VAs run which characters by looking at account names
CHARACTER_TO_VAS = defaultdict(list)

# Miriam accounts
for account, va in account_to_va.items():
    if 'miriam' in account:
        CHARACTER_TO_VAS['MIRIAM'].append(va)

# Aurelia accounts
for account, va in account_to_va.items():
    if 'aurelia' in account:
        CHARACTER_TO_VAS['AURELIA'].append(va)

# Mara accounts
for account, va in account_to_va.items():
    if 'mara' in account:
        CHARACTER_TO_VAS['MARA'].append(va)

# Naomi accounts
for account, va in account_to_va.items():
    if 'naomi' in account:
        CHARACTER_TO_VAS['NAOMI'].append(va)

# Megan accounts
for account, va in account_to_va.items():
    if 'megan' in account:
        CHARACTER_TO_VAS['MEGAN'].append(va)

# Sofia accounts
for account, va in account_to_va.items():
    if 'sofia' in account:
        CHARACTER_TO_VAS['SOFIA'].append(va)

# Tyra accounts
for account, va in account_to_va.items():
    if 'tyra' in account:
        CHARACTER_TO_VAS['TYRA'].append(va)

# Ari accounts
for account, va in account_to_va.items():
    if 'ariri' in account:
        CHARACTER_TO_VAS['ARI'].append(va)

# Suki accounts
for account, va in account_to_va.items():
    if 'suki' in account:
        CHARACTER_TO_VAS['SUKI'].append(va)

# Nalani accounts
for account, va in account_to_va.items():
    if 'nalani' in account:
        CHARACTER_TO_VAS['NALANI'].append(va)

# Deduplicate
for char in CHARACTER_TO_VAS:
    CHARACTER_TO_VAS[char] = list(set(CHARACTER_TO_VAS[char]))

print("\n🎯 Character → VA Mapping:")
for char, vas in sorted(CHARACTER_TO_VAS.items()):
    print(f"  {char:<12} → {len(vas)} VAs: {', '.join(vas[:5])}")

# ============= CALCULATE ROI PER CHARACTER =============
print("\n" + "=" * 100)
print("💰 ROI ANALYSIS: OnlyFans Revenue vs. TikTok Performance")
print("=" * 100)

roi_analysis = []

for of_name, of_info in of_data.items():
    character = of_info['character']

    # Skip German accounts
    if character in ['MIRIAM_DE', 'AURELIA_DE']:
        continue

    # Get all VAs for this character
    vas = CHARACTER_TO_VAS.get(character, [])

    # Calculate total TikTok performance for this character
    total_views = 0
    total_posts = 0

    for va in vas:
        posts = va_posts.get(va, [])
        total_views += sum(p['views'] for p in posts)
        total_posts += len(posts)

    avg_views_per_post = total_views / total_posts if total_posts > 0 else 0

    # Revenue metrics
    total_revenue = of_info['total_revenue']
    total_subs = of_info['total_subs']
    avg_sub_value = total_revenue / total_subs if total_subs > 0 else 0

    # ROI Metrics
    views_per_sub = total_views / total_subs if total_subs > 0 else 0
    revenue_per_1k_views = (total_revenue / total_views * 1000) if total_views > 0 else 0

    roi_analysis.append({
        'of_name': of_name,
        'character': character,
        'vas': vas,
        'va_count': len(vas),
        'total_revenue': total_revenue,
        'total_subs': total_subs,
        'avg_sub_value': avg_sub_value,
        'total_views': total_views,
        'total_posts': total_posts,
        'avg_views_per_post': avg_views_per_post,
        'views_per_sub': views_per_sub,
        'revenue_per_1k_views': revenue_per_1k_views,
    })

# Sort by revenue
roi_analysis.sort(key=lambda x: x['total_revenue'], reverse=True)

# ============= PRINT ROI ANALYSIS =============
print("\n🏆 TOP PERFORMERS BY REVENUE")
print("-" * 100)
print(f"{'Rank':<5} {'OF Account':<20} {'Character':<12} {'Revenue':<12} {'Subs':<8} {'Views':<12} {'$/1k Views':<12} {'Views/Sub':<12}")
print("-" * 100)

for i, data in enumerate(roi_analysis, 1):
    print(f"{i:<5} {data['of_name']:<20} {data['character']:<12} ${data['total_revenue']:<11,.2f} {data['total_subs']:<8d} {data['total_views']:<12,d} ${data['revenue_per_1k_views']:<11.2f} {data['views_per_sub']:<12,.0f}")

print("\n")
print("🎯 CONVERSION EFFICIENCY (Views → Subs)")
print("-" * 100)
efficient = sorted(roi_analysis, key=lambda x: x['views_per_sub'] if x['views_per_sub'] > 0 else float('inf'))
for i, data in enumerate(efficient[:10], 1):
    if data['views_per_sub'] == 0:
        continue
    print(f"{i:<3}. {data['character']:<12} {data['views_per_sub']:>8,.0f} views/sub ({data['total_subs']:>3d} subs from {data['total_views']:>8,d} views)")

print("\n")
print("💵 REVENUE EFFICIENCY ($ per 1k Views)")
print("-" * 100)
revenue_eff = sorted(roi_analysis, key=lambda x: x['revenue_per_1k_views'], reverse=True)
for i, data in enumerate(revenue_eff[:10], 1):
    if data['revenue_per_1k_views'] == 0:
        continue
    print(f"{i:<3}. {data['character']:<12} ${data['revenue_per_1k_views']:>7.2f}/1k views (${data['total_revenue']:>8,.2f} from {data['total_views']:>8,d} views)")

# ============= VA-LEVEL BREAKDOWN =============
print("\n" + "=" * 100)
print("👥 VA-LEVEL REVENUE CONTRIBUTION")
print("=" * 100)

# Calculate each VA's contribution to their character's revenue
va_revenue_contribution = []

for of_name, of_info in of_data.items():
    character = of_info['character']

    if character in ['MIRIAM_DE', 'AURELIA_DE']:
        continue

    vas = CHARACTER_TO_VAS.get(character, [])
    total_character_views = sum(sum(p['views'] for p in va_posts.get(va, [])) for va in vas)
    total_revenue = of_info['total_revenue']

    for va in vas:
        posts = va_posts.get(va, [])
        va_views = sum(p['views'] for p in posts)
        va_posts_count = len(posts)

        # Estimate revenue contribution based on view share
        revenue_contribution = (va_views / total_character_views * total_revenue) if total_character_views > 0 else 0

        # Get dashboard data
        dash_data = dashboard.get(va, {})
        male_avg = dash_data.get('male_avg', 0)
        us_avg = dash_data.get('us_avg', 0)

        va_revenue_contribution.append({
            'va': va,
            'character': character,
            'of_account': of_name,
            'posts': va_posts_count,
            'views': va_views,
            'revenue_contribution': revenue_contribution,
            'male_avg': male_avg,
            'us_avg': us_avg,
        })

# Sort by revenue contribution
va_revenue_contribution.sort(key=lambda x: x['revenue_contribution'], reverse=True)

print("\n🥇 TOP 20 VAs BY REVENUE CONTRIBUTION")
print("-" * 100)
print(f"{'Rank':<5} {'VA':<15} {'Character':<12} {'Revenue':<12} {'Views':<12} {'Posts':<8} {'Male%':<8} {'US%':<8}")
print("-" * 100)

for i, data in enumerate(va_revenue_contribution[:20], 1):
    print(f"{i:<5} {data['va']:<15} {data['character']:<12} ${data['revenue_contribution']:<11,.2f} {data['views']:<12,d} {data['posts']:<8d} {data['male_avg']*100:<7.1f}% {data['us_avg']*100:<7.1f}%")

# ============= SAVE DETAILED CSV =============
print("\n💾 Saving detailed analysis...")
with open('/Users/felixhergenroeder/onlyfans_roi_detailed.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['VA', 'Character', 'OF Account', 'Posts', 'Views', 'Revenue Contribution', 'Male%', 'US%', '$/1k Views'])

    for data in va_revenue_contribution:
        revenue_per_1k = (data['revenue_contribution'] / data['views'] * 1000) if data['views'] > 0 else 0
        writer.writerow([
            data['va'],
            data['character'],
            data['of_account'],
            data['posts'],
            data['views'],
            f"${data['revenue_contribution']:.2f}",
            f"{data['male_avg']*100:.1f}%",
            f"{data['us_avg']*100:.1f}%",
            f"${revenue_per_1k:.2f}",
        ])

print("✅ Saved to: /Users/felixhergenroeder/onlyfans_roi_detailed.csv")

# ============= KEY INSIGHTS =============
print("\n" + "=" * 100)
print("💡 KEY INSIGHTS")
print("=" * 100)

# Best converter
best_converter = min(roi_analysis, key=lambda x: x['views_per_sub'] if x['views_per_sub'] > 0 else float('inf'))
print(f"\n🏆 Best Converter: {best_converter['character']} ({best_converter['views_per_sub']:,.0f} views/sub)")

# Most revenue
most_revenue = max(roi_analysis, key=lambda x: x['total_revenue'])
print(f"💰 Most Revenue: {most_revenue['character']} (${most_revenue['total_revenue']:,.2f})")

# Best ROI
best_roi = max(roi_analysis, key=lambda x: x['revenue_per_1k_views'])
print(f"⚡ Best ROI: {best_roi['character']} (${best_roi['revenue_per_1k_views']:.2f}/1k views)")

print("\n🎯 Analysis Complete!")
