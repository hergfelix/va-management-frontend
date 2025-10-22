# TikTok Analytics Master Database - Architecture Brainstorming

**SuperClaude Flags**: `--brainstorm --think-hard --task-manage`

## 🎯 Ziel

Entwickle die optimale Architektur für ein TikTok Analytics System, das:
- 45k+ Posts mit vollständiger Historie verwaltet
- Historisches Performance-Tracking (Day 1-5) ermöglicht
- Slide-Level Analytics über Posts hinweg unterstützt
- Account & VA Performance Metriken tracked
- Auf 100k+ Posts skaliert

---

## 📊 Aktueller Status

### Vorhandene Daten

**MASTER_TIKTOK_DATABASE.csv** (45,077 Posts)
```
Columns (15): created_date, created_time, account, va, post_url, views, likes,
comments, shares, engagement, engagement_rate, hashtags, sound, slides, source
```

**master_with_snaptik.csv** (5 Test-Posts mit vollständiger Struktur)
```
Columns (67):
- Basic: va_url, post_url, created_date, creator, set_id, set_code, va, post_type,
  platform, account, logged_at, first_scraped_at
- Metrics: views, likes, comments, shares, engagement, engagement_rate, followers
- Time-Series: day1_views, day2_views, day3_views, day4_views, day5_views
- Scraping: last_scraped_at, scrape_status, scrape_interval, scrape_count, days_since_posted
- Content: hashtags, sound, sound_url, slide_count, ocr_text
- Slides: slide_1, slide_2, slide_3, ..., slide_12 (R2 Cloudflare URLs)
```

**tiktok_analytics.db** (SQLite, 91 MB)
```sql
-- Current schema (9 tables)
posts, slides, accounts, vas, creators, sets, post_metrics, performance_trends, metadata
```

---

## 🔑 Kern-Architektur-Fragen

### Q1: Historical Performance Tracking

**Problem**: Wir wollen Post-Performance über Zeit tracken (Day 1-5 und darüber hinaus)

**Option A: Flat Column Structure** (aktuell in master_with_snaptik.csv)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    post_url TEXT,
    day1_views INTEGER,
    day2_views INTEGER,
    day3_views INTEGER,
    day4_views INTEGER,
    day5_views INTEGER,
    -- ...
)
```
✅ **Pro**:
- Einfache Queries: `SELECT day1_views, day2_views FROM posts WHERE id = 123`
- Schnelle Aggregation für Dashboard
- Direkte CSV Import-Kompatibilität

❌ **Contra**:
- Limitiert auf 5 Tage (Erweiterung = Schema-Änderung)
- Keine exakten Scrape-Timestamps (nur "Day 1", "Day 2")
- Schwierig: "Wie viele Posts hatten >10k Views nach 48 Stunden?"
- Kein Scrape-Verlauf bei Fehlern

**Option B: Time-Series Table**
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    post_url TEXT,
    created_date DATETIME,
    -- core post data
);

CREATE TABLE metrics_snapshots (
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    scraped_at DATETIME,
    hours_since_posted REAL,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
```
✅ **Pro**:
- Unbegrenzte Time Windows
- Exakte Scrape-Timestamps
- Flexibel: Kann später daily/weekly scrapes hinzufügen
- Queries: "Performance nach genau 48h, 72h, 1 Woche"
- Scrape-History mit Fehlererkennung

❌ **Contra**:
- Komplexere Queries (JOINs erforderlich)
- Mehr Storage (jeder Scrape = neue Row)
- Aggregationen aufwendiger

**Option C: Hybrid Approach**
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    post_url TEXT,
    -- Cached for quick dashboard access
    day1_views INTEGER,
    day3_views INTEGER,
    day5_views INTEGER,
    final_views INTEGER, -- after 30 days
    -- ...
);

CREATE TABLE metrics_snapshots (
    -- Detailed history for analysis
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    scraped_at DATETIME,
    -- full metrics
);
```
✅ **Pro**: Beste Kombination aus Performance & Flexibilität
❌ **Contra**: Mehr Komplexität, Sync zwischen Tables

**❓ FRAGE**: Welcher Ansatz ist optimal für unser Use-Case?

---

### Q2: Slide-Level Data Storage

**Problem**: Jeder Post hat 1-12 Slides. Wir wollen:
- Slide-URLs speichern (R2 Cloudflare Links)
- OCR Text pro Slide
- Cross-Post Slide-Analyse ("Welche Slides performen gut?")
- Slide Reuse Detection

**Option A: Column-Based** (aktuell in master_with_snaptik.csv)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    slide_count INTEGER,
    slide_1 TEXT,
    slide_2 TEXT,
    slide_3 TEXT,
    -- ... bis slide_12
    ocr_text TEXT  -- Combined OCR for all slides
);
```
✅ **Pro**:
- Simple
- Direkter CSV Import
- Schnell für "Zeig mir alle Slides eines Posts"

❌ **Contra**:
- Limitiert auf 12 Slides
- Cross-Post Slide-Analyse unmöglich:
  - "Finde alle Posts, die Slide X verwenden" ❌
  - "Welche Slides haben beste Performance?" ❌
- OCR Text nicht slide-spezifisch
- Kein Image Hashing für Duplicate Detection

**Option B: Normalized Slides Table**
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    post_url TEXT,
    slide_count INTEGER
);

CREATE TABLE slides (
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    slide_index INTEGER,  -- 1-12
    slide_url TEXT,       -- R2 Cloudflare URL
    ocr_text TEXT,
    image_hash TEXT,      -- für Duplicate Detection
    width INTEGER,
    height INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    UNIQUE(post_id, slide_index)
);

CREATE INDEX idx_slides_hash ON slides(image_hash);
```
✅ **Pro**:
- Unbegrenzte Slides pro Post
- Cross-Post Slide-Analyse:
  ```sql
  -- Finde Reposts (gleiche Slides, andere Posts)
  SELECT s1.post_id, s2.post_id, s1.image_hash
  FROM slides s1
  JOIN slides s2 ON s1.image_hash = s2.image_hash
  WHERE s1.post_id != s2.post_id;

  -- Top-performing Slides
  SELECT s.slide_url, AVG(p.views) as avg_views
  FROM slides s
  JOIN posts p ON s.post_id = p.id
  GROUP BY s.image_hash
  ORDER BY avg_views DESC;
  ```
- Slide-spezifisches OCR
- Reusable Slide Library möglich

❌ **Contra**:
- Mehr JOIN Overhead
- Komplexere Queries für Basic Operations

**❓ FRAGE**: Welcher Ansatz für Slide Storage?

---

### Q3: Follower History Tracking

**Problem**: Account-Follower-Anzahl ändert sich über Zeit. Wir wollen:
- Follower Growth Trends
- Korrelation: "Post Performance vs Account Size"
- "War Account groß/klein als Post veröffentlicht wurde?"

**Option A: Post-Time Snapshot Only** (aktuell in master_with_snaptik.csv)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    account TEXT,
    followers INTEGER,  -- Follower count at post time
    created_date DATETIME
);
```
✅ **Pro**:
- Simple
- Direkter Context: "Post hatte X views bei Y followern"

❌ **Contra**:
- Kein Account Growth Tracking
- Kann nicht zeigen: "Account wuchs von 10k → 50k in 3 Monaten"
- Follower-Daten nur wenn Post erstellt wurde

**Option B: Account-Level Time-Series**
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    platform TEXT,
    creator TEXT,
    va TEXT
);

CREATE TABLE account_snapshots (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    snapshot_date DATE,
    followers INTEGER,
    total_posts INTEGER,
    total_likes INTEGER,
    total_views INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE(account_id, snapshot_date)
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    created_date DATETIME,
    followers_at_post_time INTEGER,  -- cached
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```
✅ **Pro**:
- Vollständige Account Growth History
- Queries: "Zeige Account-Wachstum über 6 Monate"
- Follower-Trends unabhängig von Posts
- Kann Account-Level KPIs berechnen:
  - Follower Growth Rate
  - Average Views per Follower
  - Engagement Rate Trends

❌ **Contra**:
- Mehr Storage
- Daily Scraping erforderlich für vollständige History
- Komplexere Queries

**Option C: Hybrid** (Cached + History)
```sql
-- Cached follower count in posts table for quick access
CREATE TABLE posts (
    followers_at_post_time INTEGER
);

-- Detailed history in separate table
CREATE TABLE account_snapshots (
    -- ...
);
```

**❓ FRAGE**: Wie sollten wir Follower History tracken?

---

### Q4: VA & Set Management

**Aktuell**: VA (Virtual Assistant) und Set (Content-Batch) sind wichtige Dimensionen

**Fragen**:
1. **VA Performance**: Wie tracken wir VA-spezifische KPIs?
   - Posts per VA
   - Average Performance per VA
   - VA Rankings
   - VA Efficiency (Posts/Day, Quality Score)

2. **Set Management**: Sets sind Content-Batches
   - Set Performance Tracking
   - Set-Level Analytics
   - Best/Worst Sets

**Vorgeschlagene Struktur**:
```sql
CREATE TABLE vas (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    joined_date DATE,
    status TEXT,  -- active, inactive, training
    notes TEXT
);

CREATE TABLE sets (
    id INTEGER PRIMARY KEY,
    set_code TEXT UNIQUE,  -- "SET001", "SET002"
    creator TEXT,
    created_date DATE,
    description TEXT
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    va_id INTEGER,
    set_id INTEGER,
    -- ...
    FOREIGN KEY (va_id) REFERENCES vas(id),
    FOREIGN KEY (set_id) REFERENCES sets(id)
);

-- VA Performance View
CREATE VIEW va_performance AS
SELECT
    v.name as va_name,
    COUNT(p.id) as total_posts,
    AVG(p.views) as avg_views,
    AVG(p.engagement_rate) as avg_engagement,
    SUM(CASE WHEN p.views > 10000 THEN 1 ELSE 0 END) as viral_posts
FROM vas v
LEFT JOIN posts p ON v.id = p.va_id
GROUP BY v.id;
```

**❓ FRAGE**: Sinnvolle Struktur für VA/Set Management?

---

### Q5: Performance Optimization

**Erwartete Load**:
- 45,000 Posts (aktuell) → 100,000+ Posts (Ziel)
- 92,000 Slides (aktuell) → 200,000+ Slides
- Daily Scraping für aktive Posts
- Dashboard Queries: <1 Sekunde

**Optimierungsstrategien**:

**Indexes**:
```sql
-- Performance-critical indexes
CREATE INDEX idx_posts_created_date ON posts(created_date);
CREATE INDEX idx_posts_account ON posts(account);
CREATE INDEX idx_posts_va ON posts(va_id);
CREATE INDEX idx_posts_views ON posts(views);
CREATE INDEX idx_metrics_post_scraped ON metrics_snapshots(post_id, scraped_at);
CREATE INDEX idx_slides_post ON slides(post_id);
CREATE INDEX idx_slides_hash ON slides(image_hash);
```

**Partitioning** (wenn DB wächst):
```sql
-- Posts nach Monat partitionieren
CREATE TABLE posts_2024_10 (
    CHECK (created_date >= '2024-10-01' AND created_date < '2024-11-01')
) INHERITS (posts);

CREATE TABLE posts_2024_11 (...);
```

**Materialized Views** für Dashboards:
```sql
-- Cached aggregations, refresh hourly
CREATE MATERIALIZED VIEW dashboard_summary AS
SELECT
    DATE(created_date) as date,
    COUNT(*) as posts_count,
    SUM(views) as total_views,
    AVG(engagement_rate) as avg_engagement
FROM posts
GROUP BY DATE(created_date);
```

**Caching Strategy**:
- Redis für Dashboard Queries
- Cache TTL: 5 minutes für Live Data, 1 hour für Historical
- Pre-compute VA Rankings, Set Performance

**❓ FRAGE**: Welche Optimierungen sind prioritär?

---

### Q6: Migration Strategy

**Challenge**: 45,077 Posts von basic CSV → full structure

**Vorhandene Daten**:
- ✅ MASTER_TIKTOK_DATABASE.csv: 45k Posts, basic metrics
- ✅ master_with_snaptik.csv: 5 Posts, vollständige Struktur (Template)
- ❌ Missing: Follower History, Day 1-5 Tracking, R2 Slide URLs, OCR Text

**Migration Options**:

**Option A: Minimale Migration**
```python
# Migriere nur vorhandene Daten
- Import 45k posts mit basic metrics
- Follower = NULL (füllen wir später)
- day1-5_views = NULL (nur für neue Posts)
- Slides = NULL (scrapen wir nach Bedarf)
```
✅ Schnell, sofort einsatzbereit
❌ Incomplete Data für Analysen

**Option B: Backfill mit Scraping**
```python
# 1. Basis-Migration
- Import 45k posts

# 2. Progressive Backfill
- Top 1000 Posts (by views): Full rescrape + R2 upload
- Top 5000 Posts: Scrape current metrics only
- Rest: Keep basic data
```
✅ Wichtigste Daten vollständig
❌ Zeitaufwendig (Tage)

**Option C: Fresh Start + Selective Import**
```python
# Neue DB mit vollständiger Struktur
- Import nur Posts der letzten 90 Tage (vollständig)
- Ältere Posts: Basic import, kein Backfill
- Fokus: Neue Posts ab heute = vollständige Daten
```
✅ Beste Datenqualität für aktuelle Posts
❌ Historische Daten incomplete

**❓ FRAGE**: Welche Migration Strategy?

---

## 🎯 5-Ebenen System Requirements

### Ebene 1: Slideshow Performance & Repost Intelligence
- Slide-Level Analytics
- Repost Detection (gleiche Slides, verschiedene Posts)
- Best-Performing Slides
- Slide Reuse Recommendations

### Ebene 2: Account Performance & KPI Dashboard
- Account Growth Tracking
- KPI Scoring (0-100)
- Performance vs Baseline
- Viral Rate, Engagement Quality

### Ebene 3: VA Performance & Management
- VA Rankings
- Posts per VA, Quality Scores
- VA Efficiency Metrics
- Improvement Plans

### Ebene 4: Revenue Attribution & ROI
- Revenue per Post/Account/VA
- Cost Tracking (VA Zeit, Tools)
- ROI Berechnung

### Ebene 5: Content & Creator Management
- Creator Performance
- Content Pipeline
- Task Management (Reel Lists)

**❓ FRAGE**: Welche DB-Strukturen brauchen wir für jede Ebene?

---

## 📋 Erwartete Outputs

Bitte liefere:

1. **Empfohlenes DB Schema** (SQL DDL)
   - Alle Tables mit Columns
   - Primary Keys, Foreign Keys
   - Indexes

2. **Architektur-Begründung**
   - Warum diese Struktur?
   - Trade-offs erklärt
   - Skalierbarkeit

3. **Migration Plan**
   - Schritt-für-Schritt
   - Bash/Python Scripts
   - Batch Sizes, Timing

4. **Performance Optimierungen**
   - Kritische Indexes
   - Caching Strategy
   - Query Optimierung

5. **Beispiel-Queries**
   - Für jede der 5 Ebenen
   - Dashboard Queries
   - Analytics Queries

6. **Implementierungs-Roadmap**
   - Phase 1: Core Schema + Migration
   - Phase 2: Time-Series + Slide Analytics
   - Phase 3: Advanced Features (VA Scoring, Revenue)
   - Phase 4: Optimierungen

---

## 🚀 Next Steps nach Architecture Decision

1. **Schema erstellen** (SQL DDL)
2. **Migration Scripts** (Python)
3. **R2 Cloudflare Integration** (Slide Upload)
4. **Scraping Pipeline** (Day 1-5 Tracking)
5. **Dashboard Development** (Streamlit/Dash)
6. **5-Ebenen System Implementation**

---

**Aktiviere bitte**:
- `business-panel-experts` für KPI & Strategy-Entscheidungen
- `system-architect` für DB Schema Design
- `python-expert` für Migration & Scraping Scripts
- `backend-architect` für Performance Optimierung

**Lass uns systematisch durchgehen und die beste Lösung finden!** 🎯
