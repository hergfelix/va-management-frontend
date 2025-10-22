#!/usr/bin/env python3
"""
Real TikTok Scraping Test
Test with actual TikTok URLs from master_with_snaptik.csv
"""

import asyncio
import time
import csv
import json
from datetime import datetime
from optimal_metrics_scraper import OptimalTikTokScraper

async def test_real_tiktok_posts():
    """
    Test the scraper with real TikTok URLs
    """
    # Load real test posts
    real_posts = []
    with open('real_test_posts.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            real_posts.append(row)
    
    print("🎯 REAL TIKTOK SCRAPING TEST")
    print("=" * 60)
    print(f"Testing {len(real_posts)} real TikTok posts...")
    print()
    
    # Initialize scraper
    scraper = OptimalTikTokScraper()
    
    # Extract URLs for scraping
    test_urls = [post['post_url'] for post in real_posts]
    
    print("📊 BASELINE DATA (from your CSV):")
    print("-" * 40)
    for i, post in enumerate(real_posts, 1):
        print(f"{i}. {post['account']} ({post['creator']})")
        print(f"   Views: {int(post['current_views']):,} | Likes: {int(post['current_likes']):,} | Engagement: {post['current_engagement_rate']}%")
    print()
    
    # Run the scraper
    print("🚀 STARTING REAL SCRAPING...")
    print("-" * 40)
    
    start_time = time.time()
    results = await scraper.scrape_batch(test_urls)
    end_time = time.time()
    
    # Calculate metrics
    successful_scrapes = [r for r in results if r.success]
    success_rate = len(successful_scrapes) / len(test_urls) * 100
    total_time = end_time - start_time
    posts_per_minute = len(test_urls) / (total_time / 60)
    total_cost = sum(r.cost for r in results)
    
    print(f"\n📈 SCRAPING RESULTS:")
    print("-" * 40)
    print(f"✅ Success rate: {success_rate:.1f}%")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"🚀 Speed: {posts_per_minute:.1f} posts/minute")
    print(f"💰 Total cost: ${total_cost:.4f}")
    print(f"💵 Cost per 1000: ${(total_cost / len(test_urls)) * 1000:.2f}")
    
    # Compare with baseline data
    print(f"\n📊 COMPARISON: SCRAPED vs BASELINE")
    print("-" * 60)
    print(f"{'Account':<15} {'Method':<10} {'Scraped Views':<15} {'Baseline Views':<15} {'Difference':<12}")
    print("-" * 60)
    
    comparison_data = []
    for i, (post, result) in enumerate(zip(real_posts, results)):
        if result.success:
            scraped_views = result.metrics.get('views', 0)
            baseline_views = int(post['current_views'])
            difference = scraped_views - baseline_views
            diff_percent = (difference / baseline_views * 100) if baseline_views > 0 else 0
            
            print(f"{post['account']:<15} {result.method.value:<10} {scraped_views:<15,} {baseline_views:<15,} {difference:+,} ({diff_percent:+.1f}%)")
            
            comparison_data.append({
                'account': post['account'],
                'creator': post['creator'],
                'va': post['va'],
                'post_url': post['post_url'],
                'scraping_method': result.method.value,
                'scraped_views': scraped_views,
                'scraped_likes': result.metrics.get('likes', 0),
                'scraped_comments': result.metrics.get('comments', 0),
                'scraped_shares': result.metrics.get('shares', 0),
                'scraped_engagement_rate': result.metrics.get('engagement_rate', 0),
                'baseline_views': baseline_views,
                'baseline_likes': int(post['current_likes']),
                'baseline_comments': int(post['current_comments']),
                'baseline_shares': int(post['current_shares']),
                'baseline_engagement_rate': float(post['current_engagement_rate']),
                'views_difference': difference,
                'views_difference_percent': diff_percent,
                'scraped_at': datetime.now().isoformat(),
                'success': True
            })
        else:
            print(f"{post['account']:<15} {'FAILED':<10} {'ERROR':<15} {post['current_views']:<15,} {'N/A':<12}")
            comparison_data.append({
                'account': post['account'],
                'creator': post['creator'],
                'va': post['va'],
                'post_url': post['post_url'],
                'scraping_method': result.method.value if result.method else 'none',
                'error': result.error,
                'baseline_views': int(post['current_views']),
                'baseline_likes': int(post['current_likes']),
                'baseline_comments': int(post['current_comments']),
                'baseline_shares': int(post['current_shares']),
                'baseline_engagement_rate': float(post['current_engagement_rate']),
                'scraped_at': datetime.now().isoformat(),
                'success': False
            })
    
    # Save detailed results to CSV
    csv_filename = 'real_tiktok_scraping_results.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        if comparison_data:
            fieldnames = comparison_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(comparison_data)
    
    print(f"\n💾 RESULTS SAVED TO: {csv_filename}")
    
    # Show method usage
    method_usage = {}
    for result in results:
        if result.success:
            method = result.method.value
            method_usage[method] = method_usage.get(method, 0) + 1
    
    print(f"\n🔧 METHOD USAGE:")
    for method, count in method_usage.items():
        percentage = (count / len(results)) * 100
        print(f"  {method}: {count} posts ({percentage:.1f}%)")
    
    # Performance report
    report = scraper.get_performance_report()
    print(f"\n📊 PERFORMANCE REPORT:")
    print(f"  Overall success rate: {report['overall_success_rate']:.1%}")
    print(f"  Total cost: ${report['total_cost']:.4f}")
    
    return comparison_data

if __name__ == "__main__":
    asyncio.run(test_real_tiktok_posts())
