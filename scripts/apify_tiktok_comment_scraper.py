"""
Apify TikTok Comment Scraper
SuperClaude Apify Comments Extraction Specialist

This scraper will use Apify's TikTok Comment Scraper to extract real comments
"""

import asyncio
import json
import time
from datetime import datetime
from apify_client import ApifyClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApifyTikTokCommentScraper:
    """
    Apify TikTok Comment Scraper
    """
    
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.client = None
        
    def __enter__(self):
        """Setup Apify client"""
        if self.api_token:
            self.client = ApifyClient(self.api_token)
        else:
            # Use default token (you'll need to set this)
            self.client = ApifyClient()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        pass

    def scrape_comments_apify(self, post_url: str) -> dict:
        """
        Scrape comments using Apify's TikTok Comment Scraper
        """
        try:
            logger.info(f"💬 Apify TikTok comment scraping: {post_url}")
            
            # Actor ID for TikTok Comment Scraper
            actor_id = "BDec00yAmCm1QbMEI"
            
            # Prepare input for the actor
            run_input = {
                "startUrls": [post_url],
                "maxComments": 1000,  # Maximum comments to scrape
                "maxReplies": 100,    # Maximum replies per comment
                "includeReplies": True,
                "includeCommentText": True,
                "includeCommentAuthor": True,
                "includeCommentLikes": True,
                "includeCommentTimestamp": True
            }
            
            logger.info(f"🎯 Running Apify actor: {actor_id}")
            logger.info(f"📊 Input: {json.dumps(run_input, indent=2)}")
            
            # Run the actor
            run = self.client.actor(actor_id).call(run_input=run_input)
            
            # Get the results
            results = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            logger.info(f"✅ Apify scraping completed!")
            logger.info(f"📊 Results: {len(results)} items")
            
            # Process results
            comments_data = self._process_apify_results(results, post_url)
            
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Apify comment scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    def _process_apify_results(self, results, post_url):
        """Process Apify results into our format"""
        try:
            comments = []
            
            for item in results:
                # Extract comment data
                comment_data = {
                    "text": item.get("text", ""),
                    "author": item.get("author", {}).get("username", "Unknown"),
                    "likes": item.get("likesCount", 0),
                    "timestamp": item.get("createdAt", datetime.now().isoformat()),
                    "source": "apify_scraper",
                    "comment_id": item.get("id", ""),
                    "replies": []
                }
                
                # Extract replies if available
                if item.get("replies"):
                    for reply in item["replies"]:
                        reply_data = {
                            "text": reply.get("text", ""),
                            "author": reply.get("author", {}).get("username", "Unknown"),
                            "likes": reply.get("likesCount", 0),
                            "timestamp": reply.get("createdAt", datetime.now().isoformat()),
                            "source": "apify_scraper_reply"
                        }
                        comment_data["replies"].append(reply_data)
                
                comments.append(comment_data)
            
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "success": True,
                "comments": comments,
                "comment_count": len(comments),
                "method": "apify_tiktok_comment_scraper",
                "total_items": len(results)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing Apify results: {e}")
            return {
                "post_url": post_url,
                "success": False,
                "error": f"Processing error: {str(e)}",
                "comments": []
            }

    def scrape_comments_with_fallback(self, post_url: str) -> dict:
        """
        Scrape comments with fallback methods
        """
        try:
            # Try Apify first
            logger.info("🔄 Trying Apify TikTok Comment Scraper...")
            apify_result = self.scrape_comments_apify(post_url)
            
            if apify_result.get("success", False) and apify_result.get("comments"):
                logger.info("✅ Apify succeeded!")
                return apify_result
            else:
                logger.warning("⚠️ Apify failed, trying fallback...")
                return self._fallback_scraping(post_url)
                
        except Exception as e:
            logger.error(f"❌ All methods failed: {e}")
            return {
                "post_url": post_url,
                "success": False,
                "error": str(e),
                "comments": []
            }

    def _fallback_scraping(self, post_url: str) -> dict:
        """Fallback scraping method"""
        try:
            # This would be your custom scraping method
            logger.info("🔄 Using fallback scraping method...")
            
            # For now, return empty result
            return {
                "post_url": post_url,
                "success": False,
                "error": "Fallback method not implemented",
                "comments": []
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback scraping failed: {e}")
            return {
                "post_url": post_url,
                "success": False,
                "error": str(e),
                "comments": []
            }

def main():
    """Main execution"""
    print("💬 APIFY TIKTOK COMMENT SCRAPER")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: Apify TikTok Comment Scraper")
    print(f"🎭 Actor: BDec00yAmCm1QbMEI")
    print()
    
    # Note: You'll need to set your Apify API token
    print("⚠️  IMPORTANT: You need to set your Apify API token!")
    print("   1. Go to https://console.apify.com/account/integrations")
    print("   2. Copy your API token")
    print("   3. Set it as environment variable: export APIFY_TOKEN=your_token")
    print()
    
    # Check if API token is available
    import os
    api_token = os.getenv('APIFY_TOKEN')
    
    if not api_token:
        print("❌ No Apify API token found!")
        print("   Please set APIFY_TOKEN environment variable")
        return
    
    # Scrape comments with Apify
    with ApifyTikTokCommentScraper(api_token=api_token) as scraper:
        comments_data = scraper.scrape_comments_apify(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"apify_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 APIFY COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with Apify!")
        print(f"💬 Method: {comments_data.get('method', 'N/A')}")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        print(f"📊 Total Items: {comments_data.get('total_items', 0)}")
        
        comments = comments_data.get('comments', [])
        if comments:
            print(f"\n💬 SAMPLE COMMENTS WITH AUTHORS:")
            for i, comment in enumerate(comments[:10], 1):
                text = comment.get('text', 'N/A')[:60] + "..." if len(comment.get('text', '')) > 60 else comment.get('text', 'N/A')
                author = comment.get('author', 'N/A')
                likes = comment.get('likes', 0)
                replies_count = len(comment.get('replies', []))
                print(f"   {i:2d}. @{author}: {text} ({likes} likes, {replies_count} replies)")
            
            # Analyze authors
            authors = [comment.get('author', 'Unknown') for comment in comments]
            unique_authors = list(set(authors))
            print(f"\n👥 UNIQUE AUTHORS: {len(unique_authors)}")
            for author in unique_authors[:10]:
                count = authors.count(author)
                print(f"   • @{author}: {count} comments")
            
            # Analyze replies
            total_replies = sum(len(comment.get('replies', [])) for comment in comments)
            print(f"\n💬 TOTAL REPLIES: {total_replies}")
            
            # Show sample replies
            print(f"\n💬 SAMPLE REPLIES:")
            reply_count = 0
            for comment in comments:
                for reply in comment.get('replies', []):
                    if reply_count < 5:
                        text = reply.get('text', 'N/A')[:50] + "..." if len(reply.get('text', '')) > 50 else reply.get('text', 'N/A')
                        author = reply.get('author', 'N/A')
                        print(f"   • @{author}: {text}")
                        reply_count += 1
        else:
            print("⚠️ No comments found")
    else:
        print("❌ Apify comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    main()
