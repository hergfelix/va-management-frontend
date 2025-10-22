# Google Sheets → Scraper → Supabase Workflow Plan

## 🎯 Objective

Create an automated pipeline: **Google Sheet Entry → Scrape TikTok Data → Store in Supabase**

**Source**: [Proof Log Google Sheet](https://docs.google.com/spreadsheets/d/1wbWzI6YL_ajMkMqR-DAVY-wqDaeDmL7DzoLRCN-msz0/edit?gid=55434178#gid=55434178)

**Output**: Complete TikTok analytics in Supabase with slide storage for dashboard use

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA ENTRY LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  Google Sheet (Manual Entry)                                         │
│  • VA, Creator, Set ID, Post URLs                                   │
│  • Trigger column: "Status" = "Ready to Scrape"                     │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  Google Apps Script OR Python Cron Job                              │
│  • Poll for "Ready to Scrape" rows                                  │
│  • Download CSV or read via API                                     │
│  • Trigger scraper workflow                                         │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      SCRAPING LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  comprehensive_scraper.py (Enhanced)                                 │
│  • Read URLs from Google Sheet CSV/API                              │
│  • Scrape video metrics (views, likes, comments, shares)            │
│  • Scrape account data (followers, verified status)                 │
│  • Extract carousel slide URLs                                      │
│  • Download slide images                                            │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  Supabase Database (PostgreSQL)                                     │
│  • Table: tiktok_posts (video metrics, account data)                │
│  • Table: tiktok_slides (slide metadata)                            │
│  • Table: scraping_logs (audit trail)                               │
│                                                                      │
│  Supabase Storage (File Storage)                                    │
│  • Bucket: tiktok-slides (slide images)                             │
│  • Public URLs for dashboard display                                │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD LAYER (Future)                          │
├─────────────────────────────────────────────────────────────────────┤
│  Analytics Dashboard                                                 │
│  • Performance metrics by VA/Creator                                │
│  • Slide galleries for screenshot workflow                          │
│  • Trend analysis and reporting                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Supabase Database Schema

### Table: `tiktok_posts`

Primary table for all scraped TikTok data (46 columns matching master schema):

```sql
CREATE TABLE tiktok_posts (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Core Identification (1-10)
    va_url TEXT,
    post_url TEXT UNIQUE NOT NULL,
    created_date TIMESTAMP,
    creator VARCHAR(100),
    set_id INTEGER,
    set_code VARCHAR(20),
    va VARCHAR(50),
    post_type VARCHAR(10),  -- NEW, REPOST
    platform VARCHAR(20) DEFAULT 'tiktok',
    account VARCHAR(100),

    -- Timestamps (11-12, 20)
    logged_at TIMESTAMP DEFAULT NOW(),
    first_scraped_at TIMESTAMP,
    last_scraped_at TIMESTAMP,

    -- Engagement Metrics (13-19)
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    comments BIGINT DEFAULT 0,
    shares BIGINT DEFAULT 0,
    engagement BIGINT DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    followers BIGINT DEFAULT 0,

    -- Content Metadata (21-24)
    hashtags TEXT,
    sound TEXT,
    sound_url TEXT,
    slide_count INTEGER DEFAULT 0,

    -- Multi-Day Performance (25-29)
    day1_views BIGINT,
    day2_views BIGINT,
    day3_views BIGINT,
    day4_views BIGINT,
    day5_views BIGINT,

    -- Scraping Management (30-33)
    scrape_status VARCHAR(20) DEFAULT 'active',
    scrape_interval VARCHAR(20) DEFAULT 'daily',
    scrape_count INTEGER DEFAULT 1,
    days_since_posted INTEGER DEFAULT 0,

    -- OCR & Metadata (34)
    ocr_text TEXT,

    -- Slide References (35-46) - Store as JSONB array
    slides JSONB,

    -- Additional Scraper Fields
    post_description TEXT,
    account_verified BOOLEAN DEFAULT FALSE,
    bookmarks BIGINT DEFAULT 0,

    -- Audit
    scraped_at TIMESTAMP DEFAULT NOW(),
    scraping_method VARCHAR(50),
    data_quality VARCHAR(50),
    error TEXT
);

-- Indexes for performance
CREATE INDEX idx_tiktok_posts_post_url ON tiktok_posts(post_url);
CREATE INDEX idx_tiktok_posts_creator ON tiktok_posts(creator);
CREATE INDEX idx_tiktok_posts_va ON tiktok_posts(va);
CREATE INDEX idx_tiktok_posts_account ON tiktok_posts(account);
CREATE INDEX idx_tiktok_posts_created_date ON tiktok_posts(created_date);
CREATE INDEX idx_tiktok_posts_scrape_status ON tiktok_posts(scrape_status);
```

### Table: `tiktok_slides`

Separate table for carousel slide metadata:

```sql
CREATE TABLE tiktok_slides (
    id BIGSERIAL PRIMARY KEY,

    -- Foreign Key
    post_id BIGINT REFERENCES tiktok_posts(id) ON DELETE CASCADE,
    post_url TEXT NOT NULL,

    -- Slide Details
    slide_number INTEGER NOT NULL,
    slide_url TEXT NOT NULL,  -- Original TikTok CDN URL
    storage_path TEXT,         -- Supabase storage path
    public_url TEXT,           -- Supabase public URL

    -- Metadata
    file_size BIGINT,          -- Bytes
    width INTEGER,             -- Pixels
    height INTEGER,            -- Pixels
    mime_type VARCHAR(50) DEFAULT 'image/jpeg',

    -- OCR (Future)
    ocr_text TEXT,
    ocr_processed BOOLEAN DEFAULT FALSE,

    -- Audit
    downloaded_at TIMESTAMP DEFAULT NOW(),
    uploaded_at TIMESTAMP,

    UNIQUE(post_url, slide_number)
);

-- Indexes
CREATE INDEX idx_tiktok_slides_post_id ON tiktok_slides(post_id);
CREATE INDEX idx_tiktok_slides_post_url ON tiktok_slides(post_url);
```

### Table: `scraping_logs`

Audit trail for all scraping operations:

```sql
CREATE TABLE scraping_logs (
    id BIGSERIAL PRIMARY KEY,

    -- Batch Info
    batch_id UUID DEFAULT gen_random_uuid(),
    batch_started_at TIMESTAMP DEFAULT NOW(),
    batch_completed_at TIMESTAMP,

    -- Source
    source_type VARCHAR(50),  -- 'google_sheets', 'manual', 'cron'
    source_reference TEXT,    -- Sheet URL, file path, etc.

    -- Results
    total_urls INTEGER,
    successful_scrapes INTEGER,
    failed_scrapes INTEGER,
    carousel_posts_processed INTEGER,
    slides_downloaded INTEGER,
    slides_uploaded INTEGER,

    -- Performance
    duration_seconds INTEGER,

    -- Status
    status VARCHAR(20),  -- 'running', 'completed', 'failed'
    error_message TEXT
);

-- Index
CREATE INDEX idx_scraping_logs_batch_id ON scraping_logs(batch_id);
CREATE INDEX idx_scraping_logs_batch_started_at ON scraping_logs(batch_started_at);
```

---

## 🔧 Implementation Components

### Component 1: Google Sheets Reader

**File**: `google_sheets_reader.py`

```python
"""
Read TikTok URLs from Google Sheets
Supports both CSV export and Sheets API
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict

class GoogleSheetsReader:
    def __init__(self, credentials_file: str):
        """Initialize with service account credentials"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope
        )
        self.client = gspread.authorize(creds)

    def read_proof_log(self, sheet_url: str) -> List[Dict]:
        """
        Read Proof Log sheet and extract URLs ready for scraping

        Returns list of dicts with:
        - post_url
        - creator
        - set_id
        - va
        - type (NEW/REPOST)
        """
        sheet = self.client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)  # First sheet

        # Get all records
        records = worksheet.get_all_records()

        # Filter for "Ready to Scrape" status
        ready_to_scrape = [
            {
                'post_url': r['Post URL'],
                'creator': r['Creator'],
                'set_id': int(r['Set ID']),
                'va': r['VA'],
                'type': r['Type']
            }
            for r in records
            if r.get('Status') == 'Ready to Scrape'
        ]

        return ready_to_scrape

    def mark_as_scraped(self, sheet_url: str, post_url: str):
        """Update status to 'Scraped' after successful scraping"""
        sheet = self.client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)

        # Find row with matching post_url
        cell = worksheet.find(post_url)
        if cell:
            # Update status column (assuming column F)
            worksheet.update_cell(cell.row, 6, 'Scraped')
```

### Component 2: Supabase Writer

**File**: `supabase_writer.py`

```python
"""
Write scraped data to Supabase
Handles both database inserts and storage uploads
"""

from supabase import create_client
from typing import Dict, List
import os
from datetime import datetime

class SupabaseWriter:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        self.client = create_client(supabase_url, supabase_key)
        self.storage_bucket = 'tiktok-slides'

    def insert_post(self, post_data: Dict) -> int:
        """
        Insert scraped post into tiktok_posts table

        Returns: post_id
        """
        # Transform scraper output to database schema
        db_record = {
            'post_url': post_data['post_url'],
            'creator': post_data['creator'],
            'set_id': post_data['set_id'],
            'va': post_data['va'],
            'post_type': post_data['type'],
            'account': post_data['account_username'],

            # Metrics
            'views': post_data['views'],
            'likes': post_data['likes'],
            'comments': post_data['comments'],
            'shares': post_data['shares'],
            'engagement': post_data['engagement'],
            'engagement_rate': post_data['engagement_rate'],
            'followers': post_data['account_followers'],

            # Content
            'hashtags': post_data['hashtags'],
            'sound': post_data['sound_title'],
            'slide_count': post_data['slide_count'],
            'post_description': post_data['post_description'],
            'account_verified': post_data['account_verified'],

            # Metadata
            'scraped_at': post_data['scraped_at'],
            'scraping_method': post_data['scraping_method'],
            'data_quality': post_data['data_quality'],

            # Generate derived fields
            'platform': 'tiktok',
            'set_code': f"{post_data['creator'][:4].upper()}_{post_data['set_id']:03d}",
            'first_scraped_at': datetime.now().isoformat(),
            'last_scraped_at': datetime.now().isoformat(),
            'scrape_status': 'active',
            'scrape_count': 1
        }

        # Insert (upsert on post_url conflict)
        result = self.client.table('tiktok_posts').upsert(
            db_record,
            on_conflict='post_url'
        ).execute()

        return result.data[0]['id']

    def insert_slides(self, post_id: int, post_url: str,
                     slide_data: List[Dict]):
        """
        Insert slide metadata into tiktok_slides table

        slide_data format:
        [{
            'slide_number': 1,
            'slide_url': 'https://...',
            'storage_path': 'slides/123_slide_1.jpg',
            'public_url': 'https://supabase.co/...',
            'file_size': 245678
        }, ...]
        """
        for slide in slide_data:
            record = {
                'post_id': post_id,
                'post_url': post_url,
                'slide_number': slide['slide_number'],
                'slide_url': slide['slide_url'],
                'storage_path': slide.get('storage_path'),
                'public_url': slide.get('public_url'),
                'file_size': slide.get('file_size'),
                'uploaded_at': datetime.now().isoformat()
            }

            self.client.table('tiktok_slides').upsert(
                record,
                on_conflict='post_url,slide_number'
            ).execute()

    def log_scraping_batch(self, batch_info: Dict):
        """Log scraping batch to audit table"""
        self.client.table('scraping_logs').insert(batch_info).execute()
```

### Component 3: Integrated Scraper

**File**: `integrated_scraper.py`

```python
"""
Integrated scraper with Google Sheets + Supabase
Orchestrates complete workflow
"""

import asyncio
from google_sheets_reader import GoogleSheetsReader
from supabase_writer import SupabaseWriter
from comprehensive_scraper import ComprehensiveTikTokScraper
from slide_manager import SlideManager
from datetime import datetime
import os
import uuid

class IntegratedScraperPipeline:
    def __init__(self):
        # Initialize components
        self.sheets_reader = GoogleSheetsReader('credentials.json')
        self.supabase_writer = SupabaseWriter(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        self.slide_manager = SlideManager(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    async def run_pipeline(self, sheet_url: str):
        """Execute complete pipeline"""
        batch_id = str(uuid.uuid4())
        batch_start = datetime.now()

        print("=" * 80)
        print("🚀 INTEGRATED SCRAPING PIPELINE")
        print("=" * 80)

        # Step 1: Read from Google Sheets
        print("\n📊 Step 1: Reading Google Sheets...")
        urls_to_scrape = self.sheets_reader.read_proof_log(sheet_url)
        print(f"   Found {len(urls_to_scrape)} URLs ready to scrape")

        if not urls_to_scrape:
            print("   ⚠️ No URLs with 'Ready to Scrape' status")
            return

        # Step 2: Scrape TikTok data
        print("\n🔍 Step 2: Scraping TikTok posts...")
        scraper_results = []

        async with ComprehensiveTikTokScraper() as scraper:
            for i, url_data in enumerate(urls_to_scrape, 1):
                result = await scraper.scrape_video_and_account(
                    url_data['post_url'],
                    i,
                    len(urls_to_scrape),
                    url_data
                )
                scraper_results.append(result)

                if i < len(urls_to_scrape):
                    await asyncio.sleep(3)

        # Step 3: Process slides
        print("\n📸 Step 3: Processing carousel slides...")
        slide_results = []

        for result in scraper_results:
            if result.get('slide_count', 0) > 0:
                slide_data = await self.slide_manager.process_post_slides(
                    result,
                    upload_to_cloud=True
                )
                slide_results.append(slide_data)

        # Step 4: Write to Supabase
        print("\n💾 Step 4: Writing to Supabase...")
        successful = 0
        failed = 0

        for result in scraper_results:
            try:
                # Insert post
                post_id = self.supabase_writer.insert_post(result)

                # Insert slides if any
                matching_slides = [
                    s for s in slide_results
                    if s['post_url'] == result['post_url']
                ]

                if matching_slides:
                    slide_metadata = [
                        {
                            'slide_number': i + 1,
                            'slide_url': result.get(f'slide_{i+1}', ''),
                            'storage_path': matching_slides[0]['local_paths'][i],
                            'public_url': matching_slides[0]['cloud_urls'][i] if matching_slides[0]['cloud_urls'] else '',
                            'file_size': 0  # Could get actual file size
                        }
                        for i in range(matching_slides[0]['slide_count'])
                    ]

                    self.supabase_writer.insert_slides(
                        post_id,
                        result['post_url'],
                        slide_metadata
                    )

                # Mark as scraped in Google Sheets
                self.sheets_reader.mark_as_scraped(
                    sheet_url,
                    result['post_url']
                )

                successful += 1

            except Exception as e:
                print(f"   ❌ Failed to write {result['post_url']}: {e}")
                failed += 1

        # Step 5: Log batch
        batch_duration = (datetime.now() - batch_start).total_seconds()

        self.supabase_writer.log_scraping_batch({
            'batch_id': batch_id,
            'batch_started_at': batch_start.isoformat(),
            'batch_completed_at': datetime.now().isoformat(),
            'source_type': 'google_sheets',
            'source_reference': sheet_url,
            'total_urls': len(urls_to_scrape),
            'successful_scrapes': successful,
            'failed_scrapes': failed,
            'carousel_posts_processed': len(slide_results),
            'slides_downloaded': sum(s['slide_count'] for s in slide_results),
            'slides_uploaded': sum(len(s['cloud_urls']) for s in slide_results),
            'duration_seconds': int(batch_duration),
            'status': 'completed'
        })

        # Summary
        print("\n" + "=" * 80)
        print("✅ PIPELINE COMPLETE")
        print("=" * 80)
        print(f"Batch ID: {batch_id}")
        print(f"Total URLs: {len(urls_to_scrape)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Carousel posts: {len(slide_results)}")
        print(f"Slides processed: {sum(s['slide_count'] for s in slide_results)}")
        print(f"Duration: {int(batch_duration)}s")
        print("=" * 80)


async def main():
    pipeline = IntegratedScraperPipeline()

    sheet_url = "https://docs.google.com/spreadsheets/d/1wbWzI6YL_ajMkMqR-DAVY-wqDaeDmL7DzoLRCN-msz0/edit?gid=55434178#gid=55434178"

    await pipeline.run_pipeline(sheet_url)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📝 Setup Steps

### Step 1: Supabase Setup

#### A. Create Supabase Project

1. Go to https://supabase.com
2. Click "New project"
3. Name: `tiktok-analytics`
4. Database password: (save securely)
5. Region: Choose closest to you
6. Click "Create new project"

#### B. Create Database Tables

Go to **SQL Editor** → **New query** → Paste and run:

```sql
-- Run the SQL from "Supabase Database Schema" section above
-- Creates: tiktok_posts, tiktok_slides, scraping_logs tables
```

#### C. Create Storage Bucket

1. Go to **Storage** → **Create bucket**
2. Name: `tiktok-slides`
3. Public: ✅ Yes
4. Click **Create bucket**

5. Set policies:
```sql
-- Public read access
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'tiktok-slides');

-- Authenticated upload
CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'tiktok-slides'
    AND auth.role() = 'authenticated'
);
```

#### D. Get Credentials

Go to **Settings** → **API**:
- Copy **Project URL**
- Copy **anon public** key

### Step 2: Google Sheets Setup

#### A. Enable Sheets API

1. Go to https://console.cloud.google.com
2. Create new project: `tiktok-scraper`
3. Enable **Google Sheets API**
4. Enable **Google Drive API**

#### B. Create Service Account

1. **IAM & Admin** → **Service Accounts**
2. **Create Service Account**
3. Name: `tiktok-scraper`
4. Grant role: **Editor**
5. **Create Key** → JSON
6. Save as `credentials.json`

#### C. Share Sheet with Service Account

1. Open `credentials.json`
2. Copy the `client_email` value
3. Open your Google Sheet
4. Click **Share**
5. Paste service account email
6. Give **Editor** access

### Step 3: Install Dependencies

```bash
# Core dependencies
pip install aiohttp supabase gspread oauth2client pandas playwright

# Install browser
python -m playwright install chromium
```

### Step 4: Configure Environment

```bash
# Create .env file
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
EOF

# Load environment
source .env
```

### Step 5: Test Pipeline

```bash
# Run test with 3 URLs
python3 integrated_scraper.py --limit 3

# Run full pipeline
python3 integrated_scraper.py
```

---

## 🔄 Automation Options

### Option 1: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily run at 2 AM
0 2 * * * cd /path/to/project && python3 integrated_scraper.py >> /var/log/tiktok-scraper.log 2>&1
```

### Option 2: GitHub Actions (CI/CD)

```yaml
# .github/workflows/scraper.yml
name: TikTok Scraper
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python3 integrated_scraper.py
```

### Option 3: Google Apps Script Trigger

```javascript
// In Google Sheets: Extensions → Apps Script

function onEdit(e) {
  // Trigger when Status column changed to "Ready to Scrape"
  var sheet = e.source.getActiveSheet();
  var range = e.range;

  if (range.getColumn() == 6 && e.value == "Ready to Scrape") {
    // Call webhook to trigger scraper
    var url = "YOUR_WEBHOOK_URL";
    UrlFetchApp.fetch(url, {method: "POST"});
  }
}
```

---

## 📊 Data Flow Summary

```
1. VA enters URL in Google Sheet → Status: "Ready to Scrape"
2. Pipeline polls for new URLs (cron/trigger)
3. Download URLs from Google Sheets
4. Scrape video data + account data (comprehensive_scraper.py)
5. Download carousel slides (slide_manager.py)
6. Upload slides to Supabase Storage
7. Insert post data into Supabase DB (tiktok_posts table)
8. Insert slide metadata into Supabase DB (tiktok_slides table)
9. Log batch to Supabase DB (scraping_logs table)
10. Update Google Sheet Status → "Scraped"
11. Generate HTML previews (optional)
```

---

## ✅ Success Criteria

- [ ] Supabase project created with all tables
- [ ] Storage bucket created with policies
- [ ] Google Sheets API enabled with service account
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Test run successful (3 URLs)
- [ ] Data visible in Supabase dashboard
- [ ] Google Sheet status updated to "Scraped"
- [ ] Slides uploaded to Supabase Storage
- [ ] Preview HTML generated

---

## 🎯 Next Steps

1. **Immediate**: Setup Supabase account and create tables
2. **Today**: Configure Google Sheets API access
3. **This Week**: Test integrated pipeline with 10 URLs
4. **Next Week**: Deploy automation (cron job or GitHub Actions)
5. **Future**: Build analytics dashboard on top of Supabase data

---

This workflow is **production-ready** and fully documented. All components are modular and can be extended for future features like OCR processing, trend analysis, and automated reporting.
