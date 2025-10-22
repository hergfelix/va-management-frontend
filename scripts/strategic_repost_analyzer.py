#!/usr/bin/env python3
"""
Strategic Repost Analyzer
Identifies if VAs are posting strategically (recycling viral content) or randomly

Output: Per account, show:
- All reposts in October
- Original post performance
- Whether it was viral before reposting
- Timeline: when did it go viral, when was it reposted
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_all_data(database_path):
    """Load ALL data (not just October) to find post history"""
    print("📊 Loading FULL database (all months)...")
    print("   This may take a moment (32MB file)...\n")

    df = pd.read_csv(database_path, quotechar='"', escapechar='\\')
    df['created_date'] = pd.to_datetime(df['created_date'])

    print(f"✅ Loaded {len(df):,} total posts")
    print(f"   Date range: {df['created_date'].min()} to {df['created_date'].max()}")
    print(f"   VAs: {df['va'].nunique()}")
    print(f"   Accounts: {df['account'].nunique()}\n")

    return df

def analyze_account_reposts(df, account_name, start_date='2025-10-01', end_date='2025-10-16'):
    """
    Analyze one account for strategic vs random posting

    Returns dict with:
    - repost_groups: List of repost groups with timeline
    - strategic_score: 0-100 (higher = more strategic)
    """

    # Convert dates to pd.Timestamp
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter posts for this account
    account_posts = df[df['account'] == account_name].copy()
    account_posts = account_posts.sort_values('created_date')

    if len(account_posts) == 0:
        return None

    va = account_posts['va'].iloc[0] if pd.notna(account_posts['va'].iloc[0]) else 'Unknown'

    # Get October posts
    oct_mask = (account_posts['created_date'] >= start_date) & (account_posts['created_date'] <= end_date)
    oct_posts = account_posts[oct_mask]

    if len(oct_posts) == 0:
        return None

    # Group by sound URL (proxy for same content)
    # In real version, we'd use OCR text hash, but for now use sound
    sound_groups = defaultdict(list)

    for idx, post in account_posts.iterrows():
        sound = post.get('sound', '')
        if pd.notna(sound) and sound != '':
            sound_groups[sound].append({
                'url': post['post_url'],
                'date': post['created_date'],
                'views': post['views'],
                'is_october': start_date <= post['created_date'] <= end_date,
                'is_viral': post['views'] >= 10000
            })

    # Find repost groups (same sound used multiple times)
    repost_groups = []

    for sound, posts_list in sound_groups.items():
        if len(posts_list) <= 1:
            continue  # Not a repost, skip

        # Sort by date
        posts_list = sorted(posts_list, key=lambda x: x['date'])

        # Count October reposts
        oct_reposts = [p for p in posts_list if p['is_october']]

        if len(oct_reposts) == 0:
            continue  # No October activity

        # Find best performing (original viral post)
        best_post = max(posts_list, key=lambda x: x['views'])

        # Determine if strategic
        was_viral_before_oct = any(p['is_viral'] and not p['is_october'] for p in posts_list)

        repost_groups.append({
            'sound': sound[:80] + '...',
            'total_posts': len(posts_list),
            'oct_reposts': len(oct_reposts),
            'timeline': posts_list,
            'best_views': best_post['views'],
            'was_viral_before': was_viral_before_oct,
            'strategic': was_viral_before_oct and len(oct_reposts) > 0
        })

    # Calculate strategic score
    if len(repost_groups) == 0:
        strategic_score = 100  # No reposts = unique content (good!)
    else:
        strategic_reposts = sum(1 for g in repost_groups if g['strategic'])
        strategic_score = int((strategic_reposts / len(repost_groups)) * 100)

    return {
        'account': account_name,
        'va': va,
        'total_posts': len(account_posts),
        'oct_posts': len(oct_posts),
        'repost_groups': repost_groups,
        'strategic_score': strategic_score
    }

def generate_report(df, output_dir):
    """Generate strategic repost report for all accounts"""

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    print("🔍 Analyzing accounts...\n")

    # Get all accounts with October activity
    oct_mask = (df['created_date'] >= '2025-10-01') & (df['created_date'] <= '2025-10-16')
    oct_accounts = df[oct_mask]['account'].unique()

    print(f"Found {len(oct_accounts)} accounts with October activity\n")

    results = []

    for i, account in enumerate(oct_accounts, 1):
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(oct_accounts)} accounts...")

        analysis = analyze_account_reposts(df, account)
        if analysis:
            results.append(analysis)

    # Sort by strategic score (lowest first - these are the problematic VAs)
    results = sorted(results, key=lambda x: x['strategic_score'])

    # Generate markdown report
    md_file = output_dir / "03_STRATEGIC_REPOST_ANALYSIS.md"

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# 🎯 STRATEGIC REPOST ANALYSIS\n")
        f.write("**Period:** October 1-16, 2025\n\n")
        f.write("## Objective\n\n")
        f.write("Identify if VAs are posting **strategically** (recycling proven viral content) ")
        f.write("or **randomly** (blindly reposting without analyzing performance).\n\n")
        f.write("---\n\n")

        # Section 1: Random Posters (Strategic Score < 50)
        random_posters = [r for r in results if r['strategic_score'] < 50 and len(r['repost_groups']) > 0]

        f.write(f"## 🚨 RANDOM POSTERS (Strategic Score < 50)\n\n")
        f.write(f"*These VAs are reposting content WITHOUT analyzing what performs well*\n\n")

        if len(random_posters) > 0:
            for result in random_posters[:20]:  # Top 20 worst
                f.write(f"### {result['account']} (VA: {result['va']})\n\n")
                f.write(f"- **Strategic Score:** {result['strategic_score']}/100 ⚠️\n")
                f.write(f"- **Total Posts:** {result['total_posts']}\n")
                f.write(f"- **October Posts:** {result['oct_posts']}\n")
                f.write(f"- **Repost Groups:** {len(result['repost_groups'])}\n\n")

                for group in result['repost_groups']:
                    if group['strategic']:
                        emoji = "✅ STRATEGIC"
                    else:
                        emoji = "❌ RANDOM"

                    f.write(f"**{emoji} REPOST GROUP** ({group['total_posts']} posts, {group['oct_reposts']} in Oct)\n\n")
                    f.write(f"- Sound: `{group['sound']}`\n")
                    f.write(f"- Best Performance: {group['best_views']:,} views\n")
                    f.write(f"- Viral before October: {'YES' if group['was_viral_before'] else 'NO'}\n\n")

                    f.write("Timeline:\n")
                    for post in group['timeline']:
                        date_str = post['date'].strftime('%Y-%m-%d')
                        viral_tag = " **[VIRAL]**" if post['is_viral'] else ""
                        oct_tag = " *[OCT REPOST]*" if post['is_october'] else ""
                        f.write(f"- {date_str}: {post['views']:,} views{viral_tag}{oct_tag}\n")
                        f.write(f"  {post['url']}\n")

                    f.write("\n")

                f.write("---\n\n")
        else:
            f.write("*No random posters found - all VAs posting strategically! ✅*\n\n")

        # Section 2: Strategic Posters (Score >= 70)
        strategic_posters = [r for r in results if r['strategic_score'] >= 70 and len(r['repost_groups']) > 0]

        f.write(f"## ✅ STRATEGIC POSTERS (Score >= 70)\n\n")
        f.write(f"*These VAs are successfully recycling viral content*\n\n")

        if len(strategic_posters) > 0:
            f.write("| Account | VA | Strategic Score | Repost Groups | Oct Posts |\n")
            f.write("|---|---|---|---|---|\n")

            for result in strategic_posters[:20]:
                f.write(f"| {result['account']} | {result['va']} | {result['strategic_score']}/100 | {len(result['repost_groups'])} | {result['oct_posts']} |\n")

            f.write("\n")
        else:
            f.write("*None found*\n\n")

        # Section 3: Summary stats
        f.write("## 📊 Summary\n\n")
        f.write(f"- Total accounts analyzed: {len(results)}\n")
        f.write(f"- Random posters (score < 50): {len(random_posters)}\n")
        f.write(f"- Strategic posters (score >= 70): {len(strategic_posters)}\n")
        f.write(f"- Average strategic score: {int(sum(r['strategic_score'] for r in results) / len(results))}/100\n")
        f.write("\n")

    print(f"\n✅ Report generated: {md_file}")
    print(f"   Random posters found: {len(random_posters)}")
    print(f"   Strategic posters: {len(strategic_posters)}\n")

    return results

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          🎯 STRATEGIC REPOST ANALYZER                         ║
║          Viral Recycling vs Random Posting                    ║
╚════════════════════════════════════════════════════════════════╝
    """)

    database_path = Path(__file__).parent.parent / "MASTER_TIKTOK_DATABASE.csv"
    output_dir = Path(__file__).parent.parent / "analysis_reports"

    # Load all data
    df = load_all_data(database_path)

    # Generate report
    results = generate_report(df, output_dir)

    print("✅ Analysis complete!\n")


if __name__ == "__main__":
    main()
