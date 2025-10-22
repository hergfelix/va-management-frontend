# GitHub Issues for Production Implementation

Create these issues in your GitHub repository to delegate to specialist agents.

---

## Issue #1: Setup Supabase Database Schema

**Title**: `[PROD][Backend] Setup Supabase Database Schema for TikTok Analytics`

**Labels**: `production`, `backend`, `database`, `priority:high`

**Assignee**: `@backend-architect`

**Description**:

### 🎯 Objective
Create production-ready Supabase database schema with all tables, indexes, policies, and functions for TikTok analytics system.

### 📊 Current State
- Schema documented in `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`
- Tables designed: `tiktok_posts`, `tiktok_slides`, `scraping_logs`
- No database created yet

### ✅ Production Requirements
- [x] Schema documented
- [ ] Database migrations created
- [ ] RLS policies implemented
- [ ] Indexes optimized
- [ ] Foreign key constraints
- [ ] Triggers for audit trail
- [ ] Backup strategy
- [ ] Performance testing

### 🔧 Technical Specifications

**Tables to Create**:
1. `tiktok_posts` (46 columns)
2. `tiktok_slides` (slide metadata)
3. `scraping_logs` (audit trail)

**Storage**:
- Bucket: `tiktok-slides`
- Public read access
- Authenticated upload only

**SQL Files to Create**:
```
database/migrations/
├── 001_create_tiktok_posts.sql
├── 002_create_tiktok_slides.sql
├── 003_create_scraping_logs.sql
├── 004_create_indexes.sql
├── 005_create_rls_policies.sql
└── 006_create_storage_bucket.sql
```

### 🧪 Testing Checklist
- [ ] Can insert test post record
- [ ] Can insert slide records
- [ ] Can query by all indexed fields
- [ ] RLS policies work correctly
- [ ] Foreign key constraints enforced
- [ ] Storage upload works
- [ ] Public URLs accessible

### 📚 Documentation Required
- [ ] Migration guide
- [ ] Schema diagram
- [ ] API usage examples
- [ ] Backup/restore procedures

### 🚀 Deployment Steps
1. Create Supabase project
2. Run migrations in order
3. Setup storage bucket
4. Configure policies
5. Test with sample data
6. Document connection details

### ⚠️ Risks & Mitigation
- **Risk**: Data loss during migration
  - **Mitigation**: Test on staging first, create backups
- **Risk**: Performance issues with large datasets
  - **Mitigation**: Proper indexing, query optimization
- **Risk**: Security vulnerabilities
  - **Mitigation**: RLS policies, input validation

### 📌 Acceptance Criteria
- [ ] All tables created successfully
- [ ] Sample data can be inserted
- [ ] Queries perform well (< 100ms for indexed fields)
- [ ] RLS policies tested and working
- [ ] Storage bucket accessible
- [ ] Documentation complete

**Related Files**: `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`

---

## Issue #2: Implement Google Sheets Integration

**Title**: `[PROD][Backend] Implement Google Sheets API Integration for Data Entry`

**Labels**: `production`, `backend`, `integration`, `priority:high`

**Assignee**: `@backend-architect`

**Description**:

### 🎯 Objective
Build production-ready Google Sheets integration to read TikTok URLs and update scraping status.

### 📊 Current State
- Code documented in `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`
- `google_sheets_reader.py` planned but not implemented
- No authentication setup

### ✅ Production Requirements
- [ ] Service account authentication
- [ ] Rate limiting (60 requests/min)
- [ ] Error handling and retries
- [ ] Logging
- [ ] Configuration management
- [ ] Input validation
- [ ] Status tracking
- [ ] Concurrent access handling

### 🔧 Technical Specifications

**File**: `02_Scraping_Systems/01_TikTok_Scrapers/google_sheets_reader.py`

**Features**:
- Read rows with status "Ready to Scrape"
- Extract: post_url, creator, set_id, va, type
- Update status to "Scraped" after processing
- Handle sheet changes during processing
- Batch operations for efficiency

**Dependencies**:
```
gspread>=5.12.0
oauth2client>=4.1.3
google-auth>=2.23.0
```

**Configuration**:
```env
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
GOOGLE_SHEET_URL=https://docs.google.com/...
```

### 🧪 Testing Checklist
- [ ] Can authenticate with service account
- [ ] Can read test sheet data
- [ ] Can update status correctly
- [ ] Handles missing/invalid data gracefully
- [ ] Rate limiting works
- [ ] Concurrent updates don't conflict
- [ ] Retries on transient failures

### 📚 Documentation Required
- [ ] Setup guide for service account
- [ ] Sheet structure requirements
- [ ] API usage examples
- [ ] Troubleshooting guide

### 🚀 Deployment Steps
1. Create GCP project
2. Enable Sheets API
3. Create service account
4. Share sheet with service account
5. Download credentials JSON
6. Configure environment variables
7. Test read/write operations

### ⚠️ Risks & Mitigation
- **Risk**: API quota exceeded
  - **Mitigation**: Rate limiting, caching, batch operations
- **Risk**: Concurrent edits cause conflicts
  - **Mitigation**: Optimistic locking, retry logic
- **Risk**: Credentials leak
  - **Mitigation**: .env files, .gitignore, secrets management

### 📌 Acceptance Criteria
- [ ] Can read 100+ URLs without errors
- [ ] Status updates reflected in sheet
- [ ] Handles API errors gracefully
- [ ] Logs all operations
- [ ] Configuration documented
- [ ] Tests pass

**Related Files**: `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`

---

## Issue #3: Implement Supabase Writer Module

**Title**: `[PROD][Backend] Implement Supabase Writer for Data Persistence`

**Labels**: `production`, `backend`, `database`, `priority:high`

**Assignee**: `@backend-architect`

**Description**:

### 🎯 Objective
Build production-ready Supabase writer to persist scraped data and slides.

### 📊 Current State
- Code structure documented in `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`
- `supabase_writer.py` planned but not implemented
- Database schema ready (Issue #1)

### ✅ Production Requirements
- [ ] Connection pooling
- [ ] Transaction support
- [ ] Upsert logic (handle duplicates)
- [ ] Error handling and retries
- [ ] Logging
- [ ] Performance optimization
- [ ] Input validation
- [ ] Audit trail

### 🔧 Technical Specifications

**File**: `02_Scraping_Systems/01_TikTok_Scrapers/supabase_writer.py`

**Features**:
- `insert_post()` - Upsert post data
- `insert_slides()` - Batch insert slide metadata
- `log_scraping_batch()` - Audit trail
- Connection management
- Error recovery

**Dependencies**:
```
supabase>=2.0.0
```

**Configuration**:
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
```

### 🧪 Testing Checklist
- [ ] Can insert test post
- [ ] Upsert handles duplicates correctly
- [ ] Batch insert slides works
- [ ] Foreign key constraints enforced
- [ ] Transactions rollback on error
- [ ] Logging captures all operations
- [ ] Performance acceptable (>100 posts/min)

### 📚 Documentation Required
- [ ] API reference
- [ ] Usage examples
- [ ] Error handling guide
- [ ] Performance tuning tips

### 🚀 Deployment Steps
1. Install supabase-py
2. Configure environment variables
3. Test connection
4. Run integration tests
5. Document any issues

### ⚠️ Risks & Mitigation
- **Risk**: Data duplication
  - **Mitigation**: Upsert logic, unique constraints
- **Risk**: Performance degradation
  - **Mitigation**: Batch operations, connection pooling
- **Risk**: Connection failures
  - **Mitigation**: Retry logic, exponential backoff

### 📌 Acceptance Criteria
- [ ] Can write 1000+ posts without errors
- [ ] Duplicate handling works correctly
- [ ] All errors logged appropriately
- [ ] Performance meets requirements
- [ ] Tests pass
- [ ] Documentation complete

**Related Files**: `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`, Issue #1

---

## Issue #4: Production-Ready Slide Management System

**Title**: `[PROD][Backend] Productionize Slide Download/Upload System`

**Labels**: `production`, `backend`, `storage`, `priority:medium`

**Assignee**: `@backend-architect` + `@performance-engineer`

**Description**:

### 🎯 Objective
Make `slide_manager.py` production-ready with robust error handling, monitoring, and performance optimization.

### 📊 Current State
- `slide_manager.py` implemented (prototype)
- Basic download/upload working
- No production-grade error handling
- No monitoring/metrics

### ✅ Production Requirements
- [ ] Retry logic for failed downloads
- [ ] Resume interrupted downloads
- [ ] Progress tracking
- [ ] Metrics/monitoring
- [ ] Rate limiting
- [ ] Memory optimization
- [ ] Concurrent download limits
- [ ] Disk space management
- [ ] CDN URL expiration handling

### 🔧 Technical Specifications

**Enhancements Needed**:

1. **Retry Logic**:
```python
@retry(max_attempts=3, backoff=exponential)
async def download_slide(...):
    # Implementation
```

2. **Progress Tracking**:
```python
from tqdm import tqdm
# Add progress bars for downloads
```

3. **Metrics**:
```python
class SlideMetrics:
    downloads_successful: int
    downloads_failed: int
    bytes_downloaded: int
    avg_download_time: float
```

4. **Concurrency Control**:
```python
MAX_CONCURRENT_DOWNLOADS = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
```

### 🧪 Testing Checklist
- [ ] Handles network failures gracefully
- [ ] Resumes interrupted downloads
- [ ] CDN URL expiration detected
- [ ] Memory usage acceptable (<500MB)
- [ ] Concurrent downloads work
- [ ] Metrics accurate
- [ ] Progress bars update correctly

### 📚 Documentation Required
- [ ] Error codes and recovery
- [ ] Performance tuning guide
- [ ] Monitoring setup
- [ ] Troubleshooting guide

### 🚀 Deployment Steps
1. Update `slide_manager.py`
2. Add dependencies (tqdm, retry, etc.)
3. Configure limits (concurrency, rate)
4. Setup monitoring
5. Test with 100+ carousels

### ⚠️ Risks & Mitigation
- **Risk**: Memory exhaustion with large batches
  - **Mitigation**: Streaming downloads, limits
- **Risk**: CDN blocks/rate limits
  - **Mitigation**: Delays, exponential backoff
- **Risk**: Disk space full
  - **Mitigation**: Space checks, cleanup

### 📌 Acceptance Criteria
- [ ] Can process 1000+ slides without errors
- [ ] Recovers from network failures
- [ ] Memory usage stable
- [ ] Metrics collected
- [ ] Documentation complete
- [ ] Tests pass

**Related Files**: `slide_manager.py`, `SLIDE_MANAGEMENT_SYSTEM.md`

---

## Issue #5: Build Integrated Scraper Pipeline

**Title**: `[PROD][System] Build Production Integrated Scraper Pipeline`

**Labels**: `production`, `integration`, `orchestration`, `priority:critical`

**Assignee**: `@system-architect` + `@devops-architect`

**Description**:

### 🎯 Objective
Implement complete end-to-end pipeline: Google Sheets → Scraper → Supabase with monitoring and error recovery.

### 📊 Current State
- Architecture documented in `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`
- `integrated_scraper.py` planned but not implemented
- Components exist separately (Issues #1-4)

### ✅ Production Requirements
- [ ] Error recovery and rollback
- [ ] Transaction management
- [ ] Idempotency (safe to re-run)
- [ ] Monitoring and alerting
- [ ] Logging aggregation
- [ ] Health checks
- [ ] Graceful shutdown
- [ ] Configuration management
- [ ] Deployment automation

### 🔧 Technical Specifications

**File**: `02_Scraping_Systems/01_TikTok_Scrapers/integrated_scraper.py`

**Pipeline Stages**:
1. **Initialize** - Load config, connect to services
2. **Fetch** - Read from Google Sheets
3. **Scrape** - Scrape TikTok data
4. **Process** - Download/upload slides
5. **Persist** - Write to Supabase
6. **Update** - Mark as scraped in sheet
7. **Log** - Record batch results

**Error Handling**:
- Checkpoint progress (resume capability)
- Retry failed operations
- Rollback on critical errors
- Alert on failures

**Monitoring**:
```python
metrics = {
    'batch_id': uuid,
    'duration_seconds': int,
    'urls_processed': int,
    'success_rate': float,
    'errors': List[str]
}
```

### 🧪 Testing Checklist
- [ ] End-to-end test with 10 URLs
- [ ] Handles partial failures gracefully
- [ ] Resume from checkpoint works
- [ ] All stages log correctly
- [ ] Metrics accurate
- [ ] Health check responds
- [ ] Graceful shutdown works

### 📚 Documentation Required
- [ ] Deployment guide
- [ ] Configuration reference
- [ ] Monitoring setup
- [ ] Troubleshooting runbook
- [ ] API documentation

### 🚀 Deployment Steps
1. Install all dependencies
2. Configure all services (Sheets, Supabase)
3. Setup environment variables
4. Run integration tests
5. Deploy to production
6. Setup monitoring
7. Configure alerts

### ⚠️ Risks & Mitigation
- **Risk**: Cascading failures across services
  - **Mitigation**: Circuit breakers, timeouts
- **Risk**: Data inconsistency between services
  - **Mitigation**: Transaction boundaries, rollback
- **Risk**: Silent failures
  - **Mitigation**: Comprehensive logging, monitoring

### 📌 Acceptance Criteria
- [ ] Can process 100+ URLs end-to-end
- [ ] <5% failure rate acceptable
- [ ] All failures logged and alerted
- [ ] Resume from checkpoint works
- [ ] Performance meets SLA
- [ ] Documentation complete
- [ ] Deployment automated

**Related Files**: All previous issues, `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`

---

## Issue #6: Setup Automation & Scheduling

**Title**: `[PROD][DevOps] Setup Automated Scheduling for Scraper Pipeline`

**Labels**: `production`, `devops`, `automation`, `priority:medium`

**Assignee**: `@devops-architect`

**Description**:

### 🎯 Objective
Deploy automated scheduling for the integrated scraper pipeline with monitoring and alerting.

### 📊 Current State
- Automation options documented in `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`
- No automation deployed
- Manual execution only

### ✅ Production Requirements
- [ ] Cron job or scheduled trigger
- [ ] Failure notifications
- [ ] Logging to centralized system
- [ ] Resource limits
- [ ] Automatic retries
- [ ] Manual trigger capability
- [ ] Status dashboard
- [ ] Cost monitoring

### 🔧 Technical Specifications

**Options**:
1. **Cron Job** (Linux/Mac server)
2. **GitHub Actions** (CI/CD)
3. **Cloud Functions** (Serverless)

**Recommended**: GitHub Actions

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
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
        run: python3 integrated_scraper.py
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scraper-logs
          path: logs/
```

### 🧪 Testing Checklist
- [ ] Manual trigger works
- [ ] Scheduled run executes
- [ ] Secrets loaded correctly
- [ ] Logs captured
- [ ] Failures trigger alerts
- [ ] Resource limits enforced
- [ ] Artifacts uploaded

### 📚 Documentation Required
- [ ] Deployment guide
- [ ] Manual trigger instructions
- [ ] Log access guide
- [ ] Alert configuration

### 🚀 Deployment Steps
1. Choose automation platform
2. Configure secrets
3. Deploy workflow/cron
4. Test manual trigger
5. Wait for scheduled run
6. Verify logs and alerts
7. Document process

### ⚠️ Risks & Mitigation
- **Risk**: Missed scheduled runs
  - **Mitigation**: Monitoring, alerts
- **Risk**: Secrets exposure
  - **Mitigation**: Encrypted secrets, rotation
- **Risk**: Resource exhaustion
  - **Mitigation**: Timeouts, limits

### 📌 Acceptance Criteria
- [ ] Scheduled runs execute successfully
- [ ] Manual trigger works
- [ ] All logs accessible
- [ ] Alerts configured
- [ ] Documentation complete
- [ ] Cost acceptable (<$10/month)

**Related Files**: `GOOGLE_SHEETS_TO_SUPABASE_WORKFLOW.md`, Issue #5

---

## Issue #7: Build Analytics Dashboard (Future)

**Title**: `[FUTURE][Frontend] Build Analytics Dashboard on Supabase Data`

**Labels**: `enhancement`, `frontend`, `dashboard`, `priority:low`

**Assignee**: `@frontend-architect`

**Description**:

### 🎯 Objective
Build web dashboard to visualize TikTok analytics data from Supabase.

### 📊 Current State
- Data in Supabase ready for visualization
- No dashboard exists
- Future enhancement

### ✅ Requirements
- [ ] Performance metrics by VA/Creator
- [ ] Slide galleries
- [ ] Trend analysis
- [ ] Export functionality
- [ ] Responsive design
- [ ] Authentication

### 🔧 Technical Stack
- **Frontend**: Next.js + React
- **UI**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts or Chart.js
- **Database**: Supabase (existing)
- **Auth**: Supabase Auth

### 📌 Acceptance Criteria
- [ ] Can view all posts with metrics
- [ ] Can filter by VA/Creator
- [ ] Can view slide galleries
- [ ] Charts load quickly (<2s)
- [ ] Mobile responsive
- [ ] Authenticated access

**Related Files**: Supabase database from Issue #1

---

## 📋 Issue Creation Priority

**Critical Path** (Do First):
1. ✅ Issue #1: Setup Supabase Database Schema
2. ✅ Issue #2: Implement Google Sheets Integration
3. ✅ Issue #3: Implement Supabase Writer Module
4. ✅ Issue #5: Build Integrated Scraper Pipeline

**High Priority** (Do Next):
5. ✅ Issue #4: Production-Ready Slide Management
6. ✅ Issue #6: Setup Automation & Scheduling

**Future Enhancements**:
7. ⏳ Issue #7: Build Analytics Dashboard

---

## 🚀 How to Create Issues

### Using GitHub CLI:
```bash
# Create all issues at once
gh issue create --title "[PROD][Backend] Setup Supabase Database Schema" \
  --body-file issue_01_supabase_schema.md \
  --label "production,backend,database,priority:high"

gh issue create --title "[PROD][Backend] Implement Google Sheets Integration" \
  --body-file issue_02_google_sheets.md \
  --label "production,backend,integration,priority:high"

# ... repeat for all issues
```

### Using GitHub Web Interface:
1. Go to repository → Issues → New issue
2. Copy/paste issue content from this file
3. Add appropriate labels
4. Assign to specialist agent (or leave unassigned)
5. Create issue

---

## 📊 Agent Assignment Guide

| Issue | Primary Agent | Support Agent |
|-------|--------------|---------------|
| #1 | @backend-architect | @security-engineer |
| #2 | @backend-architect | @system-architect |
| #3 | @backend-architect | @performance-engineer |
| #4 | @backend-architect | @performance-engineer |
| #5 | @system-architect | @devops-architect |
| #6 | @devops-architect | @system-architect |
| #7 | @frontend-architect | @backend-architect |

---

## ✅ Verification Checklist

After all issues completed:
- [ ] Supabase database fully operational
- [ ] Google Sheets integration working
- [ ] Slides downloading and uploading
- [ ] End-to-end pipeline functional
- [ ] Automation deployed and tested
- [ ] All documentation updated
- [ ] Production monitoring active
- [ ] Team trained on system

---

**Next Action**: Create these issues in GitHub and assign to specialist agents for implementation.
