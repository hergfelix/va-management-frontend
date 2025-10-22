# TikTok Slide Management System

Complete system for downloading, storing, and previewing TikTok carousel slides with Supabase integration.

## 🎯 Overview

This system enables you to:
1. **Download** carousel slide images from TikTok URLs
2. **Upload** slides to Supabase Storage for cloud hosting
3. **Generate** HTML preview pages for easy screenshot/copy workflow
4. **Browse** all carousel posts through an index page

## 📦 Components

### 1. `slide_manager.py` - Core Module

Main class for slide operations:

```python
from slide_manager import SlideManager

# Initialize (local only)
manager = SlideManager()

# Initialize with Supabase
manager = SlideManager(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key"
)

# Process post slides
result = await manager.process_post_slides(post_data, upload_to_cloud=True)

# Generate preview
preview_path = manager.generate_preview_html(result)
```

### 2. `process_slides_from_csv.py` - CSV Processor

Batch process slides from scraper output:

```bash
# Download slides only (local cache)
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv

# Download and upload to Supabase
python3 process_slides_from_csv.py data.csv --upload
```

## 🚀 Quick Start

### Installation

```bash
# Required
pip install aiohttp

# Optional (for Supabase upload)
pip install supabase

# Optional (for CSV processing)
pip install pandas
```

### Basic Usage

#### Step 1: Process Existing Scraper Output

```bash
cd "02_Scraping_Systems/01_TikTok_Scrapers"

# Process CSV with carousel posts
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv
```

This will:
- ✅ Find all carousel posts (where `slide_count` > 0)
- ✅ Download slide images to `./slide_cache/`
- ✅ Generate individual preview HTML files
- ✅ Create `index.html` with links to all previews

#### Step 2: Open Preview in Browser

```bash
# Mac
open slide_cache/index.html

# Linux
xdg-open slide_cache/index.html

# Windows
start slide_cache/index.html
```

#### Step 3: Screenshot Workflow

1. **Open preview** in browser
2. **Screenshot individual slides** using:
   - Mac: `Cmd + Shift + 4` (select area)
   - Windows: `Win + Shift + S`
3. **Download slides** using "💾 Download" button
4. **Copy URLs** using "📋 Copy URL" button

## ☁️ Supabase Integration

### Setup Supabase Storage

#### 1. Create Storage Bucket

Go to Supabase Dashboard → Storage → Create bucket:
- **Name**: `tiktok-slides`
- **Public**: Yes (for preview URLs)
- **File size limit**: 10MB
- **Allowed MIME types**: `image/jpeg`, `image/png`

#### 2. Set Environment Variables

```bash
# Add to .env file
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Or pass directly in code
manager = SlideManager(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key"
)
```

#### 3. Enable Upload

```bash
# Upload slides to Supabase during processing
python3 process_slides_from_csv.py data.csv --upload
```

### Supabase Policies

Set up Row Level Security (RLS) policies:

```sql
-- Allow public read access to slides
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'tiktok-slides');

-- Allow authenticated upload
CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'tiktok-slides'
    AND auth.role() = 'authenticated'
);
```

## 📊 Data Flow

```
Scraper CSV
    ↓
process_slides_from_csv.py
    ↓
SlideManager.process_post_slides()
    ↓
┌─────────────────────┬──────────────────────┐
│   Download Slides   │   Upload to Supabase │
│   (local cache)     │   (cloud storage)    │
└─────────────────────┴──────────────────────┘
    ↓
SlideManager.generate_preview_html()
    ↓
HTML Preview Files
    ↓
Browser → Screenshot/Download
```

## 📁 File Structure

```
02_Scraping_Systems/01_TikTok_Scrapers/
├── slide_manager.py                    # Core module
├── process_slides_from_csv.py          # CSV processor
├── slide_cache/                        # Downloaded slides
│   ├── 7330716631651519786_slide_1.jpg
│   ├── 7330716631651519786_slide_2.jpg
│   ├── 7330716631651519786_preview.html
│   └── index.html                      # Main index
└── SLIDE_MANAGEMENT_SYSTEM.md          # This file
```

## 🎨 Preview Features

### Individual Post Preview

Each preview page includes:
- **Slide display**: Full-size images in order
- **Download buttons**: Save individual slides
- **Copy URL**: Get Supabase/local URLs
- **Open full**: View in new tab
- **Keyboard shortcuts**: `Cmd/Ctrl + S` to download
- **Responsive design**: Works on mobile/tablet

### Index Page

Master index with:
- **Grid layout**: All carousel posts
- **Quick access**: Click to view any preview
- **Stats**: Total posts processed
- **Responsive**: Adapts to screen size

## 🔧 Advanced Usage

### Programmatic Access

```python
import asyncio
from slide_manager import SlideManager

async def process_single_post():
    manager = SlideManager()

    # Post data from scraper
    post = {
        'post_url': 'https://www.tiktok.com/@user/video/123',
        'slide_count': 3,
        'slide_1': 'https://p16-sign.tiktokcdn-us.com/...',
        'slide_2': 'https://p16-sign.tiktokcdn-us.com/...',
        'slide_3': 'https://p16-sign.tiktokcdn-us.com/...'
    }

    # Download and process
    result = await manager.process_post_slides(post)

    # Generate preview
    preview = manager.generate_preview_html(result)

    print(f"Preview: {preview}")
    print(f"Local files: {result['local_paths']}")
    print(f"Cloud URLs: {result['cloud_urls']}")

asyncio.run(process_single_post())
```

### Custom Storage Path

```python
# Use custom cache directory
manager = SlideManager(local_cache_dir="./my_slides")
```

### Batch Processing with Limit

```python
from pathlib import Path
import csv

def get_carousel_posts(csv_path, limit=10):
    """Get first N carousel posts"""
    posts = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get('slide_count', 0)) > 0:
                posts.append(row)
                if len(posts) >= limit:
                    break
    return posts
```

## 🎯 Use Cases

### 1. VA Screenshot Workflow

**Problem**: VAs need to screenshot TikTok carousel slides for analysis

**Solution**:
1. Run comprehensive scraper → CSV with slide URLs
2. Process CSV → Generate previews
3. Share preview URL with VA
4. VA opens in browser → Screenshots each slide
5. No TikTok app required, no manual navigation

### 2. Content Archive

**Problem**: Need permanent archive of carousel content

**Solution**:
1. Download slides to local cache
2. Upload to Supabase for cloud backup
3. Generate previews for future reference
4. Delete TikTok URLs remain accessible

### 3. Bulk Analysis

**Problem**: Analyze 100+ carousel posts efficiently

**Solution**:
1. Scrape all posts → Get slide URLs
2. Batch download all slides
3. Use index page for quick navigation
4. Export slide URLs for external tools

## ⚙️ Configuration

### Environment Variables

```bash
# Supabase (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Slide cache (optional, default: ./slide_cache)
SLIDE_CACHE_DIR=/path/to/cache
```

### SlideManager Options

```python
SlideManager(
    supabase_url=None,        # Supabase project URL
    supabase_key=None,        # Supabase anon key
    local_cache_dir="./cache" # Local storage path
)
```

### Processing Options

```python
process_post_slides(
    post_data,              # Dict with post_url, slide_count, slide_1..12
    upload_to_cloud=True    # Whether to upload to Supabase
)
```

## 🐛 Troubleshooting

### Issue: "No carousel posts found"

**Cause**: CSV doesn't have `slide_count` column or all values are 0

**Solution**:
1. Ensure you're using output from updated `comprehensive_scraper.py`
2. Check CSV has carousel posts (not all posts have slides)
3. Verify column names match expected format

### Issue: "Supabase upload failed"

**Cause**: Missing credentials or bucket doesn't exist

**Solution**:
1. Check `SUPABASE_URL` and `SUPABASE_KEY` environment variables
2. Create `tiktok-slides` bucket in Supabase dashboard
3. Verify bucket is public
4. Check RLS policies allow uploads

### Issue: "Download failed" for slides

**Cause**: TikTok CDN URL expired or rate limiting

**Solution**:
1. CDN URLs expire after ~24 hours - re-scrape if needed
2. Add delays between downloads (already built-in)
3. Check network connectivity
4. Verify URL format is correct

### Issue: "Preview shows broken images"

**Cause**: Local paths not found or cloud URLs wrong

**Solution**:
1. Ensure slides downloaded to `slide_cache/`
2. Open preview from same directory
3. If using Supabase, verify uploads succeeded
4. Check browser console for URL errors

## 📈 Performance

### Download Speed
- **Single slide**: ~1-2 seconds
- **3-slide carousel**: ~4-6 seconds
- **Rate limiting**: 1 second between posts

### Storage Requirements
- **Average slide**: 200-500KB
- **3-slide carousel**: ~1.5MB
- **100 carousel posts**: ~150MB

### Supabase Limits (Free Tier)
- **Storage**: 1GB total
- **Bandwidth**: 2GB/month
- **File uploads**: No rate limit
- **Estimated capacity**: ~2,000 carousel posts

## 🔒 Security

### Best Practices

1. **Environment Variables**: Never commit credentials
2. **Public Bucket**: Only for non-sensitive content
3. **RLS Policies**: Restrict upload to authenticated users
4. **URL Expiration**: CDN URLs expire after ~24h
5. **Local Cache**: Clear periodically to save space

### Supabase Security

```sql
-- Read-only public access
CREATE POLICY "Public Read"
ON storage.objects FOR SELECT
USING (bucket_id = 'tiktok-slides');

-- Authenticated users can upload
CREATE POLICY "Auth Upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'tiktok-slides'
    AND auth.role() = 'authenticated'
);

-- Users can only delete their own uploads (if tracking user_id)
CREATE POLICY "User Delete"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'tiktok-slides'
    AND owner = auth.uid()
);
```

## 🎓 Examples

### Example 1: Process Test Data

```bash
# Get test CSV with carousel posts
python3 comprehensive_scraper.py --limit 10

# Process slides
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_10_VIDEOS_*.csv

# Open preview
open slide_cache/index.html
```

### Example 2: Upload to Supabase

```bash
# Set credentials
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="eyJxxx..."

# Process with upload
python3 process_slides_from_csv.py data.csv --upload

# Verify in Supabase dashboard
# Storage → tiktok-slides → slides/
```

### Example 3: Custom Integration

```python
# In your scraper script
from slide_manager import SlideManager

async def scrape_with_slides():
    manager = SlideManager()

    # After scraping post...
    if post_data['slide_count'] > 0:
        slide_result = await manager.process_post_slides(post_data)
        preview = manager.generate_preview_html(slide_result)

        # Add preview URL to database
        post_data['preview_url'] = str(preview)

    return post_data
```

## 📚 API Reference

### SlideManager Class

#### Methods

**`__init__(supabase_url, supabase_key, local_cache_dir)`**
- Initialize slide manager
- **Args**: Optional Supabase credentials and cache directory
- **Returns**: SlideManager instance

**`download_slide(url, post_id, slide_number, session)`**
- Download single slide image
- **Args**: Image URL, post identifier, slide index, aiohttp session
- **Returns**: Path to downloaded file or None

**`upload_to_supabase(local_path, bucket, public)`**
- Upload slide to Supabase Storage
- **Args**: Local file path, bucket name, public flag
- **Returns**: Public URL or None

**`process_post_slides(post_data, upload_to_cloud)`**
- Process all slides for a post
- **Args**: Post dictionary, upload flag
- **Returns**: Dict with local_paths and cloud_urls

**`generate_preview_html(slide_data, output_path)`**
- Generate HTML preview page
- **Args**: Slide data from process_post_slides(), optional output path
- **Returns**: Path to HTML file

## 🚀 Future Enhancements

### Planned Features
- [ ] Thumbnail generation for faster previews
- [ ] Batch download progress bar
- [ ] Resume interrupted downloads
- [ ] OCR text extraction from slides
- [ ] Automatic metadata tagging
- [ ] Search/filter in index page
- [ ] Export to PDF
- [ ] Comparison view for A/B testing

### Integration Ideas
- [ ] Directly integrate into comprehensive_scraper.py
- [ ] Auto-generate previews during scraping
- [ ] Add to master database schema
- [ ] Create API endpoints for slide access
- [ ] Build dashboard for slide management

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review TRANSFORMATION_GUIDE.md for CSV format
3. Verify slide URLs are valid (expire after 24h)
4. Test with sample data first

## 📄 License

Part of TikTok Analytics Project - Internal use only
