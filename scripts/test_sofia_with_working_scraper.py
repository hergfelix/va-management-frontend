"""
Test Sofia's Post with Working Scraper
Using the proven real_tiktok_scraper.py that worked before
"""

import asyncio
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.real_tiktok_scraper import RealTikTokScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sofia_with_working_scraper():
    """Test Sofia's post with the working scraper"""
    
    print("🎯 TESTING SOFIA'S POST WITH WORKING SCRAPER")
    print("=" * 60)
    
    # Sofia's post details
    post_url = "https://www.tiktok.com/t/ZTMure1j4/"
    creator = "Sofia"
    set_id = 86
    va = "Almira"
    post_type = "NEW"
    
    print(f"🔍 Target: {post_url}")
    print(f"👤 Creator: {creator}")
    print(f"📦 Set: #{set_id}")
    print(f"👥 VA: {va}")
    print(f"📝 Type: {post_type}")
    print()
    
    # Create baseline data (like we did before)
    baseline_data = {
        'account': 'sofia_account',
        'creator': creator,
        'va': va,
        'current_views': 0,  # We'll get real data
        'current_likes': 0,
        'current_engagement_rate': 0.0
    }
    
    # Use the working scraper
    async with RealTikTokScraper(headless=True, debug=True) as scraper:
        print("🚀 Starting real scraping with working method...")
        
        # Create a DataFrame like we did before (the working method)
        test_df = pd.DataFrame([{
            'post_url': post_url,
            'account': 'sofia_account',
            'creator': creator,
            'va': va,
            'current_views': 0,
            'current_likes': 0,
            'current_engagement_rate': 0.0
        }])
        
        # Use the same method that worked before
        scraped_metrics = await scraper.scrape_post(post_url)
        
        # Add Sofia-specific metadata
        scraped_metrics.update({
            'creator': creator,
            'set_id': set_id,
            'va': va,
            'post_type': post_type,
            'post_url': post_url
        })
    
    print("\n📊 REAL SCRAPING RESULTS:")
    print("=" * 60)
    
    if scraped_metrics.get('views', 0) > 0:
        print("✅ SUCCESS! Real data extracted!")
        print(f"📊 Views: {scraped_metrics.get('views', 0):,}")
        print(f"❤️ Likes: {scraped_metrics.get('likes', 0):,}")
        print(f"💬 Comments: {scraped_metrics.get('comments', 0):,}")
        print(f"📤 Shares: {scraped_metrics.get('shares', 0):,}")
        print(f"🔖 Bookmarks: {scraped_metrics.get('bookmarks', 0):,}")
        print(f"📈 Engagement Rate: {scraped_metrics.get('engagement_rate', 0):.2f}%")
        print(f"👤 Creator: {scraped_metrics.get('creator', 'N/A')}")
        print(f"👥 VA: {scraped_metrics.get('va', 'N/A')}")
        print(f"📦 Set: #{scraped_metrics.get('set_id', 'N/A')}")
        print(f"📝 Type: {scraped_metrics.get('post_type', 'N/A')}")
        
        # Save results
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"sofia_working_scraper_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(scraped_metrics, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Create CSV for easy analysis
        csv_data = [scraped_metrics]
        df = pd.DataFrame(csv_data)
        csv_file = f"sofia_working_scraper_results_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        print(f"📊 CSV saved to: {csv_file}")
        
    else:
        print("❌ No data extracted")
        if 'error' in scraped_metrics:
            print(f"Error: {scraped_metrics['error']}")
        else:
            print("Views: 0 - TikTok may be blocking or post not accessible")
    
    return scraped_metrics

if __name__ == "__main__":
    asyncio.run(test_sofia_with_working_scraper())
