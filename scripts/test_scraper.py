#!/usr/bin/env python3
"""
Test script for the Optimal TikTok Metrics Scraper
Tests with 10 → 100 → 1000 posts as specified in SWARM requirements
"""

import asyncio
import time
import json
from pathlib import Path
from optimal_metrics_scraper import OptimalTikTokScraper

async def test_scraper_scale():
    """
    Test the scraper at different scales: 10 → 100 → 1000 posts
    """
    # Test URLs (in real implementation, these would come from database)
    test_urls = [
        "https://www.tiktok.com/@user1/video/123",
        "https://www.tiktok.com/@user2/video/456",
        "https://www.tiktok.com/@user3/video/789",
        "https://www.tiktok.com/@user4/video/101",
        "https://www.tiktok.com/@user5/video/112",
        "https://www.tiktok.com/@user6/video/131",
        "https://www.tiktok.com/@user7/video/415",
        "https://www.tiktok.com/@user8/video/161",
        "https://www.tiktok.com/@user9/video/718",
        "https://www.tiktok.com/@user10/video/192",
    ]
    
    # Extend to 100 URLs
    urls_100 = test_urls * 10
    
    # Extend to 1000 URLs
    urls_1000 = test_urls * 100
    
    scraper = OptimalTikTokScraper()
    
    print("🧪 Testing Optimal TikTok Scraper at Scale")
    print("=" * 60)
    
    # Test 1: 10 posts
    print("\n📊 Test 1: 10 Posts")
    print("-" * 30)
    
    start_time = time.time()
    results_10 = await scraper.scrape_batch(test_urls)
    end_time = time.time()
    
    success_rate_10 = len([r for r in results_10 if r.success]) / len(test_urls) * 100
    total_time_10 = end_time - start_time
    posts_per_minute_10 = len(test_urls) / (total_time_10 / 60)
    total_cost_10 = sum(r.cost for r in results_10)
    
    print(f"✅ Posts tested: {len(test_urls)}")
    print(f"✅ Success rate: {success_rate_10:.1f}%")
    print(f"✅ Total time: {total_time_10:.2f} seconds")
    print(f"✅ Speed: {posts_per_minute_10:.1f} posts/minute")
    print(f"✅ Total cost: ${total_cost_10:.4f}")
    print(f"✅ Cost per 1000: ${(total_cost_10 / len(test_urls)) * 1000:.2f}")
    
    # Test 2: 100 posts
    print("\n📊 Test 2: 100 Posts")
    print("-" * 30)
    
    start_time = time.time()
    results_100 = await scraper.scrape_batch(urls_100)
    end_time = time.time()
    
    success_rate_100 = len([r for r in results_100 if r.success]) / len(urls_100) * 100
    total_time_100 = end_time - start_time
    posts_per_minute_100 = len(urls_100) / (total_time_100 / 60)
    total_cost_100 = sum(r.cost for r in results_100)
    
    print(f"✅ Posts tested: {len(urls_100)}")
    print(f"✅ Success rate: {success_rate_100:.1f}%")
    print(f"✅ Total time: {total_time_100:.2f} seconds")
    print(f"✅ Speed: {posts_per_minute_100:.1f} posts/minute")
    print(f"✅ Total cost: ${total_cost_100:.4f}")
    print(f"✅ Cost per 1000: ${(total_cost_100 / len(urls_100)) * 1000:.2f}")
    
    # Test 3: 1000 posts (if budget allows)
    print("\n📊 Test 3: 1000 Posts")
    print("-" * 30)
    
    # Check if we have budget for 1000 posts
    estimated_cost_1000 = (total_cost_100 / len(urls_100)) * 1000
    if estimated_cost_1000 > scraper.config["max_budget_per_day"]:
        print(f"⚠️ Skipping 1000 posts test - estimated cost ${estimated_cost_1000:.2f} exceeds daily budget ${scraper.config['max_budget_per_day']}")
        print("💡 Increase max_budget_per_day in config to test 1000 posts")
    else:
        start_time = time.time()
        results_1000 = await scraper.scrape_batch(urls_1000)
        end_time = time.time()
        
        success_rate_1000 = len([r for r in results_1000 if r.success]) / len(urls_1000) * 100
        total_time_1000 = end_time - start_time
        posts_per_minute_1000 = len(urls_1000) / (total_time_1000 / 60)
        total_cost_1000 = sum(r.cost for r in results_1000)
        
        print(f"✅ Posts tested: {len(urls_1000)}")
        print(f"✅ Success rate: {success_rate_1000:.1f}%")
        print(f"✅ Total time: {total_time_1000:.2f} seconds")
        print(f"✅ Speed: {posts_per_minute_1000:.1f} posts/minute")
        print(f"✅ Total cost: ${total_cost_1000:.4f}")
        print(f"✅ Cost per 1000: ${(total_cost_1000 / len(urls_1000)) * 1000:.2f}")
    
    # Performance Report
    print("\n📈 Performance Report")
    print("-" * 30)
    
    report = scraper.get_performance_report()
    print(f"Overall success rate: {report['overall_success_rate']:.1%}")
    print(f"Total cost today: ${report['total_cost']:.4f}")
    print(f"Total posts processed: {report['total_posts']}")
    
    print("\nMethod performance:")
    for method, stats in report["methods"].items():
        print(f"  {method}: {stats['success_rate']:.1%} success, ${stats['avg_cost']:.4f} avg cost")
    
    # Method usage analysis
    print("\n🔍 Method Usage Analysis")
    print("-" * 30)
    
    all_results = results_10 + results_100
    method_usage = {}
    for result in all_results:
        method = result.method.value
        method_usage[method] = method_usage.get(method, 0) + 1
    
    for method, count in method_usage.items():
        percentage = (count / len(all_results)) * 100
        print(f"  {method}: {count} posts ({percentage:.1f}%)")
    
    # Cost analysis
    print("\n💰 Cost Analysis")
    print("-" * 30)
    
    cost_per_1000 = (total_cost_100 / len(urls_100)) * 1000
    daily_cost_1000_posts = cost_per_1000
    monthly_cost_1000_posts = daily_cost_1000_posts * 30
    annual_cost_1000_posts = daily_cost_1000_posts * 365
    
    print(f"Cost per 1000 posts: ${cost_per_1000:.2f}")
    print(f"Daily cost (1000 posts): ${daily_cost_1000_posts:.2f}")
    print(f"Monthly cost (1000 posts): ${monthly_cost_1000_posts:.2f}")
    print(f"Annual cost (1000 posts): ${annual_cost_1000_posts:.2f}")
    
    # ROI analysis
    print("\n📊 ROI Analysis")
    print("-" * 30)
    
    manual_time_per_post = 2  # minutes
    manual_cost_per_hour = 25  # dollars
    manual_cost_per_post = (manual_time_per_post / 60) * manual_cost_per_hour
    
    automated_cost_per_post = total_cost_100 / len(urls_100)
    savings_per_post = manual_cost_per_post - automated_cost_per_post
    roi_percentage = (savings_per_post / automated_cost_per_post) * 100
    
    print(f"Manual cost per post: ${manual_cost_per_post:.4f}")
    print(f"Automated cost per post: ${automated_cost_per_post:.4f}")
    print(f"Savings per post: ${savings_per_post:.4f}")
    print(f"ROI: {roi_percentage:.1f}%")
    
    # Break-even analysis
    break_even_posts = scraper.config["max_budget_per_day"] / automated_cost_per_post
    print(f"Break-even posts per day: {break_even_posts:.0f}")
    
    print("\n🎯 Test Results Summary")
    print("=" * 60)
    print(f"✅ 10 posts: {success_rate_10:.1f}% success, ${(total_cost_10 / len(test_urls)) * 1000:.2f}/1k")
    print(f"✅ 100 posts: {success_rate_100:.1f}% success, ${(total_cost_100 / len(urls_100)) * 1000:.2f}/1k")
    if 'results_1000' in locals():
        print(f"✅ 1000 posts: {success_rate_1000:.1f}% success, ${(total_cost_1000 / len(urls_1000)) * 1000:.2f}/1k")
    
    print(f"\n🏆 Overall Performance:")
    print(f"   Success Rate: {report['overall_success_rate']:.1%}")
    print(f"   Cost Efficiency: ${cost_per_1000:.2f} per 1000 posts")
    print(f"   ROI: {roi_percentage:.1f}%")
    print(f"   Break-even: {break_even_posts:.0f} posts/day")
    
    return {
        "test_10": {
            "posts": len(test_urls),
            "success_rate": success_rate_10,
            "cost_per_1000": (total_cost_10 / len(test_urls)) * 1000
        },
        "test_100": {
            "posts": len(urls_100),
            "success_rate": success_rate_100,
            "cost_per_1000": (total_cost_100 / len(urls_100)) * 1000
        },
        "overall": {
            "success_rate": report['overall_success_rate'],
            "total_cost": report['total_cost'],
            "roi": roi_percentage
        }
    }

if __name__ == "__main__":
    asyncio.run(test_scraper_scale())
