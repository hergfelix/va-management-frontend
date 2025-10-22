#!/usr/bin/env python3
"""
Test OCR on a SINGLE post with slides to verify the pipeline works
"""

import pandas as pd
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from pathlib import Path

# Load October data
print("📊 Loading October data...")
df = pd.read_csv('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
                 quotechar='"', escapechar='\\')
df['created_date'] = pd.to_datetime(df['created_date'])
oct_df = df[(df['created_date'] >= '2025-10-01') & (df['created_date'] <= '2025-10-16')]

# Find first post with slides
posts_with_slides = oct_df[oct_df['slides'].notna() & (oct_df['slides'] != '')]
sample = posts_with_slides.iloc[0]

print(f"\n=== TESTING OCR ON: ===")
print(f"Account: {sample['account']}")
print(f"VA: {sample['va']}")
print(f"URL: {sample['post_url']}")
print(f"Views: {sample['views']}")

# Extract slide URLs
slides_str = str(sample['slides'])
slide_urls = [url.strip() for url in slides_str.split('|') if url.strip()]

print(f"\n📸 Found {len(slide_urls)} slide URLs")

# Download and OCR each slide
for i, url in enumerate(slide_urls[:3], 1):  # Test first 3 slides
    print(f"\n--- Slide {i} ---")
    print(f"URL: {url[:80]}...")

    try:
        # Download image with proper headers to bypass TikTok CDN protection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            print(f"✅ Downloaded: {img.size[0]}x{img.size[1]} pixels")

            # Run OCR
            text = pytesseract.image_to_string(img)
            text = text.strip()

            if text:
                print(f"📝 OCR Text ({len(text)} chars):")
                print(f"   \"{text[:200]}...\"")
            else:
                print(f"⚠️  No text detected (empty OCR result)")
        else:
            print(f"❌ Download failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ OCR Test complete!")
