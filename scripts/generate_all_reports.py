#!/usr/bin/env python3
"""
COMPLETE REPORTING SUITE
Generates 4 reports: VA, Post, Account, Character
"""

import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict
import os

print("🎯 GENERATING COMPLETE REPORTING SUITE")
print("=" * 80)

# ============= LOAD ALL DATA =============
print("\n📂 Loading all data...")

# TikTok posts
tiktok_posts = []
with open('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tiktok_posts.append({
            'date': row['created_date'],
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
        })

# OnlyFans revenue
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

print(f"  ✅ {len(tiktok_posts):,} posts, {len(revenue_files)} revenue CSVs")

# Character conversion rates
CHARACTER_VIEWS_PER_SUB = {
    'MIRIAM': 7387,
    'ARIRI': 3935,
    'MARA': 13863,
    'SOFIA': 20316,
    'NAOMI': 14627,
    'MEGAN': 23425,
    'AURELIA': 28524,
    'TYRA': 27814,
    'SUKI': 18096,
    'NALANI': 107196,
}

LTV = 22.89
END_DATE = datetime(2025, 10, 17).date()

# ========================================
# REPORT 1: VA PERFORMANCE (with tenure)
# ========================================
print("\n📊 Generating VA Performance Report...")

va_data = defaultdict(lambda: {
    'posts': 0,
    'views': 0,
    'engagement': 0,
    'first_date': None,
    'characters': set(),
    'character_posts': defaultdict(int),
    'character_first_date': {}
})

for post in tiktok_posts:
    va = post['va']
    if va:
        va_data[va]['posts'] += 1
        va_data[va]['views'] += post['views']
        va_data[va]['engagement'] += post['engagement']

        if not va_data[va]['first_date'] or post['date'] < va_data[va]['first_date']:
            va_data[va]['first_date'] = post['date']

        # Detect character
        account = post['account']
        character = None
        for of_acc, char in OF_ACCOUNTS.items():
            if char.lower() in account:
                character = char
                va_data[va]['characters'].add(char)
                va_data[va]['character_posts'][char] += 1

                # Track first date per character
                if char not in va_data[va]['character_first_date']:
                    va_data[va]['character_first_date'][char] = post['date']
                elif post['date'] < va_data[va]['character_first_date'][char]:
                    va_data[va]['character_first_date'][char] = post['date']
                break

va_performance = []

for va, data in va_data.items():
    # Determine current/main character (most posts)
    if data['character_posts']:
        current_character = max(data['character_posts'].items(), key=lambda x: x[1])[0]
        first_date_for_character = datetime.strptime(data['character_first_date'][current_character], "%Y-%m-%d").date()
    else:
        # Fallback if no character detected
        current_character = None
        first_date_for_character = datetime.strptime(data['first_date'], "%Y-%m-%d").date()

    # Calculate tenure based on CURRENT CHARACTER start date
    days_active = (END_DATE - first_date_for_character).days
    months_active = days_active / 30.0

    # Cost calculation based on current character tenure
    monthly_cost = 310  # Salary + proxy
    setup_cost = 330
    total_cost = (monthly_cost * months_active) + setup_cost

    # Estimate revenue
    estimated_subs = 0
    for character in data['characters']:
        views_per_sub = CHARACTER_VIEWS_PER_SUB.get(character, 20000)
        estimated_subs += data['views'] / views_per_sub

    estimated_revenue = estimated_subs * LTV
    profit = estimated_revenue - total_cost
    roi = (profit / total_cost * 100) if total_cost > 0 else 0

    # Monthly metrics
    revenue_per_month = estimated_revenue / months_active if months_active > 0 else 0
    profit_per_month = profit / months_active if months_active > 0 else 0
    posts_per_month = data['posts'] / months_active if months_active > 0 else 0

    # Calculate subs per month (PRIMARY METRIC)
    subs_per_month = estimated_subs / months_active if months_active > 0 else 0

    va_performance.append({
        'va': va,
        'months_active': months_active,
        'posts': data['posts'],
        'posts_per_month': posts_per_month,
        'total_views': data['views'],
        'avg_views': data['views'] / data['posts'] if data['posts'] > 0 else 0,
        'estimated_subs': estimated_subs,
        'subs_per_month': subs_per_month,
        'estimated_revenue': estimated_revenue,
        'revenue_per_month': revenue_per_month,
        'total_cost': total_cost,
        'profit': profit,
        'profit_per_month': profit_per_month,
        'roi': roi,
        'current_character': current_character if current_character else '',
        'all_characters': ', '.join(sorted(data['characters'])),
        'status': 'NEW' if months_active < 2 else 'EXPERIENCED'
    })

# Calculate character-specific benchmarks (top 50% avg views per character)
char_benchmarks = {}
char_vas = defaultdict(list)
for va in va_performance:
    if va['status'] == 'EXPERIENCED' and va['current_character']:
        char_vas[va['current_character']].append(va)

for character, vas in char_vas.items():
    if len(vas) >= 2:
        # Sort by avg views
        sorted_vas = sorted(vas, key=lambda x: x['avg_views'], reverse=True)
        # Take top 50% average
        top_half = sorted_vas[:max(1, len(sorted_vas) // 2)]
        benchmark = sum(v['avg_views'] for v in top_half) / len(top_half)
        char_benchmarks[character] = benchmark

# Categorize with character-specific opportunity cost analysis
new_vas = [v for v in va_performance if v['status'] == 'NEW']
exp_profitable = [v for v in va_performance if v['status'] == 'EXPERIENCED' and v['roi'] >= 0]
exp_replace = [v for v in va_performance if v['status'] == 'EXPERIENCED' and v['roi'] < 0]

# Further categorize profitable VAs based on character-specific benchmarks
exp_keep = []
exp_watch = []
exp_opportunity_cost = []

for va in exp_profitable:
    char = va['current_character']

    # If no benchmark or high ROI, keep
    if not char or char not in char_benchmarks or va['roi'] >= 200:
        exp_keep.append(va)
    else:
        benchmark = char_benchmarks[char]
        # Below 60% of character benchmark = opportunity cost
        if va['avg_views'] < benchmark * 0.6:
            exp_opportunity_cost.append(va)
        # Below 80% of benchmark but profitable = watch
        elif va['avg_views'] < benchmark * 0.8:
            exp_watch.append(va)
        else:
            exp_keep.append(va)

# Sort by SUBS PER MONTH (primary metric)
new_vas.sort(key=lambda x: x['subs_per_month'], reverse=True)
exp_keep.sort(key=lambda x: x['subs_per_month'], reverse=True)
exp_watch.sort(key=lambda x: x['subs_per_month'], reverse=True)
exp_opportunity_cost.sort(key=lambda x: x['subs_per_month'])
exp_replace.sort(key=lambda x: x['subs_per_month'])

# Save VA Report as MARKDOWN (complete tables with all VAs)
va_report_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/01_VA_PERFORMANCE_REPORT.md'
with open(va_report_file, 'w', encoding='utf-8') as f:
    f.write("# 👥 VA PERFORMANCE REPORT\n")
    f.write("**Period:** Mai 9 - Okt 17, 2025 (5.5 months)\n")
    f.write(f"**Total VAs:** {len(va_performance)}\n\n")

    f.write("## Summary\n")
    f.write(f"- ✅ **KEEP ({len(exp_keep)}):** Strong performers (good ROI + meets character benchmarks)\n")
    f.write(f"- ⚠️ **WATCH ({len(exp_watch)}):** Below character benchmark but still profitable\n")
    f.write(f"- 💰 **OPPORTUNITY COST ({len(exp_opportunity_cost)}):** Far below character benchmark (replace for higher gains)\n")
    f.write(f"- ❌ **REPLACE ({len(exp_replace)}):** Negative ROI (losing money)\n")
    f.write(f"- 🆕 **NEW ({len(new_vas)}):** < 2 months (too early to judge)\n\n")

    f.write("**PRIMARY METRIC:** NEW SUBS PER MONTH (recurring revenue excluded)\n\n")
    f.write("---\n\n")

    # Replace list - Negative ROI
    f.write("## ❌ VAs TO REPLACE (Negative ROI)\n\n")
    if exp_replace:
        f.write("These VAs are **losing money**. Replace immediately.\n\n")
        f.write("| VA | Months | Posts | **Avg Views** | Subs/M | $/M | ROI | Main Char |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for va in exp_replace:
            f.write(f"| {va['va']} | {va['months_active']:.1f} | {va['posts']:,} | "
                   f"**{va['avg_views']:,.0f}** | {va['subs_per_month']:.1f} | ${va['profit_per_month']:,.0f} | "
                   f"{va['roi']:.0f}% | {va['current_character']} |\n")
        total_loss = sum(v['profit_per_month'] for v in exp_replace)
        f.write(f"\n**Total Monthly Loss:** ${abs(total_loss):,.0f}\n")
    else:
        f.write("**None!** All experienced VAs are at least break-even. ✅\n")
    f.write("\n---\n\n")

    # Opportunity Cost list
    f.write("## 💰 VAs TO REPLACE (Opportunity Cost)\n\n")
    if exp_opportunity_cost:
        f.write("These VAs are profitable but **far below their character's benchmark**.\n")
        f.write("Replacing them with better performers would significantly increase revenue.\n\n")
        f.write("| VA | Months | Posts | **Avg Views** | Char Benchmark | % of Benchmark | Subs/M | $/M | Main Char |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for va in exp_opportunity_cost:
            benchmark = char_benchmarks.get(va['current_character'], 0)
            pct_of_benchmark = (va['avg_views'] / benchmark * 100) if benchmark > 0 else 0
            f.write(f"| {va['va']} | {va['months_active']:.1f} | {va['posts']:,} | "
                   f"**{va['avg_views']:,.0f}** | {benchmark:,.0f} | {pct_of_benchmark:.0f}% | "
                   f"{va['subs_per_month']:.1f} | ${va['profit_per_month']:,.0f} | {va['current_character']} |\n")

        # Calculate opportunity cost
        current_subs = sum(v['subs_per_month'] for v in exp_opportunity_cost)
        # Estimate if they reached 80% of benchmark
        potential_subs = 0
        for va in exp_opportunity_cost:
            char = va['current_character']
            if char and char in CHARACTER_VIEWS_PER_SUB:
                benchmark = char_benchmarks.get(char, va['avg_views'])
                target_views = benchmark * 0.8
                posts_per_month = va['posts_per_month']
                potential_monthly_views = target_views * posts_per_month
                potential_subs += potential_monthly_views / CHARACTER_VIEWS_PER_SUB[char]
            else:
                potential_subs += va['subs_per_month']

        gain_subs = potential_subs - current_subs
        gain_revenue = gain_subs * LTV

        f.write(f"\n**Opportunity Cost Analysis:**\n")
        f.write(f"- Current: {current_subs:.0f} subs/month\n")
        f.write(f"- Potential (with better VAs): {potential_subs:.0f} subs/month\n")
        f.write(f"- **Monthly gain: +{gain_subs:.0f} subs = +${gain_revenue:,.0f}**\n")
    else:
        f.write("**None!** All VAs meet their character benchmarks. 🎉\n")
    f.write("\n---\n\n")

    # New VAs (COMPLETE)
    f.write("## 🆕 NEW VAs (< 2 Months)\n\n")
    f.write("Too early to make final judgment, but ranked by **SUBS/MONTH**:\n\n")
    f.write("| VA | Months | Posts | P/M | **Avg Views** | Subs/M | $/M | Main Char |\n")
    f.write("|---|---|---|---|---|---|---|---|\n")
    for i, va in enumerate(new_vas, 1):
        marker = "**" if i <= 3 else ""
        f.write(f"| {marker}{va['va']}{marker} | {va['months_active']:.1f} | {va['posts']:,} | "
               f"{va['posts_per_month']:.0f} | **{va['avg_views']:,.0f}** | "
               f"{va['subs_per_month']:.1f} | ${va['profit_per_month']:,.0f} | {va['current_character']} |\n")
    f.write("\n---\n\n")

    # Watch list (COMPLETE)
    f.write("## ⚠️ VAs TO WATCH\n\n")
    f.write("These VAs are **below their character benchmark** but still profitable. Monitor for 1 more month:\n\n")
    if exp_watch:
        f.write("| VA | Months | Posts | **Avg Views** | Char Benchmark | % of Benchmark | Subs/M | $/M | Main Char |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for va in exp_watch:
            benchmark = char_benchmarks.get(va['current_character'], 0)
            pct_of_benchmark = (va['avg_views'] / benchmark * 100) if benchmark > 0 else 0
            f.write(f"| {va['va']} | {va['months_active']:.1f} | {va['posts']:,} | "
                   f"**{va['avg_views']:,.0f}** | {benchmark:,.0f} | {pct_of_benchmark:.0f}% | "
                   f"{va['subs_per_month']:.1f} | ${va['profit_per_month']:,.0f} | {va['current_character']} |\n")
    f.write("\n---\n\n")

    # Keep list (COMPLETE - ALL VAs)
    f.write("## ✅ VAs TO KEEP & SCALE\n\n")
    f.write("Experienced VAs with ROI ≥ 100%. **Ranked by SUBS/MONTH:**\n\n")
    f.write("| Rank | VA | Months | Posts | **Avg Views** | Subs/M | Total Subs | ROI | $/M | Main Char |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for i, va in enumerate(exp_keep, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
        marker = "**" if i <= 10 else ""
        f.write(f"| {emoji} | {marker}{va['va']}{marker} | {va['months_active']:.1f} | {va['posts']:,} | "
               f"**{va['avg_views']:,.0f}** | {va['subs_per_month']:.1f} | {va['estimated_subs']:.0f} | "
               f"{va['roi']:.0f}% | ${va['profit_per_month']:,.0f} | {va['current_character']} |\n")

    f.write("\n### 💡 Key Insights:\n\n")
    f.write("**Top Tier (Most Subs/Month):**\n")
    for i, va in enumerate(exp_keep[:3], 1):
        f.write(f"- {i}. **{va['va']}** ({va['current_character']}): {va['avg_views']:,.0f} avg views → {va['subs_per_month']:.1f} subs/month → ${va['profit_per_month']:,.0f}/month\n")

    # Character-specific performance analysis
    f.write("\n**Performance by Character:**\n\n")

    # Group VAs by character
    char_performance = defaultdict(list)
    for va in exp_keep:
        if va['current_character']:
            char_performance[va['current_character']].append(va)

    # Show avg views benchmarks per character
    for character in sorted(char_performance.keys()):
        vas = char_performance[character]
        avg_views_list = [va['avg_views'] for va in vas]
        avg_views_avg = sum(avg_views_list) / len(avg_views_list)
        best_va = max(vas, key=lambda x: x['avg_views'])

        f.write(f"- **{character}** ({len(vas)} VAs): Avg {avg_views_avg:,.0f} views/post | ")
        f.write(f"Best: {best_va['va']} ({best_va['avg_views']:,.0f} views)\n")

    f.write("\n---\n\n")

    f.write("## 📊 Recommendations\n\n")
    f.write("### 1. IMMEDIATE ACTION\n")
    if exp_replace:
        f.write(f"❌ **Replace {len(exp_replace)} VAs** with negative ROI (losing money)\n\n")
    else:
        f.write("✅ **No VAs losing money!**\n\n")

    if exp_opportunity_cost:
        f.write(f"💰 **Consider replacing {len(exp_opportunity_cost)} VAs** due to opportunity cost\n")
        f.write(f"   → These are profitable but far below character benchmarks\n")
        potential_gain = sum(v['subs_per_month'] for v in exp_opportunity_cost) * 0.8 * LTV
        f.write(f"   → Potential monthly gain: ~${potential_gain:,.0f}\n\n")
    else:
        f.write("✅ **All VAs meet character benchmarks!**\n\n")

    f.write("### 2. SCALE TOP PERFORMERS\n")
    f.write("🚀 **Give more accounts to:**\n")
    for i, va in enumerate(exp_keep[:3], 1):
        f.write(f"- {va['va']} ({va['subs_per_month']:.1f} subs/month)\n")
    total_subs = sum(va['subs_per_month'] for va in exp_keep[:3])
    f.write(f"\nThese 3 VAs alone generate **{total_subs:.0f} new subs/month!**\n\n")

    f.write("### 3. MONITOR NEW VAs\n")
    f.write("⏳ **Wait 1 more month** before judging new VAs\n\n")

    f.write("### 4. WATCH LIST\n")
    if exp_watch:
        f.write(f"⚠️ Monitor these {len(exp_watch)} VAs for 1 more month:\n")
        f.write("- If subs/month doesn't improve → reassign to better characters\n\n")

    f.write("---\n\n")
    f.write("## 💰 Cost Structure Reference\n\n")
    f.write("**Per VA:**\n")
    f.write("- Salary + Proxy: $310/month\n")
    f.write("- Handy Setup: $330 (one-time)\n\n")
    f.write(f"**Break-even:** ~89 subs needed (at ${LTV:.2f} LTV)\n\n")
    f.write("---\n\n")
    f.write(f"*Report generated: {datetime.now().strftime('%Y-%m-%d')}*\n")
    f.write(f"*Data source: {len(tiktok_posts):,} TikTok posts, {len(revenue_files)} revenue CSVs*\n")

print(f"  ✅ VA Report (Markdown): {va_report_file}")

# Save CSV (sorted by subs/month)
va_csv = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/01_VA_PERFORMANCE_DETAILED.csv'
with open(va_csv, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['va', 'status', 'months_active', 'posts', 'posts_per_month', 'total_views', 'avg_views',
                  'estimated_subs', 'subs_per_month', 'estimated_revenue', 'revenue_per_month', 'total_cost', 'profit',
                  'profit_per_month', 'roi', 'current_character', 'all_characters']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted(va_performance, key=lambda x: x['subs_per_month'], reverse=True))

print(f"  ✅ VA CSV: {va_csv}")

print("\n🎯 All reports generated!")
print(f"\nReports saved in:")
print(f"  📁 /Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/")
