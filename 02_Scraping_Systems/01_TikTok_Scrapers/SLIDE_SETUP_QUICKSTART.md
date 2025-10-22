# 🚀 Slide Management - Quick Start Guide

Get up and running with TikTok carousel slide downloads in 5 minutes.

## ⚡ Quick Setup (No Supabase)

### 1. Install Dependencies

```bash
pip install aiohttp
```

### 2. Process Existing Scraper Output

```bash
cd "02_Scraping_Systems/01_TikTok_Scrapers"

# Find CSV files with slides
ls -lh COMPREHENSIVE_SCRAPED_*.csv

# Process any CSV
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv
```

### 3. Open Preview

```bash
# Mac
open slide_cache/index.html

# Linux
xdg-open slide_cache/index.html

# Windows
start slide_cache\index.html
```

**Done!** 🎉 You can now:
- View all carousel slides in browser
- Screenshot individual slides
- Download slides with one click

---

## ☁️ Full Setup (With Supabase)

### 1. Install All Dependencies

```bash
pip install aiohttp supabase pandas playwright
python -m playwright install chromium
```

### 2. Setup Supabase Storage

#### A. Create Bucket
1. Go to https://app.supabase.com
2. Select your project
3. Go to **Storage** → **Create a new bucket**
4. **Bucket name**: `tiktok-slides`
5. **Public bucket**: ✅ Yes
6. Click **Create bucket**

#### B. Set Policies

Go to **Storage** → **tiktok-slides** → **Policies**

**Policy 1 - Public Read**:
```sql
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'tiktok-slides');
```

**Policy 2 - Authenticated Upload**:
```sql
CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'tiktok-slides'
    AND auth.role() = 'authenticated'
);
```

#### C. Get Credentials

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxx.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJxxx...your-anon-key
EOF

# Load environment
source .env
# Or on Windows: set SUPABASE_URL=... & set SUPABASE_KEY=...
```

### 4. Process with Upload

```bash
# Download AND upload to Supabase
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv --upload
```

### 5. Verify Upload

1. Go to Supabase Dashboard
2. **Storage** → **tiktok-slides** → **slides/**
3. You should see: `{post_id}_slide_{number}.jpg`

---

## 🎯 Usage Examples

### Example 1: Test with 3 Posts

```bash
# Run scraper on 3 URLs
python3 comprehensive_scraper.py --limit 3

# Process slides
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_3_VIDEOS_*.csv

# Open preview
open slide_cache/index.html
```

### Example 2: Production Run (50 Posts)

```bash
# Scrape 50 posts
python3 comprehensive_scraper.py --limit 50

# Download and upload slides
python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS_*.csv --upload

# Share preview
echo "Preview URL: file://$(pwd)/slide_cache/index.html"
```

### Example 3: Existing Data

```bash
# If you already have CSV with slides
python3 process_slides_from_csv.py /path/to/existing_data.csv
```

---

## 📸 Screenshot Workflow

Once preview is open in browser:

### For VA/Poster Use:

1. **Navigate**: Click post from index
2. **Screenshot**:
   - Mac: `Cmd + Shift + 4` → Select slide area
   - Windows: `Win + Shift + S` → Select area
3. **Save**: Screenshot auto-saves to desktop
4. **Next slide**: Scroll down, repeat

### Keyboard Shortcuts:

- `Cmd/Ctrl + S`: Download first slide
- `Scroll`: Navigate slides
- `Click Download`: Save specific slide

---

## 🔧 Troubleshooting

### "No carousel posts found"

**Cause**: CSV doesn't have slides or missing `slide_count` column

**Fix**:
```bash
# Check CSV has slide_count column
head -1 your_file.csv | grep slide_count

# If missing, run updated comprehensive_scraper.py first
```

### "aiohttp not found"

**Fix**:
```bash
pip install aiohttp
```

### "Supabase upload failed"

**Fix**:
1. Check environment variables:
   ```bash
   echo $SUPABASE_URL
   echo $SUPABASE_KEY
   ```
2. Verify bucket exists: `tiktok-slides`
3. Check bucket is public
4. Install supabase: `pip install supabase`

### "Images not loading in preview"

**Fix**:
1. Ensure slides downloaded: `ls slide_cache/*.jpg`
2. Open preview from correct directory
3. If using Supabase URLs, verify upload succeeded

---

## 📊 Expected Results

After processing, you should see:

```
slide_cache/
├── index.html                          # Main index page
├── 7330716631651519786_preview.html   # Individual previews
├── 7330716631651519786_slide_1.jpg    # Downloaded slides
├── 7330716631651519786_slide_2.jpg
└── ...
```

**File Sizes**:
- Slide image: ~200-500KB
- Preview HTML: ~5-10KB
- Index HTML: ~2-3KB

---

## 🎓 What's Next?

### For VAs:
1. Bookmark the index.html file location
2. Use preview for daily screenshot tasks
3. No need to open TikTok app

### For Developers:
1. Read full docs: `SLIDE_MANAGEMENT_SYSTEM.md`
2. Integrate into scraper: Import `SlideManager`
3. Customize HTML templates as needed

### For Production:
1. Setup automated scraping cron job
2. Auto-process slides after scraping
3. Share preview URL with team
4. Setup Supabase for permanent storage

---

## 📚 Full Documentation

- **Complete Guide**: `SLIDE_MANAGEMENT_SYSTEM.md`
- **API Reference**: See SlideManager class in `slide_manager.py`
- **Scraper Docs**: `TRANSFORMATION_GUIDE.md`

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Can run `python3 process_slides_from_csv.py` without errors
- [ ] `slide_cache/` directory created with files
- [ ] `index.html` opens in browser successfully
- [ ] Can see slide images in preview pages
- [ ] Download button works for slides
- [ ] (Optional) Supabase bucket shows uploaded files

---

## 🚀 Pro Tips

1. **Cache Reuse**: Already-downloaded slides skip re-download
2. **Rate Limiting**: Built-in delays prevent TikTok blocking
3. **URL Expiration**: TikTok CDN URLs expire after 24h - re-scrape if needed
4. **Batch Processing**: Process multiple CSVs by running script multiple times
5. **Preview Sharing**: Share `index.html` via Dropbox/Drive for team access

---

## 📞 Need Help?

Check the troubleshooting section above, or review:
- `SLIDE_MANAGEMENT_SYSTEM.md` - Full documentation
- `TRANSFORMATION_GUIDE.md` - CSV format details
- GitHub Issues - Report bugs

---

**Happy scraping!** 📸✨
