# Scraper Output → Master Database Transformation Guide

## Overview
This guide documents the transformation from comprehensive scraper output to the master database schema format.

## Quick Start

```bash
# Transform a scraper output file
python3 transform_to_master_schema.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv

# Specify custom output filename
python3 transform_to_master_schema.py input.csv output.csv
```

## Field Mappings

### ✅ Direct Mappings (Available from Scraper)

| Master Field | Scraper Field | Notes |
|--------------|---------------|-------|
| `post_url` | `post_url` | Direct copy |
| `creator` | `creator` | Direct copy |
| `set_id` | `set_id` | Direct copy |
| `va` | `va` | Direct copy |
| `post_type` | `type` | NEW/REPOST |
| `account` | `account_username` | TikTok username |
| `views` | `views` | Post view count |
| `likes` | `likes` | Post like count |
| `comments` | `comments` | Comment count |
| `shares` | `shares` | Share count |
| `engagement` | `engagement` | Total engagement |
| `engagement_rate` | `engagement_rate` | Percentage |
| `followers` | `account_followers` | Account followers |
| `hashtags` | `hashtags` | Post hashtags |
| `sound` | `sound_title` | Sound/music title |

### 🔄 Derived Fields (Calculated)

| Master Field | Derivation Logic | Example |
|--------------|------------------|---------|
| `va_url` | Extracted from `post_url` if short format | `https://www.tiktok.com/t/ZTMmAeEUy/` |
| `set_code` | `{CREATOR[:4]}_{SET_ID:03d}` | `TYRA_066` |
| `platform` | Always `"tiktok"` | `tiktok` |
| `logged_at` | `scraped_at` timestamp | `2025-10-22T19:36:13.699232` |
| `first_scraped_at` | `scraped_at` timestamp | `2025-10-22T19:36:13.699232` |
| `last_scraped_at` | `scraped_at` timestamp | `2025-10-22T19:36:13.699232` |
| `scrape_status` | Always `"active"` for new scrapes | `active` |
| `scrape_interval` | Always `"daily"` for initial scrape | `daily` |
| `scrape_count` | Always `"1"` for first scrape | `1` |
| `days_since_posted` | Always `"0"` for initial scrape | `0` |

### ⚠️ Fields Requiring Manual Population

These fields are NOT available from the current scraper and need additional data sources:

| Master Field | Required Data | Source |
|--------------|---------------|--------|
| `created_date` | Post creation timestamp | TikTok API or manual entry |
| `sound_url` | TikTok sound URL | TikTok API |
| `slide_count` | Number of carousel images | Image carousel detection |
| `day1_views` - `day5_views` | Multi-day view tracking | Scheduled re-scraping |
| `ocr_text` | Text extracted from images | OCR processing |
| `slide_1` - `slide_12` | Image URLs for carousel posts | Image download/hosting |

### 📊 Fields Not Used (Scraper-Specific)

These fields exist in scraper output but are not mapped to master schema:

- `bookmarks` - Not tracked in master schema
- `account_following` - Not tracked in master schema
- `account_posts` - Not tracked in master schema
- `account_likes` - Not tracked in master schema
- `account_verified` - Not tracked in master schema
- `mentions` - Combined into hashtags in master schema
- `content_length` - Not tracked in master schema
- `sound_author` - Not tracked in master schema
- `has_sound` - Implicit if sound field populated
- `scraping_method` - Internal metadata
- `data_quality` - Internal metadata
- `error` - Internal metadata

## Schema Structure

### Master Database (46 columns)

```
Core Identification (1-10):
  va_url, post_url, created_date, creator, set_id, set_code,
  va, post_type, platform, account

Timestamps (11-12, 20):
  logged_at, first_scraped_at, last_scraped_at

Engagement Metrics (13-19):
  views, likes, comments, shares, engagement, engagement_rate, followers

Content Metadata (21-24):
  hashtags, sound, sound_url, slide_count

Multi-Day Performance (25-29):
  day1_views, day2_views, day3_views, day4_views, day5_views

Scraping Management (30-33):
  scrape_status, scrape_interval, scrape_count, days_since_posted

OCR & Slides (34-46):
  ocr_text, slide_1 through slide_12
```

## Transformation Statistics

**Test Results (50 URLs):**
- Total rows processed: 50
- Successfully transformed: 49 (98%)
- Failed/skipped: 1 (2%)
- Column count: 46 ✅
- Schema match: 100% ✅

## Usage Examples

### Transform Single File
```bash
python3 transform_to_master_schema.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv
# Output: COMPREHENSIVE_SCRAPED_50_VIDEOS_MASTER_FORMAT.csv
```

### Batch Transform Multiple Files
```bash
for file in COMPREHENSIVE_SCRAPED_*.csv; do
    python3 transform_to_master_schema.py "$file"
done
```

### Custom Output Location
```bash
python3 transform_to_master_schema.py \
    input/scraper_output.csv \
    output/master_format.csv
```

## Integration Workflow

### 1. Scrape Data
```bash
python3 comprehensive_scraper.py
# Output: COMPREHENSIVE_SCRAPED_*.csv
```

### 2. Transform to Master Format
```bash
python3 transform_to_master_schema.py COMPREHENSIVE_SCRAPED_*.csv
# Output: *_MASTER_FORMAT.csv
```

### 3. Manual Enrichment (Optional)
- Add `va_url` short URLs
- Add `created_date` timestamps
- Add `sound_url` references
- Process images for OCR and slide URLs

### 4. Merge into Master Database
```bash
# Append to master_with_snaptik.csv
cat *_MASTER_FORMAT.csv | tail -n +2 >> master_with_snaptik.csv
```

## Data Quality Notes

### ✅ High Quality Fields (98%+ accuracy)
- Account metrics (followers, username)
- Engagement metrics (views, likes, comments)
- Post metadata (creator, VA, set_id)
- Timestamps (scraped_at)

### ⚠️ Fields Requiring Validation
- `va_url` - May be empty if not short URL format
- `set_code` - Generated automatically, verify format
- `hashtags` - Verify proper comma separation

### 🔴 Fields Requiring External Data
- `created_date` - Not available from DOM scraping
- `sound_url` - Requires TikTok API
- Multi-day views - Requires scheduled re-scraping
- Image data - Requires additional processing

## Troubleshooting

### Issue: Column Count Mismatch
```
Solution: Verify input file has correct scraper format
Check: head -1 input.csv | tr ',' '\n' | wc -l
Expected: 30 columns from scraper
```

### Issue: Missing Required Fields
```
Solution: Ensure scraper output includes all required columns
Required: post_url, creator, set_id, va, account_username, etc.
```

### Issue: Failed Rows
```
Solution: Check scraping_success column in input
Only rows with scraping_success='True' are transformed
```

## Next Steps

### Short-term Enhancement
1. Add VA URL extraction from TikTok API
2. Implement multi-day view tracking scheduler
3. Add OCR processing pipeline for image text

### Long-term Integration
1. Build automated enrichment pipeline
2. Integrate with database update system
3. Add data validation and quality checks
4. Implement conflict resolution for re-scrapes
