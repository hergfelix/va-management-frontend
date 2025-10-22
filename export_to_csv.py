#!/usr/bin/env python3
"""
Export SQLite database to CSV files
Makes it easy to view data in Excel/Google Sheets
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime

def export_table_to_csv(db_path: str, table_name: str, output_dir: str = "./exports"):
    """Export a single table to CSV"""

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    # Get all data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print(f"⚠️  {table_name}: No data to export")
        return None

    # Get column names
    columns = rows[0].keys()

    # Write to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = output_path / f"{table_name}_{timestamp}.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for row in rows:
            writer.writerow(dict(row))

    conn.close()

    row_count = len(rows)
    print(f"✅ {table_name}: Exported {row_count:,} rows → {csv_file}")
    return csv_file

def export_all_tables(db_path: str = "./tiktok_analytics.db", output_dir: str = "./exports"):
    """Export all tables to CSV files"""

    print("=" * 60)
    print("📊 Exporting SQLite Database to CSV")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Output: {output_dir}/")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Filter out system tables
    user_tables = [t for t in tables if not t.startswith('sqlite_') and not t.startswith('alembic_')]

    conn.close()

    print(f"Found {len(user_tables)} tables to export:\n")

    exported_files = []

    for table in user_tables:
        csv_file = export_table_to_csv(db_path, table, output_dir)
        if csv_file:
            exported_files.append(csv_file)

    print()
    print("=" * 60)
    print(f"🎉 Export Complete! {len(exported_files)} files created")
    print("=" * 60)
    print(f"\n📁 Files saved to: {Path(output_dir).absolute()}")
    print("\n💡 To view:")
    print(f"   - Open in Excel/Numbers: open {output_dir}/")
    print(f"   - Import to Google Sheets")
    print(f"   - Open with any spreadsheet app")

    return exported_files

def export_custom_query(db_path: str, query: str, output_file: str):
    """Export results of a custom SQL query to CSV"""

    print(f"🔍 Running custom query...")
    print(f"Query: {query[:100]}...")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("⚠️  Query returned no results")
        return None

    columns = rows[0].keys()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for row in rows:
            writer.writerow(dict(row))

    conn.close()

    print(f"✅ Exported {len(rows):,} rows → {output_file}")
    return output_file

def show_preview(db_path: str = "./tiktok_analytics.db"):
    """Show a preview of database contents"""

    print("=" * 60)
    print("👀 Database Preview")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table stats
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    user_tables = [t for t in tables if not t.startswith('sqlite_') and not t.startswith('alembic_')]

    print(f"\n📊 Database: {db_path}")
    print(f"\n📋 Tables ({len(user_tables)}):\n")

    for table in user_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   - {table}: {count:,} rows")

    # Show sample posts
    print("\n📌 Sample Posts (First 5):\n")
    cursor.execute("""
    SELECT account, views, likes, post_url
    FROM posts
    ORDER BY views DESC
    LIMIT 5
    """)

    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"   {i}. {row[0]} - {row[1]:,} views, {row[2]:,} likes")
        print(f"      {row[3]}")

    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys

    # Show preview first
    show_preview()

    print()
    input("Press Enter to export all tables to CSV... ")

    # Export all tables
    export_all_tables()

    # Example: Export custom query
    print("\n💡 Example: Custom query export")
    print("   You can also export specific data with custom queries")

    # Uncomment to export top posts:
    # export_custom_query(
    #     "./tiktok_analytics.db",
    #     "SELECT * FROM posts WHERE views > 10000 ORDER BY views DESC",
    #     "./exports/top_posts.csv"
    # )
