#!/usr/bin/env python3
"""
FINAL TIKTOK → ONLYFANS ANALYSIS
Simple, fast analysis of what actually drives revenue
"""

import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict

print("🎯 FINAL TIKTOK → ONLYFANS ANALYSIS")
print("=" * 80)

# ============= LOAD DATA =============
print("\n📂 Loading data...")

# Load TikTok posts
tiktok_posts = []
with open('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tiktok_posts.append({
            'date': row['created_date'],
            'account': row['account'].lower(),
            'va': row['va'],
            'views': int(row['views'] or 0),
            'engagement': int(row['engagement'] or 0),
            'engagement_rate': float(row['engagement_rate'] or 0),
        })

print(f"  ✅ {len(tiktok_posts):,} TikTok posts")

# Load OnlyFans revenue
OF_ACCOUNTS = {
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
                    if of_name in OF_ACCOUNTS:
                        if date_str not in daily_revenue:
                            daily_revenue[date_str] = {}
                        daily_revenue[date_str][of_name] = {
                            'new_subs': int(row.get('New Subs', 0) or 0),
                            'total_revenue': float(row.get('Total Revenue', 0) or 0),
                        }
        except:
            continue

print(f"  ✅ {len(revenue_files)} revenue CSVs loaded")

# ============= MAP POSTS TO CHARACTERS =============
character_posts = defaultdict(list)
for post in tiktok_posts:
    for of_account, character in OF_ACCOUNTS.items():
        if character.lower() in post['account']:
            character_posts[character].append(post)
            break

# ============= CALCULATE METRICS =============
print("\n📊 Calculating metrics...")

# LTV
sept_start = datetime(2025, 9, 1).date()
sept_end = datetime(2025, 9, 30).date()
sept_subs = 0
sept_revenue = 0

current = sept_start
while current <= sept_end:
    date_str = current.strftime("%Y-%m-%d")
    if date_str in daily_revenue:
        for of_account, data in daily_revenue[date_str].items():
            sept_subs += data['new_subs']
            sept_revenue += data['total_revenue']
    current += timedelta(days=1)

ltv = sept_revenue / sept_subs if sept_subs > 0 else 22.89

# Total revenue and subs by character
character_stats = {}
for character in OF_ACCOUNTS.values():
    posts = character_posts[character]
    total_views = sum(p['views'] for p in posts)

    # Get OnlyFans account name
    of_account = [k for k, v in OF_ACCOUNTS.items() if v == character][0]

    # Sum revenue and subs
    total_subs = 0
    total_revenue = 0
    for date_str, accounts in daily_revenue.items():
        if of_account in accounts:
            total_subs += accounts[of_account]['new_subs']
            total_revenue += accounts[of_account]['total_revenue']

    character_stats[character] = {
        'posts': len(posts),
        'total_views': total_views,
        'avg_views': total_views / len(posts) if posts else 0,
        'total_subs': total_subs,
        'total_revenue': total_revenue,
        'views_per_sub': total_views / total_subs if total_subs > 0 else 0,
        'revenue_per_1k_views': (total_revenue / total_views * 1000) if total_views > 0 else 0,
    }

# VA stats
va_stats = defaultdict(lambda: {'posts': 0, 'views': 0})
for post in tiktok_posts:
    if post['va']:
        va_stats[post['va']]['posts'] += 1
        va_stats[post['va']]['views'] += post['views']

# ============= SAVE REPORT =============
output = []

output.append("=" * 80)
output.append("🎯 FINAL TIKTOK → ONLYFANS ANALYSIS REPORT")
output.append("=" * 80)
output.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
output.append(f"Period: Mai 9 - Okt 17, 2025 (162 days)")
output.append(f"LTV per Sub: ${ltv:.2f}")

# CHARACTER PERFORMANCE
output.append("\n" + "=" * 80)
output.append("👥 CHARACTER PERFORMANCE")
output.append("=" * 80)

sorted_chars = sorted(character_stats.items(), key=lambda x: x[1]['total_revenue'], reverse=True)

output.append(f"\n{'Character':<12} {'Posts':>7} {'Total Views':>12} {'Subs':>6} {'Revenue':>12} {'Views/Sub':>10} {'$/1k Views':>11}")
output.append("-" * 80)

for character, stats in sorted_chars:
    output.append(f"{character:<12} {stats['posts']:>7,} {stats['total_views']:>12,} "
                 f"{stats['total_subs']:>6,} ${stats['total_revenue']:>11,.0f} "
                 f"{stats['views_per_sub']:>10,.0f} ${stats['revenue_per_1k_views']:>10.2f}")

# TOP VAs
output.append("\n" + "=" * 80)
output.append("🏆 TOP 15 VAs BY TOTAL VIEWS")
output.append("=" * 80)

sorted_vas = sorted(va_stats.items(), key=lambda x: x[1]['views'], reverse=True)[:15]

output.append(f"\n{'VA':<15} {'Posts':>7} {'Total Views':>12} {'Avg Views/Post':>15}")
output.append("-" * 80)

for va, stats in sorted_vas:
    avg_views = stats['views'] / stats['posts'] if stats['posts'] > 0 else 0
    output.append(f"{va:<15} {stats['posts']:>7,} {stats['views']:>12,} {avg_views:>15,.0f}")

# MONTHLY TRENDS
output.append("\n" + "=" * 80)
output.append("📈 MONTHLY REVENUE & SUBS TRENDS")
output.append("=" * 80)

monthly_data = defaultdict(lambda: {'subs': 0, 'revenue': 0})
for date_str, accounts in daily_revenue.items():
    month = date_str[:7]  # YYYY-MM
    for of_account, data in accounts.items():
        monthly_data[month]['subs'] += data['new_subs']
        monthly_data[month]['revenue'] += data['total_revenue']

output.append(f"\n{'Month':<10} {'New Subs':>10} {'Revenue':>12} {'Avg $/Sub':>12}")
output.append("-" * 80)

for month in sorted(monthly_data.keys()):
    data = monthly_data[month]
    avg_per_sub = data['revenue'] / data['subs'] if data['subs'] > 0 else 0
    output.append(f"{month:<10} {data['subs']:>10,} ${data['revenue']:>11,.0f} ${avg_per_sub:>11.2f}")

# VIEW BRACKETS
output.append("\n" + "=" * 80)
output.append("📊 POSTS BY VIEW BRACKET")
output.append("=" * 80)

view_brackets = [
    (0, 1000, "0-1k"),
    (1000, 5000, "1k-5k"),
    (5000, 10000, "5k-10k"),
    (10000, 50000, "10k-50k"),
    (50000, 100000, "50k-100k"),
    (100000, 500000, "100k-500k"),
    (500000, float('inf'), "500k+"),
]

bracket_stats = defaultdict(lambda: {'count': 0, 'total_views': 0})
for post in tiktok_posts:
    for min_v, max_v, label in view_brackets:
        if min_v <= post['views'] < max_v:
            bracket_stats[label]['count'] += 1
            bracket_stats[label]['total_views'] += post['views']
            break

output.append(f"\n{'Bracket':<12} {'Posts':>8} {'Total Views':>14} {'% of Total':>12}")
output.append("-" * 80)

total_all_views = sum(p['views'] for p in tiktok_posts)
for _, _, label in view_brackets:
    if label in bracket_stats:
        stats = bracket_stats[label]
        pct = (stats['total_views'] / total_all_views * 100) if total_all_views > 0 else 0
        output.append(f"{label:<12} {stats['count']:>8,} {stats['total_views']:>14,} {pct:>11.1f}%")

# KEY INSIGHTS
output.append("\n" + "=" * 80)
output.append("💡 KEY INSIGHTS")
output.append("=" * 80)

total_revenue = sum(s['total_revenue'] for s in character_stats.values())
total_subs = sum(s['total_subs'] for s in character_stats.values())

output.append(f"\n1. TOTAL ATTRIBUTION:")
output.append(f"   • Total Revenue: ${total_revenue:,.0f}")
output.append(f"   • Total New Subs: {total_subs:,}")
output.append(f"   • LTV per Sub: ${ltv:.2f}")

top_char = sorted_chars[0]
output.append(f"\n2. TOP PERFORMER:")
output.append(f"   • {top_char[0]} generates {top_char[1]['total_revenue']/total_revenue*100:.1f}% of total revenue")
output.append(f"   • {top_char[1]['total_subs']:,} subs from {top_char[1]['posts']:,} posts")
output.append(f"   • {top_char[1]['views_per_sub']:,.0f} views per sub (conversion rate)")

best_conversion = min(sorted_chars, key=lambda x: x[1]['views_per_sub'] if x[1]['views_per_sub'] > 0 else float('inf'))
output.append(f"\n3. BEST CONVERSION:")
output.append(f"   • {best_conversion[0]} has lowest views/sub: {best_conversion[1]['views_per_sub']:,.0f}")
output.append(f"   • ${best_conversion[1]['revenue_per_1k_views']:.2f} revenue per 1k views")

top_va = sorted_vas[0]
output.append(f"\n4. TOP VA:")
output.append(f"   • {top_va[0]} created {top_va[1]['posts']:,} posts")
output.append(f"   • Generated {top_va[1]['views']:,} total views")

# Find best month
best_month = max(monthly_data.items(), key=lambda x: x[1]['revenue'])
output.append(f"\n5. BEST MONTH:")
output.append(f"   • {best_month[0]}: ${best_month[1]['revenue']:,.0f} revenue")
output.append(f"   • {best_month[1]['subs']:,} new subs")

output.append("\n" + "=" * 80)
output.append("🎯 ANALYSIS COMPLETE")
output.append("=" * 80)

# Print to console
report_text = "\n".join(output)
print(report_text)

# Save to file
report_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/FINAL_ANALYSIS_REPORT.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"\n✅ Saved to: {report_file}")
