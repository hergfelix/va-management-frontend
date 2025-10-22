"""
Create Complete CSV with Your 3 Links + Full Data
SuperClaude Complete CSV Creator

This creates a CSV with your 3 links + complete data from working videos
"""

import pandas as pd
import json
from datetime import datetime

def create_complete_csv_your_3_links():
    """
    Create complete CSV with your 3 links + full data from working videos
    """
    print("📊 CREATING COMPLETE CSV WITH YOUR 3 LINKS + FULL DATA")
    print("=" * 70)
    
    # Your 3 links data (from mobile scraping - only views)
    your_3_links_data = [
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZTMmT78be/",
            "creator": "Mara",
            "set_id": 19,
            "va": "Leah",
            "type": "New",
            
            # Post Metrics (MOBILE SCRAPED DATA - ONLY VIEWS)
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
            "data_quality": "Partial (Views Only)"
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZTMmTvGqd/",
            "creator": "Sofia",
            "set_id": 89,
            "va": "Pilar",
            "type": "REPOST",
            
            # Post Metrics (MOBILE SCRAPED DATA - ONLY VIEWS)
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
            "data_quality": "Partial (Views Only)"
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/t/ZP8AWUGAJ/",
            "creator": "Tyra",
            "set_id": 4,
            "va": "Kyle",
            "type": "REPOST",
            
            # Post Metrics (MOBILE SCRAPED DATA - ONLY VIEWS)
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
            "data_quality": "Partial (Views Only)"
        }
    ]
    
    # Complete data from working videos (for reference and comparison)
    complete_working_data = [
        {
            # Post Information
            "post_url": "https://www.tiktok.com/@maracloudd/video/7550243000379559181",
            "creator": "Mara",
            "set_id": 21,
            "va": "Leah",
            "type": "REPOST",
            
            # Post Metrics (COMPLETE DATA)
            "views": 988,
            "likes": 40,
            "comments": 22,
            "shares": 0,
            "bookmarks": 0,
            "engagement": 62,
            "engagement_rate": 6.28,
            
            # Account Information (COMPLETE DATA)
            "account_username": "maracloudd",
            "account_followers": 8612,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information (COMPLETE DATA)
            "post_description": "For the boys... | elevones Vertigo 0 pecho D Tell me the saddest thing that's ever happened to you. I'm not talking \"I couldn't go out with my friends.\" I'm talking the most gut wrenching, heart breaking thing ever. Keepers",
            "hashtags": "fyp, relatable, pickuptruck, mentalhealth",
            "mentions": "",
            "content_length": 200,
            
            # Sound Information (COMPLETE DATA)
            "sound_title": "",
            "sound_url": "https://www.tiktok.com/music/som-original-7489218187797220102",
            "sound_author": "",
            "has_sound": True,
            
            # Slides Information (COMPLETE DATA)
            "slide_count": 2,
            "slide_1": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550243000379559181/slide_1.jpg",
            "slide_2": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550243000379559181/slide_2.jpg",
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
            "scraped_at": "2025-10-22T00:59:37.601856",
            "scraping_method": "real_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Complete"
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/@naomifallinn/video/7550462758928649527",
            "creator": "Naomi",
            "set_id": 27,
            "va": "Beverly",
            "type": "REPOST",
            
            # Post Metrics (COMPLETE DATA)
            "views": 1973,
            "likes": 119,
            "comments": 6,
            "shares": 3,
            "bookmarks": 0,
            "engagement": 128,
            "engagement_rate": 6.49,
            
            # Account Information (COMPLETE DATA)
            "account_username": "naomifallinn",
            "account_followers": 5984,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information (COMPLETE DATA)
            "post_description": "if you ever see him spaced out, shaking his leg, biting his nails, blasting music or going silent... | just grab his attention, don't ask what's wrong, he's just remembering stuff he doesn't want to. just hold his hand and be there for him.",
            "hashtags": "",
            "mentions": "",
            "content_length": 200,
            
            # Sound Information (COMPLETE DATA)
            "sound_title": "",
            "sound_url": "https://www.tiktok.com/music/original-sound-6918489585085418245",
            "sound_author": "",
            "has_sound": True,
            
            # Slides Information (COMPLETE DATA)
            "slide_count": 2,
            "slide_1": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550462758928649527/slide_1.jpg",
            "slide_2": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550462758928649527/slide_2.jpg",
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
            "scraped_at": "2025-10-22T00:59:45.663365",
            "scraping_method": "real_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Complete"
        },
        {
            # Post Information
            "post_url": "https://www.tiktok.com/@naomibubbless/video/7550462964399213879",
            "creator": "Naomi",
            "set_id": 37,
            "va": "Beverly",
            "type": "REPOST",
            
            # Post Metrics (COMPLETE DATA)
            "views": 307,
            "likes": 37,
            "comments": 5,
            "shares": 0,
            "bookmarks": 0,
            "engagement": 42,
            "engagement_rate": 13.68,
            
            # Account Information (COMPLETE DATA)
            "account_username": "naomibubbless",
            "account_followers": 3895,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            
            # Content Information (COMPLETE DATA)
            "post_description": "Behind all the anger, | Behind all the trust issues, | was just a boy who wanted to feel like he was something to someone at least once.",
            "hashtags": "fyp, fypシ゚viral",
            "mentions": "",
            "content_length": 150,
            
            # Sound Information (COMPLETE DATA)
            "sound_title": "",
            "sound_url": "https://www.tiktok.com/music/O-N-E-M-O-R-E-L-I-G-H-T-7171127074671332102",
            "sound_author": "",
            "has_sound": True,
            
            # Slides Information (COMPLETE DATA)
            "slide_count": 3,
            "slide_1": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550462964399213879/slide_1.jpg",
            "slide_2": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550462964399213879/slide_2.jpg",
            "slide_3": "https://pub-7f3727f6b8d9442a91c5e4c8c050b4c9.r2.dev/7550462964399213879/slide_3.jpg",
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
            "scraped_at": "2025-10-22T00:59:53.573756",
            "scraping_method": "real_tiktok_scraper",
            "scraping_success": True,
            "data_quality": "Complete"
        }
    ]
    
    # Combine your 3 links + complete working data
    all_data = your_3_links_data + complete_working_data
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"COMPLETE_YOUR_3_LINKS_PLUS_FULL_DATA_{timestamp}.csv"
    
    df.to_csv(output_file, index=False)
    
    print("✅ COMPLETE CSV CREATED!")
    print(f"📁 File: {output_file}")
    print(f"📊 Records: {len(df)}")
    print(f"📋 Columns: {len(df.columns)}")
    
    print("\n📊 DATA BREAKDOWN:")
    print("=" * 50)
    
    # Your 3 links summary
    your_3_links = df[df['data_quality'] == 'Partial (Views Only)']
    print(f"🎯 YOUR 3 LINKS (Partial Data):")
    print(f"   • Records: {len(your_3_links)}")
    print(f"   • Total Views: {your_3_links['views'].sum():,}")
    print(f"   • Data Quality: Views only (TikTok blocks other metrics)")
    
    # Complete working data summary
    complete_data = df[df['data_quality'] == 'Complete']
    print(f"\n✅ COMPLETE WORKING DATA (Full Data):")
    print(f"   • Records: {len(complete_data)}")
    print(f"   • Total Views: {complete_data['views'].sum():,}")
    print(f"   • Total Likes: {complete_data['likes'].sum():,}")
    print(f"   • Total Comments: {complete_data['comments'].sum():,}")
    print(f"   • Total Shares: {complete_data['shares'].sum():,}")
    print(f"   • Total Engagement: {complete_data['engagement'].sum():,}")
    print(f"   • Avg Engagement Rate: {complete_data['engagement_rate'].mean():.2f}%")
    print(f"   • Total Followers: {complete_data['account_followers'].sum():,}")
    print(f"   • Total Slides: {complete_data['slide_count'].sum()}")
    
    print("\n👥 YOUR 3 LINKS BREAKDOWN:")
    for i, row in your_3_links.iterrows():
        print(f"   {i+1}. {row['creator']} (Set #{row['set_id']}) | {row['va']} | {row['views']:>4,} views | {row['type']} | {row['data_quality']}")
    
    print("\n✅ COMPLETE DATA BREAKDOWN:")
    for i, row in complete_data.iterrows():
        print(f"   {i+1}. {row['creator']} (Set #{row['set_id']}) | {row['va']} | {row['views']:>4,} views | {row['likes']:>3,} likes | {row['comments']:>2,} comments | {row['engagement_rate']:>5.2f}% engagement")
    
    print(f"\n💾 Complete CSV saved to: {output_file}")
    print("🎯 This contains:")
    print("   ✅ YOUR 3 SPECIFIC LINKS (with real views)")
    print("   ✅ COMPLETE WORKING DATA (with all metrics)")
    print("   ✅ 43 columns with all details")
    print("   ✅ Real slides, hashtags, descriptions")
    print("   ✅ Account followers, engagement rates")
    
    print("\n💡 WHAT YOU HAVE NOW:")
    print("   🎯 YOUR 3 LINKS: 313, 1,693, 125 views (real data)")
    print("   ✅ COMPLETE DATA: 988, 1,973, 307 views + likes + comments + followers")
    print("   📊 TOTAL: 6 posts with mixed data quality")
    print("   🔍 COMPARISON: You can see the difference between partial and complete data")
    
    return output_file, df

if __name__ == "__main__":
    create_complete_csv_your_3_links()
