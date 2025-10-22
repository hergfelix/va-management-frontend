# 🗄️ TikTok Analytics Master Database

**Issue #1: Setup Master Database Schema** - ✅ **COMPLETED**

Complete SQLAlchemy-based database schema for TikTok VA analytics system with migration support, comprehensive testing, and data import utilities.

## 📋 **What's Included**

### ✅ **Core Components**
- **SQLAlchemy Models** - Complete ORM models for all tables
- **Alembic Migrations** - Database version control and migrations
- **Database Configuration** - Multi-database support (SQLite, PostgreSQL, Supabase)
- **Data Import Utilities** - CSV import with batch processing
- **Comprehensive Tests** - Full test suite for all models
- **Demo Script** - Working example of all functionality

### 📊 **Database Schema**

#### **Core Tables**
- **`vas`** - Virtual Assistants (creator, set_id, set_code)
- **`posts`** - Main TikTok posts with all metrics
- **`metrics_history`** - Time series metrics tracking
- **`slides`** - Individual slides with OCR text

#### **Analytics Tables**
- **`content_templates`** - Generated content variations
- **`repost_candidates`** - Posts identified for reposting
- **`scraping_jobs`** - Scraping job tracking
- **`system_config`** - System configuration
- **`data_import_log`** - Import process logging

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd "/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025"
source venv/bin/activate
pip install -r requirements_database.txt
```

### **2. Initialize Database**
```bash
# Create database and run migrations
alembic upgrade head

# Or use the demo script
python database/demo.py
```

### **3. Import Data**
```python
from database.config import get_db
from database.import_utils import import_master_database

# Import CSV data
db = next(get_db())
results = import_master_database("MASTER_TIKTOK_DATABASE.csv", db)
print(f"Imported {results['imported']} records")
```

### **4. Run Tests**
```bash
python -m pytest tests/test_models.py -v
```

## 📁 **File Structure**

```
database/
├── models.py              # SQLAlchemy models
├── config.py              # Database configuration
├── import_utils.py        # Data import/export utilities
├── demo.py                # Demo script
├── __init__.py            # Package initialization
└── README.md              # This file

migrations/
├── versions/              # Alembic migration files
│   └── 8ee8cb25046f_initial_database_schema.py
├── env.py                 # Alembic environment
└── script.py.mako         # Migration template

tests/
└── test_models.py         # Comprehensive model tests

alembic.ini                # Alembic configuration
requirements_database.txt  # Database dependencies
```

## 🔧 **Database Configuration**

### **Supported Databases**
- **SQLite** (default, for development)
- **PostgreSQL** (for production)
- **Supabase** (recommended for production)

### **Environment Variables**
```bash
# Database type
export DB_TYPE=sqlite  # or postgresql, supabase

# Database URLs
export DATABASE_URL=postgresql://user:pass@localhost/db
export SUPABASE_DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

## 📊 **Model Relationships**

```
VA (1) ──── (N) Post
Post (1) ──── (N) MetricsHistory
Post (1) ──── (N) Slide
Post (1) ──── (1) ContentTemplate
Post (1) ──── (1) RepostCandidate
VA (1) ──── (N) MetricsHistory
```

## 🧪 **Testing**

### **Run All Tests**
```bash
python -m pytest tests/test_models.py -v
```

### **Test Coverage**
- ✅ Model creation and validation
- ✅ Relationship integrity
- ✅ Constraint enforcement
- ✅ Data import/export
- ✅ Complex queries

## 📥 **Data Import**

### **Import CSV Data**
```python
from database.import_utils import DataImporter

importer = DataImporter(db_session)
results = importer.import_csv_data("MASTER_TIKTOK_DATABASE.csv")
```

### **Import Specific Data Types**
```python
# Import VA data
va_data = [{"name": "TestVA", "creator": "TestCreator"}]
importer.import_va_data(va_data)

# Import metrics history
metrics_data = [{"post_id": 1, "views": 1000, "likes": 50}]
importer.import_metrics_history(metrics_data)
```

## 📤 **Data Export**

### **Export Posts**
```python
from database.import_utils import DataExporter

exporter = DataExporter(db_session)
count = exporter.export_posts_to_csv("posts_export.csv")
```

### **Export VA Performance**
```python
count = exporter.export_va_performance("va_performance.csv")
```

## 🔄 **Migrations**

### **Create New Migration**
```bash
alembic revision --autogenerate -m "Add new field"
```

### **Apply Migrations**
```bash
alembic upgrade head
```

### **Rollback Migration**
```bash
alembic downgrade -1
```

## 📈 **Performance Features**

### **Indexes**
- Primary keys on all tables
- Foreign key indexes
- Composite indexes for common queries
- Text search indexes

### **Constraints**
- Unique constraints on URLs and names
- Check constraints for positive values
- Foreign key relationships
- Not null constraints where appropriate

## 🔒 **Security Features**

### **Data Validation**
- Input validation in models
- Constraint enforcement
- Type checking
- Relationship integrity

### **Access Control**
- Session-based access
- Transaction management
- Error handling and rollback

## 🚀 **Production Deployment**

### **Supabase Setup**
1. Create Supabase project
2. Get database URL
3. Set environment variables
4. Run migrations
5. Import data

### **PostgreSQL Setup**
1. Install PostgreSQL
2. Create database
3. Set DATABASE_URL
4. Run migrations
5. Import data

## 📊 **Database Statistics**

After importing the master database:
- **45,077 posts** from 263 accounts
- **49 VAs** tracked
- **92,367 slides** with OCR data
- **Multiple data sources** (old_clean, current_metrics, etc.)

## 🎯 **Next Steps**

1. **Issue #2**: Migrate existing data from Google Sheets
2. **Issue #3**: Build automated TikTok scraping system
3. **Issue #4**: Setup Supabase as database backend
4. **Issue #5**: Build VA Performance Dashboard

## 🐛 **Troubleshooting**

### **Common Issues**

**Migration Errors**
```bash
# Reset database
rm tiktok_analytics.db
alembic upgrade head
```

**Import Errors**
```bash
# Check CSV format
python -c "import pandas as pd; print(pd.read_csv('MASTER_TIKTOK_DATABASE.csv', nrows=5))"
```

**Test Failures**
```bash
# Run with verbose output
python -m pytest tests/test_models.py -v -s
```

## 📞 **Support**

For issues or questions:
1. Check the test suite for examples
2. Review the demo script
3. Check Alembic migration files
4. Verify database configuration

---

**✅ Issue #1 Status: COMPLETED**

All requirements have been implemented:
- ✅ Master post database with all metrics
- ✅ Support for slides (R2 URLs)
- ✅ Track VA information (creator, set_id, set_code)
- ✅ Metrics tracking (views, likes, comments, shares, engagement rate)
- ✅ Scraping status tracking
- ✅ SQLAlchemy models with relationships
- ✅ Alembic migrations
- ✅ Comprehensive tests
- ✅ Data import utilities
