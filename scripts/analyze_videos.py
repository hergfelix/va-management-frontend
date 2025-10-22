import csv
from collections import defaultdict
from datetime import datetime

# Load Dashboard data (Account-level demographics)
dashboard_accounts = {}
with open('/Users/felixhergenroeder/Downloads/TT-Check 16_10 - TikTok Analytics Dashboard.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        account = row.get('Account', '').strip()
        if account and account not in ['TEAM TOTAL', 'OVERVIEW', '']:
            try:
                male_7d = float(row.get('Male% 7d', '0').replace('%', '')) / 100 if row.get('Male% 7d') else 0
                us_7d = float(row.get('US% 7d', '0').replace('%', '')) / 100 if row.get('US% 7d') else 0
                dashboard_accounts[account.lower()] = {
                    'male_7d': male_7d,
                    'us_7d': us_7d,
                    'account': account
                }
            except:
                pass

print(f"Loaded {len(dashboard_accounts)} accounts from dashboard")

# Load Video Metrics
videos_by_account = defaultdict(list)
total_videos = 0

with open('/Users/felixhergenroeder/Downloads/hi.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        author = row.get('author', '').strip().lower()
        try:
            views = int(row.get('playCount', 0))
            likes = int(row.get('diggCount', 0))
            comments = int(row.get('commentCount', 0))
            shares = int(row.get('shareCount', 0))
            
            video_data = {
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'engagement': likes + comments + shares,
                'url': row.get('post_url', ''),
                'created': row.get('createTimeISO', '')
            }
            
            videos_by_account[author].append(video_data)
            total_videos += 1
        except:
            pass

print(f"Loaded {total_videos} videos from {len(videos_by_account)} accounts\n")

# Match and analyze
matched = 0
unmatched_dashboard = []
unmatched_videos = []

analysis_results = []

for account_lower, demo_data in dashboard_accounts.items():
    if account_lower in videos_by_account:
        matched += 1
        videos = videos_by_account[account_lower]
        
        # Calculate video stats
        total_views = sum(v['views'] for v in videos)
        avg_views = total_views / len(videos) if videos else 0
        max_views = max(v['views'] for v in videos) if videos else 0
        
        analysis_results.append({
            'account': demo_data['account'],
            'male_7d': demo_data['male_7d'],
            'us_7d': demo_data['us_7d'],
            'video_count': len(videos),
            'total_views': total_views,
            'avg_views': avg_views,
            'max_views': max_views
        })
    else:
        unmatched_dashboard.append(demo_data['account'])

# Find accounts in videos but not in dashboard
for account in videos_by_account.keys():
    if account not in dashboard_accounts:
        unmatched_videos.append(account)

print(f"✅ Matched: {matched} accounts")
print(f"❌ In Dashboard but no videos: {len(unmatched_dashboard)}")
print(f"❌ Have videos but not in Dashboard: {len(unmatched_videos)}\n")

# Sort by different criteria
print("=" * 80)
print("TOP 10 ACCOUNTS BY AVERAGE VIEWS PER VIDEO")
print("=" * 80)
by_avg_views = sorted(analysis_results, key=lambda x: x['avg_views'], reverse=True)[:10]
for i, acc in enumerate(by_avg_views, 1):
    print(f"{i}. {acc['account']:<20} | Avg Views: {acc['avg_views']:>8,.0f} | Male: {acc['male_7d']*100:>5.1f}% | US: {acc['us_7d']*100:>5.1f}% | Videos: {acc['video_count']}")

print("\n" + "=" * 80)
print("ACCOUNTS WITH HIGH US% (>65%) - VIDEO PERFORMANCE")
print("=" * 80)
high_us = sorted([a for a in analysis_results if a['us_7d'] > 0.65], key=lambda x: x['avg_views'], reverse=True)
for i, acc in enumerate(high_us[:15], 1):
    print(f"{i}. {acc['account']:<20} | Avg Views: {acc['avg_views']:>8,.0f} | Male: {acc['male_7d']*100:>5.1f}% | US: {acc['us_7d']*100:>5.1f}% | Videos: {acc['video_count']}")

print("\n" + "=" * 80)
print("ACCOUNTS WITH LOW US% (<40%) - VIDEO PERFORMANCE")
print("=" * 80)
low_us = sorted([a for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0], key=lambda x: x['avg_views'], reverse=True)
for i, acc in enumerate(low_us[:15], 1):
    print(f"{i}. {acc['account']:<20} | Avg Views: {acc['avg_views']:>8,.0f} | Male: {acc['male_7d']*100:>5.1f}% | US: {acc['us_7d']*100:>5.1f}% | Videos: {acc['video_count']}")

print("\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)

# Calculate correlations
high_us_avg = sum(a['avg_views'] for a in analysis_results if a['us_7d'] > 0.65) / len([a for a in analysis_results if a['us_7d'] > 0.65]) if [a for a in analysis_results if a['us_7d'] > 0.65] else 0
low_us_avg = sum(a['avg_views'] for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0) / len([a for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0]) if [a for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0] else 0

print(f"High US% (>65%) accounts - Avg views per video: {high_us_avg:,.0f}")
print(f"Low US% (<40%) accounts - Avg views per video: {low_us_avg:,.0f}")
if high_us_avg > 0 and low_us_avg > 0:
    print(f"Difference: {((high_us_avg / low_us_avg - 1) * 100):.1f}% {'MORE' if high_us_avg > low_us_avg else 'LESS'} views for high US%")

print("\n" + "=" * 80)
print("PROXY CHANGE CANDIDATES (Low US%, Good Male%, Good Video Performance)")
print("=" * 80)
candidates = sorted([a for a in analysis_results if a['us_7d'] < 0.40 and a['male_7d'] > 0.85 and a['avg_views'] > 2000], key=lambda x: x['avg_views'], reverse=True)
for i, acc in enumerate(candidates, 1):
    print(f"{i}. {acc['account']:<20} | Avg Views: {acc['avg_views']:>8,.0f} | Male: {acc['male_7d']*100:>5.1f}% | US: {acc['us_7d']*100:>5.1f}% ⚠️ PROXY NEEDED")
