"""
Create Final CSV with Your 3 Links Data
SuperClaude Final CSV Creator for Your 3 Links

This creates a clean CSV with the mobile-scraped data from your 3 links
"""

import pandas as pd
import json
from datetime import datetime

def create_final_csv_your_3_links():
    """
    Create final CSV with your 3 links data
    """
    print("📊 CREATING FINAL CSV WITH YOUR 3 LINKS DATA")
    print("=" * 60)
    
    # Your 3 links data (from mobile scraping)
    your_3_links_data = [
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZTMmT78be/",
            "creator": "Mara",
            "set_id": 19,
            "va": "Leah",
            "type": "New",
            
            # Post Metrics (MOBILE SCRAPED DATA)
            "views": 313,
            "likes": 0,  # Could not extract with mobile
            "comments": 0,  # Could not extract with mobile
            "shares": 0,  # Could not extract with mobile
            "bookmarks": 0,  # Could not extract with mobile
            "engagement": 0,
            "engagement_rate": 0.0,
            
            # Account Information (Could not extract with mobile)
            "account_username": "Unknown",
            "account_followers": 0,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information
            "post_description": "",
            "hashtags": "",
            "mentions": "",
            "content_length": 0,
            
            # Sound Information
            "sound_title": "",
            "sound_url": "",
            "sound_author": "",
            "has_sound": False,
            
            # Slides Information
            "slide_count": 0,
            "slide_1": "",
            "slide_2": "",
            "slide_3": "",
            "slide_4": "",
            "slide_5": "",
            "slide_6": "",
            "slide_7": "",
            "slide_8": "",
            "slide_9": "",
            "slide_10": "",
            "slide_11": "",
            "slide_12": "",
            
            # Scraping Information
            "scraped_at": "2025-10-22T04:13:49.293587",
            "scraping_method": "mobile_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Partial"  # Only views extracted
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZTMmTvGqd/",
            "creator": "Sofia",
            "set_id": 89,
            "va": "Pilar",
            "type": "REPOST",
            
            # Post Metrics (MOBILE SCRAPED DATA)
            "views": 1693,
            "likes": 0,  # Could not extract with mobile
            "comments": 0,  # Could not extract with mobile
            "shares": 0,  # Could not extract with mobile
            "bookmarks": 0,  # Could not extract with mobile
            "engagement": 0,
            "engagement_rate": 0.0,
            
            # Account Information (Could not extract with mobile)
            "account_username": "Unknown",
            "account_followers": 0,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information
            "post_description": "",
            "hashtags": "",
            "mentions": "",
            "content_length": 0,
            
            # Sound Information
            "sound_title": "",
            "sound_url": "",
            "sound_author": "",
            "has_sound": False,
            
            # Slides Information
            "slide_count": 0,
            "slide_1": "",
            "slide_2": "",
            "slide_3": "",
            "slide_4": "",
            "slide_5": "",
            "slide_6": "",
            "slide_7": "",
            "slide_8": "",
            "slide_9": "",
            "slide_10": "",
            "slide_11": "",
            "slide_12": "",
            
            # Scraping Information
            "scraped_at": "2025-10-22T04:13:56.713426",
            "scraping_method": "mobile_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Partial"  # Only views extracted
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZP8AWUGAJ/",
            "creator": "Tyra",
            "set_id": 4,
            "va": "Kyle",
            "type": "REPOST",
            
            # Post Metrics (MOBILE SCRAPED DATA)
            "views": 125,
            "likes": 0,  # Could not extract with mobile
            "comments": 0,  # Could not extract with mobile
            "shares": 0,  # Could not extract with mobile
            "bookmarks": 0,  # Could not extract with mobile
            "engagement": 0,
            "engagement_rate": 0.0,
            
            # Account Information (Could not extract with mobile)
            "account_username": "Unknown",
            "account_followers": 0,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information
            "post_description": "",
            "hashtags": "",
            "mentions": "",
            "content_length": 0,
            
            # Sound Information
            "sound_title": "",
            "sound_url": "",
            "sound_author": "",
            "has_sound": False,
            
            # Slides Information
            "slide_count": 0,
            "slide_1": "",
            "slide_2": "",
            "slide_3": "",
            "slide_4": "",
            "slide_5": "",
            "slide_6": "",
            "slide_7": "",
            "slide_8": "",
            "slide_9": "",
            "slide_10": "",
            "slide_11": "",
            "slide_12": "",
            
            # Scraping Information
            "scraped_at": "2025-10-22T04:14:09.552762",
            "scraping_method": "mobile_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Partial"  # Only views extracted
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(your_3_links_data)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"FINAL_YOUR_3_LINKS_DATA_{timestamp}.csv"
    
    df.to_csv(output_file, index=False)
    
    print("✅ FINAL CSV CREATED!")
    print(f"📁 File: {output_file}")
    print(f"📊 Records: {len(df)}")
    print(f"📋 Columns: {len(df.columns)}")
    
    print("\n📋 COLUMNS INCLUDED:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print("\n📊 YOUR 3 LINKS DATA SUMMARY:")
    print("=" * 60)
    
    total_views = df['views'].sum()
    total_likes = df['likes'].sum()
    total_comments = df['comments'].sum()
    total_shares = df['shares'].sum()
    total_bookmarks = df['bookmarks'].sum()
    total_engagement = df['engagement'].sum()
    avg_engagement_rate = df['engagement_rate'].mean()
    
    print(f"📈 Total Views: {total_views:,}")
    print(f"❤️  Total Likes: {total_likes:,}")
    print(f"💬 Total Comments: {total_comments:,}")
    print(f"📤 Total Shares: {total_shares:,}")
    print(f"🔖 Total Bookmarks: {total_bookmarks:,}")
    print(f"📊 Total Engagement: {total_engagement:,}")
    print(f"📈 Average Engagement Rate: {avg_engagement_rate:.2f}%")
    
    print("\n👥 YOUR 3 LINKS BREAKDOWN:")
    for i, row in df.iterrows():
        print(f"   {i+1}. {row['creator']} (Set #{row['set_id']}) | {row['va']} | {row['views']:>4,} views | {row['type']}")
    
    print("\n🎯 VA PERFORMANCE:")
    va_performance = df.groupby('va').agg({
        'views': 'sum',
        'likes': 'sum',
        'comments': 'sum',
        'engagement_rate': 'mean',
        'creator': 'count'
    }).round(2)
    va_performance.columns = ['Total Views', 'Total Likes', 'Total Comments', 'Avg Engagement Rate', 'Posts']
    
    for va, data in va_performance.iterrows():
        print(f"   {va:<10}: {data['Posts']} posts, {data['Total Views']:>6,} views, {data['Avg Engagement Rate']:>6.2f}% avg engagement")
    
    print(f"\n💾 Final CSV saved to: {output_file}")
    print("🎯 This contains YOUR 3 SPECIFIC LINKS with:")
    print("   ✅ Real views (313, 1,693, 125)")
    print("   ✅ Correct creator, set, VA information")
    print("   ✅ Mobile scraping method")
    print("   ⚠️  Limited data (views only - TikTok blocks other metrics)")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Use this CSV for your analysis")
    print("   2. Combine with other data sources if needed")
    print("   3. Set up automated mobile scraping for future posts")
    print("   4. Consider using the working scraper for other URLs")
    
    return output_file, df

if __name__ == "__main__":
    create_final_csv_your_3_links()
