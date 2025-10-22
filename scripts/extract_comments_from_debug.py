"""
Extract Comments from Debug HTML
SuperClaude Comments Analysis Specialist

Extract and analyze real comments from TikTok debug HTML
"""

import re
import json
import html
from datetime import datetime

def extract_comments_from_debug_html(html_file_path):
    """
    Extract real comments from TikTok debug HTML
    """
    print("🔍 EXTRACTING REAL COMMENTS FROM DEBUG HTML")
    print("=" * 60)
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 HTML file loaded: {len(content):,} characters")
        
        # Extract JSON data
        json_data = extract_json_data(content)
        if not json_data:
            print("❌ No JSON data found")
            return None
        
        print(f"✅ JSON data extracted: {len(json_data):,} characters")
        
        # Parse comments from JSON
        comments = parse_comments_from_json(json_data)
        
        # Analyze comments
        analyze_comments(comments)
        
        return comments
        
    except Exception as e:
        print(f"❌ Error extracting comments: {e}")
        return None

def extract_json_data(content):
    """Extract JSON data from HTML"""
    try:
        # Look for the main JSON data
        json_patterns = [
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.__DATA__\s*=\s*({.*?});'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                return matches[0]
        
        return None
        
    except Exception as e:
        print(f"❌ Error extracting JSON: {e}")
        return None

def parse_comments_from_json(json_data):
    """Parse comments from JSON data"""
    comments = []
    
    try:
        # Look for comment patterns in JSON
        comment_patterns = [
            r'"commentCount":(\d+)',
            r'"comment_count":(\d+)',
            r'"comments":\[(.*?)\]',
            r'"commentList":\[(.*?)\]',
            r'"replies":\[(.*?)\]'
        ]
        
        print("🔍 Searching for comment data...")
        
        # Find comment count
        comment_count = 0
        for pattern in comment_patterns:
            matches = re.findall(pattern, json_data)
            if matches:
                if pattern.startswith('"commentCount"') or pattern.startswith('"comment_count"'):
                    comment_count = int(matches[0])
                    print(f"✅ Found comment count: {comment_count}")
                elif 'comments' in pattern or 'replies' in pattern:
                    print(f"✅ Found comment array data")
                    # Try to extract individual comments
                    comments.extend(extract_individual_comments(matches[0]))
        
        # Look for individual comment text
        text_patterns = [
            r'"text":"([^"]+)"',
            r'"content":"([^"]+)"',
            r'"comment":"([^"]+)"',
            r'"message":"([^"]+)"'
        ]
        
        for pattern in text_patterns:
            matches = re.findall(pattern, json_data)
            for i, text in enumerate(matches):
                if len(text) > 5 and not text.startswith('http'):
                    # Decode HTML entities
                    decoded_text = html.unescape(text)
                    comments.append({
                        "comment_id": f"comment_{i}",
                        "text": decoded_text,
                        "author": f"user_{i}",
                        "timestamp": datetime.now().isoformat(),
                        "likes": 0,
                        "source": "json_extraction"
                    })
        
        # Remove duplicates
        unique_comments = []
        seen_texts = set()
        for comment in comments:
            if comment["text"] not in seen_texts:
                unique_comments.append(comment)
                seen_texts.add(comment["text"])
        
        print(f"✅ Extracted {len(unique_comments)} unique comments")
        return unique_comments
        
    except Exception as e:
        print(f"❌ Error parsing comments: {e}")
        return []

def extract_individual_comments(comment_array_data):
    """Extract individual comments from array data"""
    comments = []
    
    try:
        # Look for individual comment objects
        comment_object_pattern = r'\{[^}]*"text":"([^"]+)"[^}]*\}'
        matches = re.findall(comment_object_pattern, comment_array_data)
        
        for i, text in enumerate(matches):
            if len(text) > 5:
                comments.append({
                    "comment_id": f"array_comment_{i}",
                    "text": html.unescape(text),
                    "author": f"user_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "likes": 0,
                    "source": "array_extraction"
                })
        
        return comments
        
    except Exception as e:
        print(f"❌ Error extracting individual comments: {e}")
        return []

def analyze_comments(comments):
    """Analyze the extracted comments"""
    print("\n📊 COMMENTS ANALYSIS:")
    print("=" * 60)
    
    if not comments:
        print("❌ No comments found")
        return
    
    print(f"💬 Total Comments: {len(comments)}")
    
    # Analyze comment lengths
    lengths = [len(comment["text"]) for comment in comments]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    print(f"📏 Average Length: {avg_length:.1f} characters")
    print(f"📏 Shortest: {min(lengths)} characters")
    print(f"📏 Longest: {max(lengths)} characters")
    
    # Look for creator comments (simplified heuristic)
    creator_comments = []
    creator_keywords = ['creator', 'author', 'op', 'poster', 'sofia', 'tiktok']
    
    for comment in comments:
        text_lower = comment["text"].lower()
        if any(keyword in text_lower for keyword in creator_keywords):
            creator_comments.append(comment)
    
    print(f"👤 Potential Creator Comments: {len(creator_comments)}")
    
    # Show sample comments
    print(f"\n💬 SAMPLE COMMENTS:")
    for i, comment in enumerate(comments[:10], 1):
        text = comment["text"][:100] + "..." if len(comment["text"]) > 100 else comment["text"]
        print(f"   {i:2d}. {text}")
    
    # Show creator comments if found
    if creator_comments:
        print(f"\n👤 CREATOR COMMENTS:")
        for i, comment in enumerate(creator_comments[:5], 1):
            text = comment["text"][:100] + "..." if len(comment["text"]) > 100 else comment["text"]
            print(f"   {i:2d}. {text}")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"extracted_comments_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comments saved to: {output_file}")

def main():
    """Main execution"""
    html_file = "real_comments_debug_1761085371.html"
    
    print("💬 REAL COMMENTS EXTRACTION")
    print("=" * 60)
    print(f"📄 Debug HTML: {html_file}")
    print(f"🎯 Target: https://www.tiktok.com/t/ZP8SxfT4H/")
    print(f"💬 Expected: 500+ comments")
    print()
    
    comments = extract_comments_from_debug_html(html_file)
    
    if comments:
        print(f"\n🎉 SUCCESS! Extracted {len(comments)} real comments!")
    else:
        print(f"\n❌ Failed to extract comments")

if __name__ == "__main__":
    main()
