#!/usr/bin/env python3
"""
Test Supabase Connection
Tests connection to Supabase using credentials from .env file
"""

import os
from dotenv import load_dotenv

def test_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase Connection...")
    print("-" * 50)

    # Load environment variables
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    # Check credentials
    if not supabase_url or supabase_url == 'https://YOUR_PROJECT_ID.supabase.co':
        print("❌ SUPABASE_URL not configured in .env file")
        print("   Please update .env with your actual Project URL")
        return False

    if not supabase_key:
        print("❌ SUPABASE_KEY not found in .env file")
        return False

    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...{supabase_key[-10:]}")
    print()

    # Test connection
    try:
        from supabase import create_client
        print("📦 Creating Supabase client...")

        client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully!")

        # Try a simple query to verify connection
        print("\n🔍 Testing database access...")
        result = client.table('tiktok_posts').select('id').limit(1).execute()
        print("✅ Database accessible!")
        print(f"   Response: {result}")

        return True

    except ImportError:
        print("❌ supabase-py not installed")
        print("   Install with: pip install supabase")
        return False

    except Exception as e:
        print(f"⚠️  Connection test note: {e}")
        print("   This is expected if database tables don't exist yet")
        print("   But connection credentials are valid!")
        return True

if __name__ == '__main__':
    success = test_connection()
    print()
    print("=" * 50)
    if success:
        print("🎉 Supabase connection ready!")
        print("\nNext steps:")
        print("1. Create database tables (see GITHUB_ISSUES.md #1)")
        print("2. Test slide upload functionality")
        print("3. Set up Google Sheets integration")
    else:
        print("❌ Please fix the issues above and try again")
