#!/usr/bin/env python3
"""
VA PERFORMANCE REPORT
Identifies which VAs should be replaced based on ROI
"""

import csv
from collections import defaultdict

print("🎯 VA PERFORMANCE REPORT - WHO TO REPLACE?")
print("=" * 80)

# ============= COSTS =============
VA_MONTHLY_SALARY = 300  # $300/month per VA
HANDY_SETUP = 330        # $330 one-time
PROXY_MONTHLY = 10       # $10/month
MONTHS_ACTIVE = 5.5      # Mai 9 - Okt 17 = ~5.5 months

MONTHLY_COST_PER_VA = VA_MONTHLY_SALARY + PROXY_MONTHLY  # $310/month
TOTAL_COST_PER_VA = (MONTHLY_COST_PER_VA * MONTHS_ACTIVE) + HANDY_SETUP  # $2,035

BREAK_EVEN_SUBS = TOTAL_COST_PER_VA / 22.89  # Need ~89 subs to break even

print(f"\n💰 COST STRUCTURE:")
print(f"  • VA Salary: ${VA_MONTHLY_SALARY}/month")
print(f"  • Proxy: ${PROXY_MONTHLY}/month")
print(f"  • Handy Setup: ${HANDY_SETUP} (one-time)")
print(f"  • Total Cost (5.5 months): ${TOTAL_COST_PER_VA:,.0f}")
print(f"  • Break-even: {BREAK_EVEN_SUBS:.0f} subs needed")

# ============= LOAD DATA =============
print(f"\n📂 Loading data...")

# Load TikTok posts
va_posts = defaultdict(lambda: {
    'posts': 0,
    'total_views': 0,
    'total_engagement': 0,
    'characters': set()
})

with open('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        va = row['va']
        if va:
            va_posts[va]['posts'] += 1
            va_posts[va]['total_views'] += int(row['views'] or 0)
            va_posts[va]['total_engagement'] += int(row['engagement'] or 0)

            # Detect character
            account = row['account'].lower()
            if 'miriam' in account:
                va_posts[va]['characters'].add('MIRIAM')
            elif 'aurelia' in account:
                va_posts[va]['characters'].add('AURELIA')
            elif 'sofia' in account:
                va_posts[va]['characters'].add('SOFIA')
            elif 'naomi' in account:
                va_posts[va]['characters'].add('NAOMI')
            elif 'mara' in account:
                va_posts[va]['characters'].add('MARA')
            elif 'megan' in account:
                va_posts[va]['characters'].add('MEGAN')
            elif 'tyra' in account:
                va_posts[va]['characters'].add('TYRA')
            elif 'suki' in account:
                va_posts[va]['characters'].add('SUKI')
            elif 'nalani' in account:
                va_posts[va]['characters'].add('NALANI')
            elif 'mika' in account or 'mira' in account:
                va_posts[va]['characters'].add('MIKA/MIRA')
            elif 'ellie' in account:
                va_posts[va]['characters'].add('ELLIE')
            elif 'ari' in account:
                va_posts[va]['characters'].add('ARIRI')

print(f"  ✅ Loaded data for {len(va_posts)} VAs")

# ============= CALCULATE METRICS =============
print(f"\n📊 Calculating VA performance...")

# Character conversion rates (from previous analysis)
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
    'MIKA/MIRA': 20000,  # estimate
    'ELLIE': 20000,      # estimate
}

LTV = 22.89

va_performance = []

for va, data in va_posts.items():
    # Estimate attributed subs based on character mix
    estimated_subs = 0
    for character in data['characters']:
        views_per_sub = CHARACTER_VIEWS_PER_SUB.get(character, 20000)
        char_subs = data['total_views'] / views_per_sub
        estimated_subs += char_subs

    estimated_revenue = estimated_subs * LTV

    roi = ((estimated_revenue - TOTAL_COST_PER_VA) / TOTAL_COST_PER_VA * 100) if TOTAL_COST_PER_VA > 0 else 0
    profit = estimated_revenue - TOTAL_COST_PER_VA

    avg_views_per_post = data['total_views'] / data['posts'] if data['posts'] > 0 else 0
    engagement_rate = (data['total_engagement'] / data['total_views'] * 100) if data['total_views'] > 0 else 0

    va_performance.append({
        'va': va,
        'posts': data['posts'],
        'total_views': data['total_views'],
        'avg_views': avg_views_per_post,
        'engagement_rate': engagement_rate,
        'estimated_subs': estimated_subs,
        'estimated_revenue': estimated_revenue,
        'cost': TOTAL_COST_PER_VA,
        'profit': profit,
        'roi': roi,
        'characters': ', '.join(sorted(data['characters'])),
    })

# Sort by ROI
va_performance.sort(key=lambda x: x['roi'], reverse=True)

# ============= CATEGORIZE VAs =============
print(f"\n🎯 Categorizing VAs...")

keep_vas = []
watch_vas = []
replace_vas = []

for va in va_performance:
    if va['roi'] >= 100:  # 100%+ ROI = Keep
        keep_vas.append(va)
    elif va['roi'] >= 0:  # Break-even to 100% = Watch
        watch_vas.append(va)
    else:  # Negative ROI = Replace
        replace_vas.append(va)

# ============= GENERATE REPORT =============
output = []

output.append("=" * 100)
output.append("🎯 VA PERFORMANCE REPORT - WHO TO REPLACE?")
output.append("=" * 100)
output.append(f"\nPeriod: Mai 9 - Okt 17, 2025 (5.5 months)")
output.append(f"Total VAs: {len(va_performance)}")
output.append(f"  • ✅ KEEP ({len(keep_vas)}): ROI ≥ 100%")
output.append(f"  • ⚠️  WATCH ({len(watch_vas)}): ROI 0-100%")
output.append(f"  • ❌ REPLACE ({len(replace_vas)}): ROI < 0%")

# REPLACE LIST
output.append("\n" + "=" * 100)
output.append("❌ VAs TO REPLACE (Negative ROI)")
output.append("=" * 100)

if replace_vas:
    output.append(f"\n{'VA':<15} {'Posts':>6} {'Avg Views':>10} {'Est Subs':>9} {'Est Rev':>10} {'ROI':>8} {'Characters':<20}")
    output.append("-" * 100)

    for va in replace_vas:
        output.append(f"{va['va']:<15} {va['posts']:>6,} {va['avg_views']:>10,.0f} "
                     f"{va['estimated_subs']:>9.1f} ${va['estimated_revenue']:>9,.0f} "
                     f"{va['roi']:>7.0f}% {va['characters']:<20}")

    total_loss = sum(va['profit'] for va in replace_vas)
    output.append(f"\nTotal Loss from Replace VAs: ${abs(total_loss):,.0f}")
else:
    output.append("\n✅ No VAs with negative ROI!")

# WATCH LIST
output.append("\n" + "=" * 100)
output.append("⚠️  VAs TO WATCH (Low ROI 0-100%)")
output.append("=" * 100)

if watch_vas:
    output.append(f"\n{'VA':<15} {'Posts':>6} {'Avg Views':>10} {'Est Subs':>9} {'Est Rev':>10} {'ROI':>8} {'Characters':<20}")
    output.append("-" * 100)

    for va in watch_vas:
        output.append(f"{va['va']:<15} {va['posts']:>6,} {va['avg_views']:>10,.0f} "
                     f"{va['estimated_subs']:>9.1f} ${va['estimated_revenue']:>9,.0f} "
                     f"{va['roi']:>7.0f}% {va['characters']:<20}")
else:
    output.append("\n✅ All VAs are either excellent or need replacement!")

# KEEP LIST (Top 15)
output.append("\n" + "=" * 100)
output.append("✅ TOP 15 VAs TO KEEP (ROI ≥ 100%)")
output.append("=" * 100)

output.append(f"\n{'VA':<15} {'Posts':>6} {'Avg Views':>10} {'Est Subs':>9} {'Est Rev':>10} {'ROI':>8} {'Profit':>10} {'Characters':<20}")
output.append("-" * 100)

for va in keep_vas[:15]:
    output.append(f"{va['va']:<15} {va['posts']:>6,} {va['avg_views']:>10,.0f} "
                 f"{va['estimated_subs']:>9.1f} ${va['estimated_revenue']:>9,.0f} "
                 f"{va['roi']:>7.0f}% ${va['profit']:>9,.0f} {va['characters']:<20}")

# SUMMARY
output.append("\n" + "=" * 100)
output.append("💡 RECOMMENDATIONS")
output.append("=" * 100)

output.append(f"\n1. IMMEDIATE ACTION:")
if replace_vas:
    output.append(f"   ❌ Replace {len(replace_vas)} VAs with negative ROI")
    output.append(f"   💸 This will save ${abs(sum(va['profit'] for va in replace_vas)):,.0f} in losses")
else:
    output.append(f"   ✅ No immediate replacements needed!")

output.append(f"\n2. MONITOR CLOSELY:")
if watch_vas:
    output.append(f"   ⚠️  {len(watch_vas)} VAs are break-even or low ROI")
    output.append(f"   📊 Give them 1 more month, then re-evaluate")
else:
    output.append(f"   ✅ All performing VAs have strong ROI!")

output.append(f"\n3. SCALE UP:")
if keep_vas:
    output.append(f"   ✅ {len(keep_vas)} VAs with 100%+ ROI")
    output.append(f"   🚀 Consider giving top performers more accounts")

    # Top 3
    output.append(f"\n   Top 3 Performers:")
    for i, va in enumerate(keep_vas[:3], 1):
        output.append(f"   {i}. {va['va']}: {va['roi']:.0f}% ROI, ${va['profit']:,.0f} profit")

output.append("\n" + "=" * 100)

# Print to console
report_text = "\n".join(output)
print(report_text)

# Save to file
report_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/VA_REPLACEMENT_REPORT.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"\n✅ Saved to: {report_file}")

# Also save as CSV for easy sorting
csv_file = '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/VA_PERFORMANCE_DETAILED.csv'
with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['va', 'posts', 'total_views', 'avg_views', 'engagement_rate',
                  'estimated_subs', 'estimated_revenue', 'cost', 'profit', 'roi', 'characters']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(va_performance)

print(f"✅ CSV saved to: {csv_file}")
