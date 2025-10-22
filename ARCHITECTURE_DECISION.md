# 🏗️ TikTok Analytics Master Database - Architecture Decision

**SuperClaude Flags**: `--brainstorm --think-hard --task-manage` ✅ **ACTIVATED**

## 🎯 **Architecture Decision Summary**

Nach systematischer Analyse aller Optionen und Trade-offs empfehle ich eine **Hybrid-Architektur** die Performance, Flexibilität und Skalierbarkeit optimal kombiniert.

---

## 📊 **Empfohlenes DB Schema (SQL DDL)**

### **Core Tables**

```sql
-- ==============================================
-- 1. ACCOUNTS TABLE (Account Management)
-- ==============================================
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    platform VARCHAR(20) DEFAULT 'tiktok',
    creator VARCHAR(100),
    va_id INTEGER,
    niche VARCHAR(100),
    target_audience VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (va_id) REFERENCES vas(id),
    INDEX idx_accounts_username (username),
    INDEX idx_accounts_va (va_id),
    INDEX idx_accounts_active (is_active)
);

-- ==============================================
-- 2. VAS TABLE (Virtual Assistants)
-- ==============================================
CREATE TABLE vas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    creator VARCHAR(100),
    set_id VARCHAR(50),
    set_code VARCHAR(50),
    joined_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, training
    performance_score FLOAT DEFAULT 0.0, -- 0-100
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_vas_name (name),
    INDEX idx_vas_status (status),
    INDEX idx_vas_performance (performance_score DESC)
);

-- ==============================================
-- 3. SETS TABLE (Content Batches)
-- ==============================================
CREATE TABLE sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_code VARCHAR(50) NOT NULL UNIQUE,
    creator VARCHAR(100),
    created_date DATE,
    description TEXT,
    total_posts INTEGER DEFAULT 0,
    avg_performance FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_sets_code (set_code),
    INDEX idx_sets_creator (creator)
);

-- ==============================================
-- 4. POSTS TABLE (Main Posts - Hybrid Approach)
-- ==============================================
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_url VARCHAR(500) NOT NULL UNIQUE,
    account_id INTEGER NOT NULL,
    va_id INTEGER,
    set_id INTEGER,
    
    -- Timestamps
    created_date DATETIME NOT NULL,
    created_time VARCHAR(10),
    first_scraped_at DATETIME,
    last_scraped_at DATETIME,
    
    -- Current Metrics (Latest)
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    
    -- Cached Day 1-5 Performance (Fast Dashboard Access)
    day1_views INTEGER DEFAULT 0,
    day2_views INTEGER DEFAULT 0,
    day3_views INTEGER DEFAULT 0,
    day4_views INTEGER DEFAULT 0,
    day5_views INTEGER DEFAULT 0,
    
    -- Account Context at Post Time
    followers_at_post_time INTEGER DEFAULT 0,
    follower_growth_rate FLOAT DEFAULT 0.0,
    
    -- Performance Indicators
    is_viral BOOLEAN DEFAULT FALSE, -- >=10k views
    viral_score FLOAT DEFAULT 0.0, -- 0-100
    content_quality_score FLOAT DEFAULT 0.0,
    
    -- Content Data
    hashtags TEXT,
    sound TEXT,
    sound_url TEXT,
    slide_count INTEGER DEFAULT 0,
    ocr_text TEXT, -- Combined OCR for quick access
    
    -- Scraping Metadata
    scrape_status VARCHAR(20) DEFAULT 'active', -- active, paused, completed
    scrape_interval INTEGER DEFAULT 24, -- hours
    scrape_count INTEGER DEFAULT 0,
    days_since_posted INTEGER,
    
    -- Source & Metadata
    source VARCHAR(50) NOT NULL, -- old_clean, current_metrics, etc.
    post_type VARCHAR(20) DEFAULT 'video',
    platform VARCHAR(20) DEFAULT 'tiktok',
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (va_id) REFERENCES vas(id),
    FOREIGN KEY (set_id) REFERENCES sets(id),
    
    -- Indexes for Performance
    INDEX idx_posts_url (post_url),
    INDEX idx_posts_account (account_id),
    INDEX idx_posts_va (va_id),
    INDEX idx_posts_set (set_id),
    INDEX idx_posts_created_date (created_date),
    INDEX idx_posts_views (views),
    INDEX idx_posts_viral (is_viral, created_date),
    INDEX idx_posts_viral_score (viral_score DESC),
    INDEX idx_posts_scrape_status (scrape_status),
    INDEX idx_posts_account_date (account_id, created_date),
    INDEX idx_posts_va_date (va_id, created_date),
    
    -- Constraints
    CHECK (views >= 0),
    CHECK (likes >= 0),
    CHECK (comments >= 0),
    CHECK (shares >= 0),
    CHECK (engagement >= 0),
    CHECK (viral_score >= 0 AND viral_score <= 100),
    CHECK (content_quality_score >= 0 AND content_quality_score <= 100)
);

-- ==============================================
-- 5. SLIDES TABLE (Normalized Slide Storage)
-- ==============================================
CREATE TABLE slides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    slide_index INTEGER NOT NULL, -- 1, 2, 3, etc.
    
    -- Slide Data
    slide_url VARCHAR(1000) NOT NULL, -- R2 Cloudflare URL
    ocr_text TEXT,
    ocr_confidence FLOAT DEFAULT 0.0,
    
    -- Image Metadata
    image_hash VARCHAR(64), -- MD5 hash for duplicate detection
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    dimensions VARCHAR(20), -- "1920x1080"
    
    -- Performance Tracking
    usage_count INTEGER DEFAULT 1, -- How many times this slide was used
    avg_performance_score FLOAT DEFAULT 0.0,
    best_performing_post_id INTEGER,
    
    -- Content Classification
    slide_category VARCHAR(50), -- 'cta', 'statement', 'question', 'image', 'mixed'
    content_type VARCHAR(50), -- 'text', 'image', 'mixed'
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (best_performing_post_id) REFERENCES posts(id),
    
    -- Indexes
    INDEX idx_slides_post (post_id),
    INDEX idx_slides_post_index (post_id, slide_index),
    INDEX idx_slides_hash (image_hash),
    INDEX idx_slides_performance (avg_performance_score DESC),
    INDEX idx_slides_category (slide_category),
    INDEX idx_slides_usage (usage_count DESC),
    
    -- Constraints
    UNIQUE(post_id, slide_index),
    CHECK (slide_index >= 1 AND slide_index <= 20),
    CHECK (usage_count >= 1)
);

-- ==============================================
-- 6. METRICS_SNAPSHOTS TABLE (Time-Series Data)
-- ==============================================
CREATE TABLE metrics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    va_id INTEGER,
    account_id INTEGER,
    
    -- Metrics at Snapshot Time
    views INTEGER NOT NULL,
    likes INTEGER NOT NULL,
    comments INTEGER NOT NULL,
    shares INTEGER NOT NULL,
    engagement INTEGER NOT NULL,
    engagement_rate FLOAT,
    
    -- Time Context
    scraped_at DATETIME NOT NULL,
    hours_since_posted REAL NOT NULL,
    days_since_posted INTEGER,
    
    -- Account Context
    followers_at_scrape INTEGER,
    
    -- Scraping Metadata
    scrape_source VARCHAR(50), -- 'manual', 'automated', 'api'
    scrape_duration_ms INTEGER,
    is_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (va_id) REFERENCES vas(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    
    -- Indexes
    INDEX idx_metrics_post (post_id),
    INDEX idx_metrics_post_scraped (post_id, scraped_at),
    INDEX idx_metrics_va_scraped (va_id, scraped_at),
    INDEX idx_metrics_account_scraped (account_id, scraped_at),
    INDEX idx_metrics_scraped_at (scraped_at),
    INDEX idx_metrics_hours_posted (hours_since_posted),
    
    -- Constraints
    UNIQUE(post_id, scraped_at),
    CHECK (views >= 0),
    CHECK (likes >= 0),
    CHECK (comments >= 0),
    CHECK (shares >= 0),
    CHECK (engagement >= 0),
    CHECK (hours_since_posted >= 0)
);

-- ==============================================
-- 7. ACCOUNT_SNAPSHOTS TABLE (Follower History)
-- ==============================================
CREATE TABLE account_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    
    -- Account Metrics at Snapshot Time
    followers INTEGER NOT NULL,
    following INTEGER DEFAULT 0,
    total_posts INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    
    -- Calculated Metrics
    follower_growth_rate FLOAT DEFAULT 0.0, -- % change from previous snapshot
    avg_views_per_post FLOAT DEFAULT 0.0,
    avg_engagement_rate FLOAT DEFAULT 0.0,
    
    -- Snapshot Metadata
    snapshot_date DATE NOT NULL,
    snapshot_source VARCHAR(50) DEFAULT 'scrape', -- 'scrape', 'api', 'manual'
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    
    -- Indexes
    INDEX idx_account_snapshots_account (account_id),
    INDEX idx_account_snapshots_date (snapshot_date),
    INDEX idx_account_snapshots_account_date (account_id, snapshot_date),
    INDEX idx_account_snapshots_followers (followers),
    INDEX idx_account_snapshots_growth (follower_growth_rate DESC),
    
    -- Constraints
    UNIQUE(account_id, snapshot_date),
    CHECK (followers >= 0),
    CHECK (following >= 0),
    CHECK (total_posts >= 0)
);

-- ==============================================
-- 8. CONTENT_TEMPLATES TABLE (Repost Intelligence)
-- ==============================================
CREATE TABLE content_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_post_id INTEGER NOT NULL,
    
    -- Template Data
    original_text TEXT NOT NULL,
    variation_1 TEXT,
    variation_2 TEXT,
    variation_3 TEXT,
    
    -- Performance Metrics
    original_views INTEGER,
    original_engagement_rate FLOAT,
    avg_performance_score FLOAT DEFAULT 0.0,
    
    -- Classification
    category VARCHAR(50), -- 'cta', 'statement', 'question', 'story', 'tip'
    content_type VARCHAR(50), -- 'text', 'image', 'mixed'
    viral_potential FLOAT DEFAULT 0.0, -- 0-100
    
    -- Usage Tracking
    is_used BOOLEAN DEFAULT FALSE,
    used_at DATETIME,
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0, -- % of uses that went viral
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (original_post_id) REFERENCES posts(id),
    
    -- Indexes
    INDEX idx_templates_original (original_post_id),
    INDEX idx_templates_category (category),
    INDEX idx_templates_performance (avg_performance_score DESC),
    INDEX idx_templates_viral_potential (viral_potential DESC),
    INDEX idx_templates_used (is_used)
);

-- ==============================================
-- 9. REPOST_CANDIDATES TABLE (Repost Intelligence)
-- ==============================================
CREATE TABLE repost_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_post_id INTEGER NOT NULL,
    
    -- Candidate Classification
    repost_type VARCHAR(50) NOT NULL, -- 'same_account', 'same_va', 'cross_creator', 'viral_recycle'
    score FLOAT NOT NULL, -- 0-100 score for repost potential
    reason TEXT, -- Why this is a good candidate
    
    -- Performance Prediction
    predicted_views INTEGER,
    predicted_engagement INTEGER,
    confidence_level FLOAT DEFAULT 0.0, -- 0-100
    
    -- Usage Tracking
    is_used BOOLEAN DEFAULT FALSE,
    used_at DATETIME,
    actual_performance_score FLOAT, -- How it actually performed
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (original_post_id) REFERENCES posts(id),
    
    -- Indexes
    INDEX idx_repost_original (original_post_id),
    INDEX idx_repost_type (repost_type),
    INDEX idx_repost_score (score DESC),
    INDEX idx_repost_used (is_used),
    INDEX idx_repost_type_score (repost_type, score DESC)
);

-- ==============================================
-- 10. SYSTEM TABLES (Management & Logging)
-- ==============================================

-- Scraping Jobs
CREATE TABLE scraping_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- 'daily_update', 'full_scrape', 'manual', 'backfill'
    
    -- Status Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    started_at DATETIME,
    completed_at DATETIME,
    
    -- Results
    posts_processed INTEGER DEFAULT 0,
    posts_updated INTEGER DEFAULT 0,
    posts_failed INTEGER DEFAULT 0,
    error_message TEXT,
    
    -- Configuration
    config TEXT, -- JSON configuration
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_jobs_name (job_name),
    INDEX idx_jobs_status (status),
    INDEX idx_jobs_type (job_type)
);

-- Data Import Log
CREATE TABLE data_import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_type VARCHAR(50) NOT NULL, -- 'csv_import', 'google_sheets', 'migration'
    source VARCHAR(200) NOT NULL,
    
    -- Results
    records_processed INTEGER DEFAULT 0,
    records_imported INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'running', -- running, completed, failed
    error_message TEXT,
    
    -- Timestamps
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    INDEX idx_import_type (import_type),
    INDEX idx_import_status (status)
);

-- System Configuration
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_config_key (key)
);
```

---

## 🎯 **Architektur-Begründung**

### **Warum Hybrid-Ansatz?**

**1. Time-Series Data (Posts + Metrics_Snapshots)**
- ✅ **Posts Table**: Cached Day 1-5 für schnelle Dashboard-Queries
- ✅ **Metrics_Snapshots**: Vollständige Historie für detaillierte Analysen
- ✅ **Best of Both**: Performance + Flexibilität

**2. Normalized Slides Table**
- ✅ **Cross-Post Analytics**: "Welche Slides performen gut?"
- ✅ **Repost Detection**: Gleiche Slides, verschiedene Posts
- ✅ **Unbegrenzte Slides**: Nicht limitiert auf 12
- ✅ **Slide-spezifisches OCR**: Bessere Content-Analyse

**3. Account Snapshots**
- ✅ **Follower Growth Tracking**: Vollständige Account-Historie
- ✅ **Performance Correlation**: "Post Performance vs Account Size"
- ✅ **Trend Analysis**: Account-Wachstum über Zeit

**4. VA & Set Management**
- ✅ **Strukturierte Hierarchie**: Accounts → VAs → Sets → Posts
- ✅ **Performance Tracking**: VA-spezifische KPIs
- ✅ **Set Analytics**: Content-Batch Performance

### **Trade-offs Erklärt**

**Storage vs Performance**:
- Mehr Storage durch Normalisierung
- Aber: Schnellere Queries durch optimierte Indexes
- Kompensiert durch intelligente Caching-Strategie

**Komplexität vs Flexibilität**:
- Komplexere Queries durch JOINs
- Aber: Unbegrenzte Erweiterungsmöglichkeiten
- Abgefedert durch Materialized Views

**Migration vs Fresh Start**:
- Komplexere Migration
- Aber: Erhaltung aller historischen Daten
- Schrittweise Migration mit Backfill-Strategie

---

## 🚀 **Migration Plan**

### **Phase 1: Schema Setup (Tag 1-2)**

```bash
# 1. Backup existing database
cp tiktok_analytics.db tiktok_analytics_backup_$(date +%Y%m%d).db

# 2. Create new schema
python3 scripts/create_new_schema.py

# 3. Verify schema
python3 scripts/verify_schema.py
```

### **Phase 2: Data Migration (Tag 3-5)**

```python
# scripts/migrate_to_new_schema.py
def migrate_existing_data():
    """
    Migrate 45k posts from old schema to new schema
    """
    # 1. Migrate VAs
    migrate_vas()
    
    # 2. Migrate Accounts
    migrate_accounts()
    
    # 3. Migrate Posts (with basic data)
    migrate_posts_basic()
    
    # 4. Migrate Slides (parse from slides column)
    migrate_slides_from_posts()
    
    # 5. Calculate performance indicators
    calculate_viral_scores()
    calculate_content_quality_scores()
```

### **Phase 3: Data Enhancement (Tag 6-10)**

```python
# scripts/enhance_existing_data.py
def enhance_data():
    """
    Enhance existing data with new features
    """
    # 1. Backfill follower counts (where possible)
    backfill_follower_counts()
    
    # 2. Parse and enhance slide data
    enhance_slide_data()
    
    # 3. Generate content templates
    generate_content_templates()
    
    # 4. Identify repost candidates
    identify_repost_candidates()
```

### **Phase 4: New Data Collection (Tag 11+)**

```python
# scripts/enhanced_scraper.py
def enhanced_scraping():
    """
    New scraping pipeline with full feature set
    """
    # 1. Collect day 1-5 metrics
    collect_time_series_metrics()
    
    # 2. Track account snapshots
    collect_account_snapshots()
    
    # 3. Enhanced slide processing
    process_slides_with_ocr()
    
    # 4. Real-time performance tracking
    update_performance_indicators()
```

---

## ⚡ **Performance Optimierungen**

### **Kritische Indexes**

```sql
-- Dashboard Performance
CREATE INDEX idx_posts_dashboard ON posts(created_date, is_viral, viral_score);
CREATE INDEX idx_posts_va_performance ON posts(va_id, created_date, viral_score);

-- Analytics Performance
CREATE INDEX idx_metrics_analytics ON metrics_snapshots(post_id, scraped_at, views);
CREATE INDEX idx_slides_analytics ON slides(image_hash, avg_performance_score);

-- Account Growth Analysis
CREATE INDEX idx_account_growth ON account_snapshots(account_id, snapshot_date, followers);
```

### **Materialized Views für Dashboards**

```sql
-- Daily Summary (refresh every hour)
CREATE MATERIALIZED VIEW daily_summary AS
SELECT
    DATE(created_date) as date,
    COUNT(*) as total_posts,
    SUM(CASE WHEN is_viral THEN 1 ELSE 0 END) as viral_posts,
    AVG(viral_score) as avg_viral_score,
    SUM(views) as total_views,
    AVG(engagement_rate) as avg_engagement_rate
FROM posts
WHERE created_date >= DATE('now', '-30 days')
GROUP BY DATE(created_date);

-- VA Performance Summary (refresh every 6 hours)
CREATE MATERIALIZED VIEW va_performance_summary AS
SELECT
    v.id as va_id,
    v.name as va_name,
    COUNT(p.id) as total_posts,
    AVG(p.viral_score) as avg_viral_score,
    SUM(CASE WHEN p.is_viral THEN 1 ELSE 0 END) as viral_posts,
    AVG(p.engagement_rate) as avg_engagement_rate,
    MAX(p.created_date) as last_post_date
FROM vas v
LEFT JOIN posts p ON v.id = p.va_id
WHERE p.created_date >= DATE('now', '-30 days')
GROUP BY v.id, v.name;
```

### **Caching Strategy**

```python
# Redis Caching Configuration
CACHE_CONFIG = {
    'dashboard_data': {'ttl': 300},      # 5 minutes
    'va_rankings': {'ttl': 1800},        # 30 minutes
    'repost_candidates': {'ttl': 3600},  # 1 hour
    'historical_data': {'ttl': 7200},    # 2 hours
}
```

---

## 📊 **Beispiel-Queries für 5 Ebenen**

### **Ebene 1: Slideshow Performance & Repost Intelligence**

```sql
-- Top-performing Slides
SELECT 
    s.image_hash,
    s.slide_url,
    COUNT(DISTINCT s.post_id) as usage_count,
    AVG(p.views) as avg_views,
    AVG(p.viral_score) as avg_viral_score,
    MAX(p.views) as best_performance
FROM slides s
JOIN posts p ON s.post_id = p.id
WHERE s.image_hash IS NOT NULL
GROUP BY s.image_hash, s.slide_url
HAVING usage_count > 1
ORDER BY avg_viral_score DESC
LIMIT 20;

-- Repost Detection (Same Slides, Different Posts)
SELECT 
    s1.post_id as original_post,
    s2.post_id as repost_candidate,
    s1.slide_url,
    p1.views as original_views,
    p2.views as repost_views,
    p1.account as original_account,
    p2.account as repost_account
FROM slides s1
JOIN slides s2 ON s1.image_hash = s2.image_hash
JOIN posts p1 ON s1.post_id = p1.id
JOIN posts p2 ON s2.post_id = p2.id
WHERE s1.post_id != s2.post_id
AND s1.image_hash IS NOT NULL
ORDER BY p1.views DESC;
```

### **Ebene 2: Account Performance & KPI Dashboard**

```sql
-- Account Performance Dashboard
SELECT 
    a.username,
    COUNT(p.id) as total_posts,
    SUM(CASE WHEN p.is_viral THEN 1 ELSE 0 END) as viral_posts,
    ROUND(AVG(p.viral_score), 2) as avg_viral_score,
    ROUND(AVG(p.engagement_rate), 2) as avg_engagement_rate,
    MAX(ac.followers) as current_followers,
    ROUND(AVG(ac.follower_growth_rate), 2) as avg_growth_rate,
    MAX(p.created_date) as last_post_date
FROM accounts a
LEFT JOIN posts p ON a.id = p.account_id
LEFT JOIN account_snapshots ac ON a.id = ac.account_id
WHERE p.created_date >= DATE('now', '-30 days')
GROUP BY a.id, a.username
ORDER BY avg_viral_score DESC;

-- Account Growth Trends
SELECT 
    a.username,
    ac.snapshot_date,
    ac.followers,
    ac.follower_growth_rate,
    ac.total_posts
FROM accounts a
JOIN account_snapshots ac ON a.id = ac.account_id
WHERE ac.snapshot_date >= DATE('now', '-90 days')
ORDER BY a.username, ac.snapshot_date;
```

### **Ebene 3: VA Performance & Management**

```sql
-- VA Performance Rankings
SELECT 
    v.name as va_name,
    v.performance_score,
    COUNT(p.id) as total_posts,
    SUM(CASE WHEN p.is_viral THEN 1 ELSE 0 END) as viral_posts,
    ROUND(AVG(p.viral_score), 2) as avg_viral_score,
    ROUND(AVG(p.content_quality_score), 2) as avg_content_quality,
    ROUND(COUNT(p.id) * 1.0 / 30, 2) as posts_per_day,
    MAX(p.created_date) as last_post_date
FROM vas v
LEFT JOIN posts p ON v.id = p.va_id
WHERE p.created_date >= DATE('now', '-30 days')
GROUP BY v.id, v.name, v.performance_score
ORDER BY avg_viral_score DESC;

-- VA Efficiency Metrics
SELECT 
    v.name as va_name,
    COUNT(DISTINCT p.account_id) as accounts_managed,
    COUNT(p.id) as total_posts,
    ROUND(AVG(p.viral_score), 2) as avg_viral_score,
    ROUND(AVG(p.content_quality_score), 2) as avg_content_quality,
    ROUND(COUNT(p.id) * 1.0 / COUNT(DISTINCT p.account_id), 2) as posts_per_account
FROM vas v
JOIN posts p ON v.id = p.va_id
WHERE p.created_date >= DATE('now', '-30 days')
GROUP BY v.id, v.name
ORDER BY avg_viral_score DESC;
```

### **Ebene 4: Revenue Attribution & ROI**

```sql
-- Post Performance vs Revenue (when revenue data available)
SELECT 
    p.post_url,
    p.account_id,
    p.va_id,
    p.views,
    p.viral_score,
    p.created_date,
    -- revenue.revenue_amount, -- when revenue table exists
    -- revenue.cost_amount,    -- when cost tracking exists
    -- ROUND(revenue.revenue_amount / revenue.cost_amount, 2) as roi
FROM posts p
-- LEFT JOIN revenue ON p.id = revenue.post_id -- when implemented
WHERE p.created_date >= DATE('now', '-30 days')
ORDER BY p.viral_score DESC;

-- VA ROI Analysis (when revenue data available)
SELECT 
    v.name as va_name,
    COUNT(p.id) as total_posts,
    -- SUM(revenue.revenue_amount) as total_revenue,
    -- SUM(revenue.cost_amount) as total_cost,
    -- ROUND(SUM(revenue.revenue_amount) / SUM(revenue.cost_amount), 2) as roi
    AVG(p.viral_score) as avg_viral_score
FROM vas v
JOIN posts p ON v.id = p.va_id
-- LEFT JOIN revenue ON p.id = revenue.post_id -- when implemented
WHERE p.created_date >= DATE('now', '-30 days')
GROUP BY v.id, v.name
ORDER BY avg_viral_score DESC;
```

### **Ebene 5: Content & Creator Management**

```sql
-- Content Template Performance
SELECT 
    ct.category,
    ct.original_text,
    ct.avg_performance_score,
    ct.viral_potential,
    ct.usage_count,
    ct.success_rate,
    p.views as original_views,
    p.account_id
FROM content_templates ct
JOIN posts p ON ct.original_post_id = p.id
WHERE ct.avg_performance_score > 50
ORDER BY ct.viral_potential DESC;

-- Repost Candidates by Type
SELECT 
    rc.repost_type,
    COUNT(*) as candidate_count,
    AVG(rc.score) as avg_score,
    AVG(rc.predicted_views) as avg_predicted_views,
    SUM(CASE WHEN rc.is_used THEN 1 ELSE 0 END) as used_count
FROM repost_candidates rc
WHERE rc.created_at >= DATE('now', '-7 days')
GROUP BY rc.repost_type
ORDER BY avg_score DESC;
```

---

## 🗓️ **Implementierungs-Roadmap**

### **Phase 1: Core Schema + Migration (Woche 1-2)**

**Tag 1-2: Schema Setup**
- [ ] Create new database schema
- [ ] Set up indexes and constraints
- [ ] Create migration scripts
- [ ] Test schema with sample data

**Tag 3-5: Data Migration**
- [ ] Migrate existing 45k posts
- [ ] Migrate VA and account data
- [ ] Parse and migrate slide data
- [ ] Calculate performance indicators

**Tag 6-7: Validation & Testing**
- [ ] Validate data integrity
- [ ] Test performance with real queries
- [ ] Optimize indexes
- [ ] Create backup procedures

### **Phase 2: Time-Series + Slide Analytics (Woche 3-4)**

**Tag 8-10: Enhanced Scraping**
- [ ] Implement day 1-5 tracking
- [ ] Set up account snapshots
- [ ] Enhance slide processing
- [ ] Create automated scraping jobs

**Tag 11-14: Analytics Implementation**
- [ ] Build slide performance analytics
- [ ] Implement repost detection
- [ ] Create content template generation
- [ ] Set up VA performance tracking

### **Phase 3: Advanced Features (Woche 5-6)**

**Tag 15-17: VA Scoring & Management**
- [ ] Implement VA performance scoring
- [ ] Create VA ranking system
- [ ] Build improvement recommendations
- [ ] Set up automated reporting

**Tag 18-21: Revenue Attribution**
- [ ] Design revenue tracking schema
- [ ] Implement cost tracking
- [ ] Create ROI calculations
- [ ] Build financial dashboards

### **Phase 4: Optimierungen & Automation (Woche 7-8)**

**Tag 22-24: Performance Optimization**
- [ ] Implement materialized views
- [ ] Set up Redis caching
- [ ] Optimize slow queries
- [ ] Create monitoring dashboards

**Tag 25-28: Automation & Monitoring**
- [ ] Automate scraping pipeline
- [ ] Set up alert systems
- [ ] Create automated reports
- [ ] Implement data quality monitoring

---

## 🎯 **Success Metrics**

### **Performance Targets**
- ✅ **Query Speed**: <100ms für Dashboard-Queries
- ✅ **Data Volume**: Support für 100k+ Posts
- ✅ **Real-time Updates**: <5 Sekunden Lag
- ✅ **Analytics**: Komplexe Queries <2 Sekunden

### **Business KPIs**
- 📊 **Viral Rate**: % Posts >10k Views
- 📈 **Growth Rate**: Follower-Wachstum pro Account
- 🎯 **Content Quality**: Durchschnittlicher Performance Score
- 👥 **VA Performance**: Erfolgsrate pro VA

### **System KPIs**
- 🔄 **Data Freshness**: <24h für aktive Posts
- 📊 **Data Quality**: >99% Datenintegrität
- ⚡ **Uptime**: >99.9% System-Verfügbarkeit
- 🚀 **Scalability**: Linear skalierbar auf 1M+ Posts

---

## 🚀 **Next Steps**

1. **✅ Schema Review**: Finalize database schema
2. **🔧 Migration Scripts**: Create migration automation
3. **📊 Dashboard Development**: Build analytics interface
4. **🔄 Scraping Pipeline**: Implement enhanced data collection
5. **📈 Performance Monitoring**: Set up system monitoring
6. **🎯 Business Intelligence**: Create automated reports

**Die Architektur ist bereit für Implementation!** 🎯

---

*Generated: 2025-10-21*  
*Status: ✅ Architecture Decision Complete*  
*Next: Implementation Phase 1*
