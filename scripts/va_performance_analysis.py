#!/usr/bin/env python3
"""
VA Performance Analysis: Proxy vs. VA-Problem Detection
Analysiert Post-Performance über Zeit + Dashboard-Daten
"""

import csv
from collections import defaultdict
from datetime import datetime
import statistics

# ============= LOAD DASHBOARD DATA =============
print("📊 Loading Dashboard Data...")
dashboard = {}
with open('/Users/felixhergenroeder/Downloads/TT-Check 16_10 - TikTok Analytics Dashboard (1).csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    current_va = None

    for line in lines:
        parts = [p.strip() for p in line.strip().split(',')]

        # VA Header zeile (z.B. "CARLA,5 Accounts,Avg Male: 87.2%,Avg US: 34.6%")
        if len(parts) > 2 and "Accounts" in parts[1]:
            va_name = parts[0]
            if va_name and va_name not in ['TIKTOK ANALYTICS DASHBOARD', 'GOAL', 'Run refreshDashboard', 'OVERVIEW', 'TEAM TOTAL']:
                current_va = va_name

                # Extract Male% and US% from "Avg Male: 87.2%"
                male_avg = 0
                us_avg = 0

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

        # Account-Zeile (direkt nach VA header)
        elif current_va and len(parts) > 10:
            account = parts[0]
            if account and account not in ['Account', 'TEAM TOTAL', ''] and not account.isupper():
                try:
                    male_7d = float(parts[2].replace('%', '')) / 100 if parts[2] else 0
                    us_7d = float(parts[5].replace('%', '')) / 100 if parts[5] else 0
                    daily_avg_7d = int(parts[8].replace(',', '')) if parts[8] else 0

                    dashboard[current_va]['accounts'].append({
                        'name': account,
                        'male_7d': male_7d,
                        'us_7d': us_7d,
                        'daily_avg_7d': daily_avg_7d
                    })
                except:
                    pass

print(f"✅ Loaded {len(dashboard)} VAs from dashboard")
print(f"Sample VAs: {list(dashboard.keys())[:5]}\n")

# ============= LOAD METRICS LOG =============
print("📈 Loading Metrics Log (12,558 posts)...")
va_posts = defaultdict(list)

with open('/Users/felixhergenroeder/Downloads/Master-Proof-Log - Metrics_Log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        va = row.get('va', '').strip().upper()  # Normalize to UPPERCASE for matching

        if not va:
            continue

        try:
            post = {
                'url': row.get('post_url', ''),
                'account': row.get('author', ''),
                'views': int(row.get('playCount', 0) or 0),
                'likes': int(row.get('diggCount', 0) or 0),
                'comments': int(row.get('commentCount', 0) or 0),
                'shares': int(row.get('shareCount', 0) or 0),
                'created': row.get('createTimeISO', ''),
                'collected': row.get('collected_at', '')
            }

            post['engagement'] = post['likes'] + post['comments'] + post['shares']
            post['engagement_rate'] = (post['engagement'] / post['views'] * 100) if post['views'] > 0 else 0

            va_posts[va].append(post)
        except Exception as e:
            continue

print(f"✅ Loaded posts from {len(va_posts)} VAs")
print(f"Total posts: {sum(len(posts) for posts in va_posts.values())}\n")

# ============= ANALYZE VA PERFORMANCE =============
print("🔍 Analyzing VA Performance...\n")

va_analysis = []

for va_name in dashboard.keys():
    posts = va_posts.get(va_name, [])

    if not posts:
        continue

    # Calculate metrics
    total_views = sum(p['views'] for p in posts)
    avg_views = total_views / len(posts) if posts else 0
    median_views = statistics.median([p['views'] for p in posts]) if posts else 0
    max_views = max([p['views'] for p in posts]) if posts else 0

    total_engagement = sum(p['engagement'] for p in posts)
    avg_engagement_rate = statistics.mean([p['engagement_rate'] for p in posts]) if posts else 0

    # View distribution (consistency indicator)
    views_list = [p['views'] for p in posts]
    view_std = statistics.stdev(views_list) if len(views_list) > 1 else 0
    consistency_score = 1 - (view_std / avg_views) if avg_views > 0 else 0

    # Dashboard data
    dash_data = dashboard[va_name]
    male_avg = dash_data['male_avg']
    us_avg = dash_data['us_avg']

    # PROBLEM DETECTION
    problems = []
    root_cause = None
    priority = 0

    # 1. Proxy Problem: Low US% but decent Male% and Views
    if us_avg < 0.40 and male_avg > 0.80 and avg_views > 1500:
        problems.append("🔴 LOW US% - PROXY PROBLEM")
        root_cause = "PROXY"
        priority = 3  # High priority

    # 2. VA Problem: Good demographics but low views/engagement
    elif us_avg > 0.65 and male_avg > 0.85 and avg_views < 3000:
        problems.append("⚠️ LOW VIEWS despite GOOD DEMO - VA LAZY")
        root_cause = "VA"
        priority = 2  # Medium priority

    # 3. VA Problem: High view variance (inconsistent posting)
    elif consistency_score < 0.3 and avg_views < 5000:
        problems.append("📉 INCONSISTENT - VA RANDOM POSTS")
        root_cause = "VA"
        priority = 2

    # 4. Both Problems: Bad demographics AND bad performance
    elif us_avg < 0.40 and avg_views < 2000:
        problems.append("🔥 BAD PROXY + BAD VA")
        root_cause = "BOTH"
        priority = 3

    # 5. Good performance
    elif us_avg > 0.65 and avg_views > 5000:
        problems.append("✅ GOOD - Keep current setup")
        root_cause = "NONE"
        priority = 0

    va_analysis.append({
        'va': va_name,
        'posts_count': len(posts),
        'avg_views': avg_views,
        'median_views': median_views,
        'max_views': max_views,
        'avg_engagement_rate': avg_engagement_rate,
        'consistency_score': consistency_score,
        'male_avg': male_avg,
        'us_avg': us_avg,
        'problems': problems,
        'root_cause': root_cause,
        'priority': priority
    })

# Sort by priority
va_analysis.sort(key=lambda x: (x['priority'], -x['avg_views']), reverse=True)

# ============= PRINT ANALYSIS =============
print("=" * 120)
print("🔥 VA PERFORMANCE ANALYSIS - ROOT CAUSE DETECTION")
print("=" * 120)
print()

print("🚨 HIGH PRIORITY - PROXY CHANGES NEEDED (Low US% + Good Male% + Decent Views)")
print("-" * 120)
proxy_problems = [va for va in va_analysis if va['root_cause'] == 'PROXY']
for i, va in enumerate(proxy_problems[:15], 1):
    print(f"{i:2d}. {va['va']:<15} │ {va['avg_views']:>8,.0f} avg views │ Male: {va['male_avg']*100:>5.1f}% │ US: {va['us_avg']*100:>5.1f}% │ {va['posts_count']:>3d} posts │ Consistency: {va['consistency_score']:.2f}")

print("\n")
print("⚠️  VA PERFORMANCE ISSUES (Good Demo but Low Views/Engagement)")
print("-" * 120)
va_problems = [va for va in va_analysis if va['root_cause'] == 'VA']
for i, va in enumerate(va_problems[:15], 1):
    print(f"{i:2d}. {va['va']:<15} │ {va['avg_views']:>8,.0f} avg views │ Male: {va['male_avg']*100:>5.1f}% │ US: {va['us_avg']*100:>5.1f}% │ {va['posts_count']:>3d} posts │ Engagement: {va['avg_engagement_rate']:.2f}%")

print("\n")
print("🔥 BOTH PROBLEMS (Bad Proxy + Lazy VA)")
print("-" * 120)
both_problems = [va for va in va_analysis if va['root_cause'] == 'BOTH']
for i, va in enumerate(both_problems[:15], 1):
    print(f"{i:2d}. {va['va']:<15} │ {va['avg_views']:>8,.0f} avg views │ Male: {va['male_avg']*100:>5.1f}% │ US: {va['us_avg']*100:>5.1f}% │ {va['posts_count']:>3d} posts │ ACTION: Proxy + Coach/Replace")

print("\n")
print("✅ TOP PERFORMERS (Keep Current Setup)")
print("-" * 120)
good_performers = [va for va in va_analysis if va['root_cause'] == 'NONE']
for i, va in enumerate(good_performers[:10], 1):
    print(f"{i:2d}. {va['va']:<15} │ {va['avg_views']:>8,.0f} avg views │ Male: {va['male_avg']*100:>5.1f}% │ US: {va['us_avg']*100:>5.1f}% │ {va['posts_count']:>3d} posts │ Consistency: {va['consistency_score']:.2f}")

# ============= SUMMARY STATS =============
print("\n")
print("=" * 120)
print("📊 SUMMARY STATISTICS")
print("=" * 120)
print(f"Total VAs analyzed: {len(va_analysis)}")
print(f"🔴 Proxy Problems: {len(proxy_problems)} VAs")
print(f"⚠️  VA Performance Issues: {len(va_problems)} VAs")
print(f"🔥 Both Problems: {len(both_problems)} VAs")
print(f"✅ Good Performers: {len(good_performers)} VAs")
print()

# Save detailed CSV for further analysis
print("💾 Saving detailed analysis to CSV...")
with open('/Users/felixhergenroeder/va_performance_detailed.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['VA', 'Posts', 'Avg Views', 'Median Views', 'Max Views', 'Engagement Rate', 'Consistency', 'Male%', 'US%', 'Root Cause', 'Priority', 'Problems'])

    for va in va_analysis:
        writer.writerow([
            va['va'],
            va['posts_count'],
            f"{va['avg_views']:.0f}",
            f"{va['median_views']:.0f}",
            f"{va['max_views']:.0f}",
            f"{va['avg_engagement_rate']:.2f}%",
            f"{va['consistency_score']:.2f}",
            f"{va['male_avg']*100:.1f}%",
            f"{va['us_avg']*100:.1f}%",
            va['root_cause'],
            va['priority'],
            ' | '.join(va['problems'])
        ])

print("✅ Saved to: /Users/felixhergenroeder/va_performance_detailed.csv")
print("\n🎯 Analysis complete!")
