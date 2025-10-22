import csv
from collections import defaultdict

# Load Dashboard data - skip headers and group rows
dashboard_accounts = {}
with open('/Users/felixhergenroeder/Downloads/TT-Check 16_10 - TikTok Analytics Dashboard.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) > 5:
            account = parts[0].strip()
            # Skip if it's a header, team total, or employee row
            if account and account not in ['Account', 'TEAM TOTAL', 'OVERVIEW', ''] and not account.isupper():
                try:
                    male_7d_str = parts[2].replace('%', '').strip()
                    us_7d_str = parts[5].replace('%', '').strip()
                    
                    if male_7d_str and us_7d_str:
                        male_7d = float(male_7d_str) / 100
                        us_7d = float(us_7d_str) / 100
                        
                        dashboard_accounts[account.lower()] = {
                            'male_7d': male_7d,
                            'us_7d': us_7d,
                            'account': account
                        }
                except:
                    pass

print(f"✅ Loaded {len(dashboard_accounts)} accounts from dashboard")
print(f"Sample accounts: {list(dashboard_accounts.keys())[:5]}\n")

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

print(f"✅ Loaded {total_videos} videos from {len(videos_by_account)} unique accounts")
print(f"Sample video accounts: {list(videos_by_account.keys())[:5]}\n")

# Match and analyze
matched = 0
analysis_results = []

for account_lower, demo_data in dashboard_accounts.items():
    if account_lower in videos_by_account:
        matched += 1
        videos = videos_by_account[account_lower]
        
        # Calculate video stats
        total_views = sum(v['views'] for v in videos)
        avg_views = total_views / len(videos) if videos else 0
        max_views = max(v['views'] for v in videos) if videos else 0
        total_engagement = sum(v['engagement'] for v in videos)
        
        analysis_results.append({
            'account': demo_data['account'],
            'male_7d': demo_data['male_7d'],
            'us_7d': demo_data['us_7d'],
            'video_count': len(videos),
            'total_views': total_views,
            'avg_views': avg_views,
            'max_views': max_views,
            'total_engagement': total_engagement
        })

print(f"✅ Successfully matched: {matched} accounts\n")

if matched == 0:
    print("⚠️  No matches found. Checking for mismatches...")
    print("\nFirst 10 Dashboard accounts:")
    for acc in list(dashboard_accounts.keys())[:10]:
        print(f"  - {acc}")
    print("\nFirst 10 Video accounts:")
    for acc in list(videos_by_account.keys())[:10]:
        print(f"  - {acc}")
else:
    # Analysis
    print("=" * 90)
    print("🏆 TOP 10 ACCOUNTS BY AVERAGE VIEWS PER VIDEO")
    print("=" * 90)
    by_avg_views = sorted(analysis_results, key=lambda x: x['avg_views'], reverse=True)[:10]
    for i, acc in enumerate(by_avg_views, 1):
        print(f"{i:2d}. {acc['account']:<22} │ Avg Views: {acc['avg_views']:>8,.0f} │ Male: {acc['male_7d']*100:>5.1f}% │ US: {acc['us_7d']*100:>5.1f}% │ Videos: {acc['video_count']:>3d}")

    print("\n" + "=" * 90)
    print("✅ HIGH US% ACCOUNTS (>65%) - VIDEO PERFORMANCE")
    print("=" * 90)
    high_us = sorted([a for a in analysis_results if a['us_7d'] > 0.65], key=lambda x: x['avg_views'], reverse=True)
    for i, acc in enumerate(high_us[:12], 1):
        print(f"{i:2d}. {acc['account']:<22} │ Avg Views: {acc['avg_views']:>8,.0f} │ Male: {acc['male_7d']*100:>5.1f}% │ US: {acc['us_7d']*100:>5.1f}% │ Videos: {acc['video_count']:>3d}")

    print("\n" + "=" * 90)
    print("⚠️  LOW US% ACCOUNTS (<40%) - VIDEO PERFORMANCE")
    print("=" * 90)
    low_us = sorted([a for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0], key=lambda x: x['avg_views'], reverse=True)
    for i, acc in enumerate(low_us[:15], 1):
        print(f"{i:2d}. {acc['account']:<22} │ Avg Views: {acc['avg_views']:>8,.0f} │ Male: {acc['male_7d']*100:>5.1f}% │ US: {acc['us_7d']*100:>5.1f}% │ Videos: {acc['video_count']:>3d}")

    print("\n" + "=" * 90)
    print("📊 KEY INSIGHTS")
    print("=" * 90)

    high_us_accts = [a for a in analysis_results if a['us_7d'] > 0.65]
    low_us_accts = [a for a in analysis_results if a['us_7d'] < 0.40 and a['us_7d'] > 0]
    
    if high_us_accts:
        high_us_avg = sum(a['avg_views'] for a in high_us_accts) / len(high_us_accts)
        print(f"High US% (>65%) accounts: {len(high_us_accts)} accounts, Avg {high_us_avg:,.0f} views/video")
    
    if low_us_accts:
        low_us_avg = sum(a['avg_views'] for a in low_us_accts) / len(low_us_accts)
        print(f"Low US% (<40%) accounts: {len(low_us_accts)} accounts, Avg {low_us_avg:,.0f} views/video")
    
    if high_us_accts and low_us_accts:
        diff_pct = ((high_us_avg / low_us_avg - 1) * 100) if low_us_avg > 0 else 0
        print(f"\n💡 High US% accounts get {abs(diff_pct):.1f}% {'MORE' if diff_pct > 0 else 'LESS'} views on average!")

    print("\n" + "=" * 90)
    print("🎯 PROXY CHANGE PRIORITY LIST")
    print("   (Low US% + Good Male% + Decent Views)")
    print("=" * 90)
    candidates = sorted([a for a in analysis_results if a['us_7d'] < 0.40 and a['male_7d'] > 0.82 and a['avg_views'] > 1500], key=lambda x: x['avg_views'], reverse=True)
    for i, acc in enumerate(candidates, 1):
        print(f"🔴 {i:2d}. {acc['account']:<22} │ {acc['avg_views']:>8,.0f} views/video │ Male: {acc['male_7d']*100:.1f}% │ US: {acc['us_7d']*100:.1f}% │ {acc['video_count']} videos")
    
    if not candidates:
        print("No accounts match criteria (US<40%, Male>82%, Avg Views>1500)")
