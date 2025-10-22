#!/usr/bin/env python3
"""
Process Slides from CSV - Extract slides from scraper output and generate previews
Works with existing comprehensive_scraper.py output files
"""

import asyncio
import csv
import sys
from pathlib import Path
from typing import List, Dict
from slide_manager import SlideManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlideProcessor:
    """Process slides from CSV files"""

    def __init__(self, csv_path: str, upload_to_supabase: bool = False):
        """
        Initialize processor

        Args:
            csv_path: Path to comprehensive scraper CSV output
            upload_to_supabase: Whether to upload slides to Supabase
        """
        self.csv_path = Path(csv_path)
        self.upload_to_supabase = upload_to_supabase
        self.manager = SlideManager()

    def load_posts_with_slides(self) -> List[Dict]:
        """Load posts that have carousel slides from CSV"""
        posts = []

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Check if post has slides
                slide_count = int(row.get('slide_count', 0))

                if slide_count > 0:
                    posts.append(row)

        logger.info(f"📊 Found {len(posts)} posts with carousel slides")
        return posts

    async def process_all_slides(self) -> Dict:
        """Download and process slides for all carousel posts"""
        posts = self.load_posts_with_slides()

        if not posts:
            logger.warning("⚠️ No carousel posts found in CSV")
            return {'processed': 0, 'previews': []}

        logger.info(f"🚀 Processing slides from {len(posts)} carousel posts...")
        print()

        results = []
        preview_files = []

        for i, post in enumerate(posts, 1):
            post_url = post.get('post_url', '')
            slide_count = post.get('slide_count', 0)

            logger.info(f"[{i}/{len(posts)}] Processing {post_url} ({slide_count} slides)")

            # Download slides
            slide_data = await self.manager.process_post_slides(
                post,
                upload_to_cloud=self.upload_to_supabase
            )

            results.append(slide_data)

            # Generate preview HTML
            if slide_data['slide_count'] > 0:
                preview_path = self.manager.generate_preview_html(slide_data)
                preview_files.append(preview_path)

            # Rate limiting
            if i < len(posts):
                await asyncio.sleep(1)

        return {
            'processed': len(results),
            'previews': preview_files,
            'results': results
        }

    def generate_index_html(self, preview_files: List[Path]) -> Path:
        """Generate index page with links to all previews"""
        index_path = self.manager.local_cache_dir / "index.html"

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Carousel Slides - Index</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #000;
            color: #fff;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            margin-bottom: 30px;
            padding: 30px;
            background: #1a1a1a;
            border-radius: 12px;
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header .stats {
            color: #888;
            font-size: 16px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .card {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(254, 44, 85, 0.3);
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #fe2c55;
        }

        .card-info {
            color: #888;
            font-size: 14px;
            margin-bottom: 15px;
        }

        .card-actions {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s;
            display: inline-block;
        }

        .btn-primary {
            background: #fe2c55;
            color: white;
        }

        .btn-primary:hover {
            background: #ff3d64;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 TikTok Carousel Slides</h1>
            <div class="stats">
                Total Posts: """ + str(len(preview_files)) + """<br>
                Generated: """ + str(Path.cwd()) + """
            </div>
        </div>

        <div class="grid">
"""

        for preview_path in preview_files:
            post_id = preview_path.stem.replace('_preview', '')
            html += f"""
            <div class="card">
                <div class="card-title">Post {post_id}</div>
                <div class="card-info">
                    Preview available
                </div>
                <div class="card-actions">
                    <a href="{preview_path.name}" class="btn btn-primary">
                        👁️ View Slides
                    </a>
                </div>
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"📄 Index generated: {index_path}")
        return index_path


async def main():
    """Main entry point"""
    print("=" * 80)
    print("📸 SLIDE PROCESSOR - Extract and Preview TikTok Carousel Slides")
    print("=" * 80)
    print()

    # Check for CSV file argument
    if len(sys.argv) < 2:
        print("Usage: python3 process_slides_from_csv.py <csv_file> [--upload]")
        print()
        print("Example:")
        print("  python3 process_slides_from_csv.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv")
        print("  python3 process_slides_from_csv.py data.csv --upload  # Upload to Supabase")
        print()
        sys.exit(1)

    csv_file = sys.argv[1]
    upload_flag = '--upload' in sys.argv

    if not Path(csv_file).exists():
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)

    print(f"📂 Processing: {csv_file}")
    print(f"☁️ Upload to Supabase: {'Yes' if upload_flag else 'No'}")
    print()

    # Initialize processor
    processor = SlideProcessor(csv_file, upload_to_supabase=upload_flag)

    # Process all slides
    print("🚀 Starting slide processing...")
    print("=" * 80)
    print()

    result = await processor.process_all_slides()

    # Generate index page
    if result['previews']:
        index_path = processor.generate_index_html(result['previews'])

    # Summary
    print()
    print("=" * 80)
    print("✅ PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Carousel posts processed: {result['processed']}")
    print(f"Preview pages generated: {len(result['previews'])}")
    print()

    if result['previews']:
        print("📄 Preview Files:")
        for preview in result['previews'][:5]:  # Show first 5
            print(f"   • {preview.name}")
        if len(result['previews']) > 5:
            print(f"   ... and {len(result['previews']) - 5} more")

        print()
        print(f"🌐 Open index: file://{index_path.absolute()}")

    print()
    print("💡 Tip: Open the index.html file in your browser to view all slide previews")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
