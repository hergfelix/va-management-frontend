"""
Slide Manager - Download TikTok carousel slides and upload to Supabase
Enables preview functionality for screenshot/copy workflow
"""

import asyncio
import aiohttp
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlideManager:
    """Manage TikTok carousel slide downloads and Supabase uploads"""

    def __init__(self,
                 supabase_url: Optional[str] = None,
                 supabase_key: Optional[str] = None,
                 local_cache_dir: str = "./slide_cache"):
        """
        Initialize slide manager

        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase anon key (or set SUPABASE_KEY env var)
            local_cache_dir: Local directory for caching downloaded slides
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        self.local_cache_dir = Path(local_cache_dir)
        self.local_cache_dir.mkdir(exist_ok=True)

        # Initialize Supabase client if credentials provided
        self.supabase_client = None
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized")
            except ImportError:
                logger.warning("⚠️ supabase-py not installed. Install with: pip install supabase")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Supabase: {e}")

    async def download_slide(self,
                            url: str,
                            post_id: str,
                            slide_number: int,
                            session: aiohttp.ClientSession) -> Optional[Path]:
        """
        Download a single slide image

        Args:
            url: TikTok slide image URL
            post_id: Unique post identifier (for organizing files)
            slide_number: Slide index (1-12)
            session: aiohttp session for download

        Returns:
            Path to downloaded file, or None if failed
        """
        try:
            # Generate filename: {post_id}_slide_{number}.jpg
            filename = f"{post_id}_slide_{slide_number}.jpg"
            filepath = self.local_cache_dir / filename

            # Check cache first
            if filepath.exists():
                logger.debug(f"✅ Cached: {filename}")
                return filepath

            # Download image
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()

                    # Save to local cache
                    with open(filepath, 'wb') as f:
                        f.write(content)

                    logger.info(f"📥 Downloaded: {filename} ({len(content):,} bytes)")
                    return filepath
                else:
                    logger.warning(f"❌ Failed download: {url} (status {response.status})")
                    return None

        except Exception as e:
            logger.error(f"❌ Error downloading {url}: {str(e)[:50]}")
            return None

    async def upload_to_supabase(self,
                                 local_path: Path,
                                 bucket: str = "tiktok-slides",
                                 public: bool = True) -> Optional[str]:
        """
        Upload slide to Supabase Storage

        Args:
            local_path: Path to local file
            bucket: Supabase storage bucket name
            public: Whether to make file publicly accessible

        Returns:
            Public URL of uploaded file, or None if failed
        """
        if not self.supabase_client:
            logger.warning("⚠️ Supabase not configured, skipping upload")
            return None

        try:
            # Read file content
            with open(local_path, 'rb') as f:
                file_content = f.read()

            # Upload to Supabase Storage
            storage_path = f"slides/{local_path.name}"

            response = self.supabase_client.storage.from_(bucket).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "image/jpeg", "upsert": "true"}
            )

            # Get public URL
            public_url = self.supabase_client.storage.from_(bucket).get_public_url(storage_path)

            logger.info(f"☁️ Uploaded: {local_path.name} → {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"❌ Upload failed for {local_path.name}: {str(e)[:100]}")
            return None

    async def process_post_slides(self,
                                  post_data: Dict,
                                  upload_to_cloud: bool = True) -> Dict:
        """
        Download and optionally upload all slides for a post

        Args:
            post_data: Dictionary with post_url, slide_count, slide_1..slide_12
            upload_to_cloud: Whether to upload to Supabase after download

        Returns:
            Dictionary with local_paths and cloud_urls for each slide
        """
        post_url = post_data.get('post_url', '')
        slide_count = int(post_data.get('slide_count', 0))

        if slide_count == 0:
            return {'slide_count': 0, 'local_paths': [], 'cloud_urls': []}

        # Generate post ID from URL
        post_id = self._generate_post_id(post_url)

        logger.info(f"🎬 Processing {slide_count} slides for post {post_id}")

        local_paths = []
        cloud_urls = []

        # Create download session
        async with aiohttp.ClientSession() as session:
            # Download all slides
            download_tasks = []
            for i in range(1, slide_count + 1):
                slide_key = f'slide_{i}'
                slide_url = post_data.get(slide_key, '')

                if slide_url:
                    task = self.download_slide(slide_url, post_id, i, session)
                    download_tasks.append(task)

            # Wait for all downloads
            downloaded_paths = await asyncio.gather(*download_tasks)
            local_paths = [p for p in downloaded_paths if p is not None]

        # Upload to Supabase if enabled
        if upload_to_cloud and self.supabase_client:
            upload_tasks = [self.upload_to_supabase(path) for path in local_paths]
            cloud_urls = await asyncio.gather(*upload_tasks)
            cloud_urls = [url for url in cloud_urls if url is not None]

        logger.info(f"✅ Processed {len(local_paths)} slides: {len(cloud_urls)} uploaded")

        return {
            'post_id': post_id,
            'post_url': post_url,
            'slide_count': len(local_paths),
            'local_paths': [str(p) for p in local_paths],
            'cloud_urls': cloud_urls
        }

    def generate_preview_html(self,
                              slide_data: Dict,
                              output_path: Optional[Path] = None) -> Path:
        """
        Generate HTML preview page for slides

        Args:
            slide_data: Result from process_post_slides()
            output_path: Where to save HTML (auto-generated if None)

        Returns:
            Path to generated HTML file
        """
        post_id = slide_data['post_id']
        post_url = slide_data['post_url']
        slide_count = slide_data['slide_count']

        # Use cloud URLs if available, otherwise local paths
        image_sources = slide_data.get('cloud_urls') or slide_data.get('local_paths', [])

        if not output_path:
            output_path = self.local_cache_dir / f"{post_id}_preview.html"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Slides Preview - {post_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #000;
            color: #fff;
            padding: 20px;
        }}

        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}

        .header {{
            margin-bottom: 20px;
            padding: 20px;
            background: #1a1a1a;
            border-radius: 12px;
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}

        .header .meta {{
            color: #888;
            font-size: 14px;
        }}

        .header a {{
            color: #fe2c55;
            text-decoration: none;
        }}

        .slides {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .slide {{
            background: #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }}

        .slide-number {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            z-index: 10;
        }}

        .slide img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .slide-actions {{
            padding: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
        }}

        .btn-primary {{
            background: #fe2c55;
            color: white;
        }}

        .btn-primary:hover {{
            background: #ff3d64;
        }}

        .btn-secondary {{
            background: #333;
            color: white;
        }}

        .btn-secondary:hover {{
            background: #444;
        }}

        .instructions {{
            margin-top: 30px;
            padding: 20px;
            background: #1a1a1a;
            border-radius: 12px;
        }}

        .instructions h2 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #fe2c55;
        }}

        .instructions ol {{
            margin-left: 20px;
            line-height: 1.8;
        }}

        .instructions code {{
            background: #000;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}

        @media (max-width: 640px) {{
            body {{
                padding: 10px;
            }}

            .header {{
                padding: 15px;
            }}

            .header h1 {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 TikTok Carousel Preview</h1>
            <div class="meta">
                Post ID: <code>{post_id}</code><br>
                Slides: {slide_count}<br>
                Original: <a href="{post_url}" target="_blank">Open TikTok</a>
            </div>
        </div>

        <div class="slides">
"""

        # Add each slide
        for i, img_src in enumerate(image_sources, 1):
            html_content += f"""
            <div class="slide">
                <div class="slide-number">Slide {i}/{slide_count}</div>
                <img src="{img_src}" alt="Slide {i}" id="slide-{i}">
                <div class="slide-actions">
                    <a href="{img_src}" download="slide_{i}.jpg" class="btn btn-primary">
                        💾 Download
                    </a>
                    <button class="btn btn-secondary" onclick="copyImage('{img_src}', {i})">
                        📋 Copy URL
                    </button>
                    <button class="btn btn-secondary" onclick="openInNew('{img_src}')">
                        🔗 Open Full
                    </button>
                </div>
            </div>
"""

        html_content += """
        </div>

        <div class="instructions">
            <h2>📖 How to Use This Preview</h2>
            <ol>
                <li><strong>Screenshot Slides</strong>: Use your system's screenshot tool:
                    <ul>
                        <li>Mac: <code>Cmd + Shift + 4</code> (select area)</li>
                        <li>Windows: <code>Win + Shift + S</code></li>
                    </ul>
                </li>
                <li><strong>Download Slides</strong>: Click "💾 Download" button on each slide</li>
                <li><strong>Copy URL</strong>: Click "📋 Copy URL" to get the image link</li>
                <li><strong>Open Full Size</strong>: Click "🔗 Open Full" to view in new tab</li>
            </ol>
        </div>
    </div>

    <script>
        function copyImage(url, slideNum) {
            navigator.clipboard.writeText(url).then(() => {
                alert(`✅ Slide ${slideNum} URL copied to clipboard!`);
            }).catch(err => {
                console.error('Failed to copy:', err);
                alert('❌ Failed to copy URL');
            });
        }

        function openInNew(url) {
            window.open(url, '_blank');
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + S to download first slide
            if ((e.metaKey || e.ctrlKey) && e.key === 's') {
                e.preventDefault();
                document.querySelector('.btn-primary').click();
            }
        });
    </script>
</body>
</html>
"""

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"📄 Preview generated: {output_path}")
        return output_path

    def _generate_post_id(self, post_url: str) -> str:
        """Generate unique post ID from URL"""
        # Extract video ID from TikTok URL
        # Example: https://www.tiktok.com/@user/video/1234567890 → 1234567890
        parts = post_url.rstrip('/').split('/')
        for part in reversed(parts):
            if part.isdigit():
                return part

        # Fallback: hash the URL
        return hashlib.md5(post_url.encode()).hexdigest()[:12]


async def main_test():
    """Test the slide manager with sample data"""
    print("=" * 80)
    print("🧪 TESTING SLIDE MANAGER")
    print("=" * 80)
    print()

    # Initialize manager
    manager = SlideManager()

    # Sample post data (you would get this from scraper)
    sample_post = {
        'post_url': 'https://www.tiktok.com/@example/video/7330716631651519786',
        'slide_count': 3,
        'slide_1': 'https://p16-sign.tiktokcdn-us.com/obj/example1.jpeg',
        'slide_2': 'https://p16-sign.tiktokcdn-us.com/obj/example2.jpeg',
        'slide_3': 'https://p16-sign.tiktokcdn-us.com/obj/example3.jpeg'
    }

    print("📥 Downloading slides...")
    result = await manager.process_post_slides(sample_post, upload_to_cloud=False)

    print()
    print("📊 Download Results:")
    print(f"   Post ID: {result['post_id']}")
    print(f"   Slides Downloaded: {result['slide_count']}")
    print(f"   Local Paths: {len(result['local_paths'])}")

    if result['slide_count'] > 0:
        print()
        print("📄 Generating HTML preview...")
        preview_path = manager.generate_preview_html(result)
        print(f"   ✅ Preview: {preview_path}")
        print()
        print(f"   🌐 Open in browser: file://{preview_path.absolute()}")

    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main_test())
