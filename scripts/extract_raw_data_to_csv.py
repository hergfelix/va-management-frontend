"""
Extract Raw Data to CSV - No Formatting, No Processing
SuperClaude Data Extraction Agent

Extracts ALL raw data from comprehensive extraction results
and saves to CSV without any formatting or processing.
"""

import json
import pandas as pd
from datetime import datetime

def extract_raw_data_to_csv():
    """Extract all raw data to CSV without any formatting"""
    
    print("📊 EXTRACTING RAW DATA TO CSV")
    print("=" * 50)
    
    # Load the comprehensive extraction results
    try:
        with open('comprehensive_extraction_results.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ comprehensive_extraction_results.json not found")
        return
    
    print("✅ Loaded comprehensive extraction results")
    
    # Extract all raw data from each agent
    raw_data_rows = []
    
    # Test post info
    test_post = data.get('test_post', {})
    url = test_post.get('url', '')
    creator = test_post.get('creator', '')
    set_id = test_post.get('set_id', '')
    va = test_post.get('va', '')
    post_type = test_post.get('post_type', '')
    
    # Process each agent's results
    results = data.get('results', {})
    
    for agent_key, agent_data in results.items():
        print(f"📋 Processing {agent_data.get('agent', agent_key)}...")
        
        # Create base row with test post info
        base_row = {
            'extraction_timestamp': data.get('timestamp', ''),
            'test_url': url,
            'creator': creator,
            'set_id': set_id,
            'va': va,
            'post_type': post_type,
            'agent_name': agent_data.get('agent', ''),
            'agent_method': agent_data.get('method', ''),
            'extraction_success': agent_data.get('success', False),
            'data_quality': agent_data.get('data_quality', ''),
            'extraction_time': agent_data.get('extraction_time', ''),
            'error_message': agent_data.get('error', '')
        }
        
        # Add post metrics if available
        post_metrics = agent_data.get('post_metrics', {})
        if post_metrics:
            base_row.update({
                'post_views': post_metrics.get('views', ''),
                'post_likes': post_metrics.get('likes', ''),
                'post_comments': post_metrics.get('comments', ''),
                'post_shares': post_metrics.get('shares', ''),
                'post_bookmarks': post_metrics.get('bookmarks', ''),
                'post_engagement_rate': post_metrics.get('engagement_rate', ''),
                'post_engagement': post_metrics.get('engagement', ''),
                'post_scraped_at': post_metrics.get('scraped_at', ''),
                'post_viral_score': post_metrics.get('viral_score', ''),
                'post_performance_trend': post_metrics.get('performance_trend', '')
            })
        
        # Add account info if available
        account_info = agent_data.get('account_info', {})
        if account_info:
            base_row.update({
                'account_username': account_info.get('username', ''),
                'account_followers': account_info.get('followers', ''),
                'account_following': account_info.get('following', ''),
                'account_posts_count': account_info.get('posts_count', ''),
                'account_bio': account_info.get('bio', ''),
                'account_verified': account_info.get('verified', ''),
                'account_created': account_info.get('account_created', ''),
                'account_last_active': account_info.get('last_active', ''),
                'account_engagement_rate': account_info.get('engagement_rate', ''),
                'account_avg_views': account_info.get('avg_views', ''),
                'account_avg_likes': account_info.get('avg_likes', '')
            })
        
        # Add content analysis if available
        content_analysis = agent_data.get('content_analysis', {})
        if content_analysis:
            base_row.update({
                'content_hashtags': str(content_analysis.get('hashtags', '')),
                'content_sound_title': content_analysis.get('sound_title', ''),
                'content_slides_count': content_analysis.get('slides_count', ''),
                'content_duration': content_analysis.get('duration', ''),
                'content_slide_urls': str(content_analysis.get('slide_urls', '')),
                'content_ocr_text': content_analysis.get('ocr_text', ''),
                'content_category': content_analysis.get('content_category', ''),
                'content_viral_potential': content_analysis.get('viral_potential', '')
            })
        
        # Add performance analysis if available
        performance_analysis = agent_data.get('performance_analysis', {})
        if performance_analysis:
            base_row.update({
                'performance_trending_score': performance_analysis.get('trending_score', ''),
                'performance_engagement_quality': performance_analysis.get('engagement_quality', ''),
                'performance_audience_reach': performance_analysis.get('audience_reach', ''),
                'performance_content_effectiveness': performance_analysis.get('content_effectiveness', '')
            })
        
        # Add any additional fields that might exist
        for key, value in agent_data.items():
            if key not in ['agent', 'method', 'success', 'data_quality', 'extraction_time', 'error', 
                          'post_metrics', 'account_info', 'content_analysis', 'performance_analysis']:
                base_row[f'additional_{key}'] = str(value)
        
        raw_data_rows.append(base_row)
    
    # Create DataFrame
    df = pd.DataFrame(raw_data_rows)
    
    # Save to CSV without any formatting
    csv_filename = f'raw_tiktok_extraction_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    
    print(f"✅ Raw data saved to: {csv_filename}")
    print(f"📊 Total rows: {len(df)}")
    print(f"📋 Total columns: {len(df.columns)}")
    
    # Show column names
    print("\n📋 COLUMNS IN RAW DATA:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    # Show sample of data
    print(f"\n📊 SAMPLE DATA (first row):")
    if not df.empty:
        first_row = df.iloc[0]
        for col in df.columns:
            value = first_row[col]
            if pd.notna(value) and value != '':
                print(f"   {col}: {value}")
    
    return csv_filename

if __name__ == "__main__":
    extract_raw_data_to_csv()
