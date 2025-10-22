# 📊 How to View Your Database

## 🎯 Your Database Contains:

**45,077 posts** from VAs like:
- miriamrollqueen (1.3M views)
- maraglowsyyy (1.2M views)
- miriamsweets (1.2M views)
- tyrastare (1.2M views)

**92,382 carousel slides** tracked

**49 VAs** in the system

## ✅ 3 Ways to View Your Data:

---

### Option 1: 📁 CSV Files (Just Created!)

**Location**: `./exports/` folder (just opened for you!)

**Files created:**
- ✅ `posts_[timestamp].csv` - **45,077 posts** (main data)
- ✅ `slides_[timestamp].csv` - **92,382 slides** (carousel images)
- ✅ `vas_[timestamp].csv` - **49 VAs** (virtual assistants)
- ✅ `metrics_snapshots_[timestamp].csv` - **1,115 snapshots**
- ✅ `data_import_log_[timestamp].csv` - Import history
- ✅ `tiktok_slides_[timestamp].csv` - New slide tracking

**How to view:**
- Double-click any CSV to open in **Excel** or **Numbers**
- Or drag to **Google Sheets**
- Works like a regular spreadsheet!

**To export again:**
```bash
python3 export_to_csv.py
```

---

### Option 2: 🖥️ Visual Database Browser (Best!)

Install DB Browser (free, like Excel but for databases):

```bash
brew install --cask db-browser-for-sqlite
```

Then open your database:
```bash
open -a "DB Browser for SQLite" tiktok_analytics.db
```

**Features:**
- 📊 Browse all tables visually
- 🔍 Filter and sort data
- 📝 Run custom queries
- 📈 View relationships between tables
- 💾 Export to CSV anytime
- 🎨 Beautiful interface

**Screenshot of what you'll see:**
- Left sidebar: List of tables (posts, slides, vas, etc.)
- Main area: Data grid (like Excel)
- Bottom: SQL query box
- Top: Export, filter, search buttons

---

### Option 3: 💻 Command Line (Quick Queries)

For quick lookups:

```bash
sqlite3 tiktok_analytics.db
```

**Useful queries:**

```sql
-- Count total posts
SELECT COUNT(*) FROM posts;

-- Top 10 posts by views
SELECT account, views, likes, post_url
FROM posts
ORDER BY views DESC
LIMIT 10;

-- Posts by VA
SELECT va, COUNT(*) as post_count, SUM(views) as total_views
FROM posts
GROUP BY va
ORDER BY total_views DESC;

-- Recent posts
SELECT account, views, created_at, post_url
FROM posts
WHERE created_at > date('now', '-7 days')
ORDER BY views DESC;

-- Export specific data to CSV
.headers on
.mode csv
.output my_export.csv
SELECT * FROM posts WHERE views > 100000;
.output stdout

-- Exit
.exit
```

---

## 🚀 Quick Access Commands:

### View in Finder
```bash
open exports/
```

### Export fresh CSV files
```bash
python3 export_to_csv.py
```

### Open database in GUI
```bash
open -a "DB Browser for SQLite" tiktok_analytics.db
```

### Quick stats
```bash
python3 -c "from export_to_csv import show_preview; show_preview()"
```

---

## 📈 What's the Difference?

| Method | Best For | Speed |
|--------|----------|-------|
| **CSV Export** | Sharing data, Excel analysis | Medium |
| **DB Browser** | Exploring, filtering, complex queries | Fast |
| **Command Line** | Quick lookups, automation | Instant |

---

## 💡 Pro Tips:

### 1. Custom Exports

Export just what you need:

```python
from export_to_csv import export_custom_query

# Export top performers
export_custom_query(
    "./tiktok_analytics.db",
    "SELECT * FROM posts WHERE views > 500000 ORDER BY views DESC",
    "./exports/top_performers.csv"
)

# Export specific VA
export_custom_query(
    "./tiktok_analytics.db",
    "SELECT * FROM posts WHERE va = 'SofiaVA' ORDER BY views DESC",
    "./exports/sofia_posts.csv"
)
```

### 2. Google Sheets Import

1. Open Google Sheets
2. **File** → **Import**
3. **Upload** → Select your CSV
4. Choose **Replace** or **Insert new sheet**
5. Done!

### 3. Excel Pivot Tables

Your CSV files work perfectly with Excel Pivot Tables:
1. Open `posts_[timestamp].csv` in Excel
2. **Insert** → **Pivot Table**
3. Analyze by VA, views, dates, etc.

---

## 🔄 Keep Data Fresh:

### Re-export anytime:
```bash
python3 export_to_csv.py
```

### Automatic exports (add to your scraper):
```python
# At the end of your scraper
from export_to_csv import export_all_tables
export_all_tables()
print("✅ Database updated and exported to CSV!")
```

---

## 📊 Your Data Summary:

**Total Posts**: 45,077
**Total Slides**: 92,382
**Total VAs**: 49
**Total View Count**: Millions!

**Top Post**:
- miriamrollqueen
- 1,300,000 views
- 50,500 likes
- https://www.tiktok.com/@miriamrollqueen/video/7530833330200235278

---

## 🎉 Bottom Line:

**YES, you can view it like CSV!**

I just exported everything to the `exports/` folder (opened it for you). Double-click any file to open in Excel/Numbers/Sheets. Works exactly like regular spreadsheets!

**Want the full experience?** Install DB Browser for a beautiful visual interface that's way better than CSV!

---

**CSV Location**: `./exports/`
**Database**: `./tiktok_analytics.db`
**Export Tool**: `./export_to_csv.py`
