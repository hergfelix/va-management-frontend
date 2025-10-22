"""
Google Sheets Integration for Professional Follower Tracking
Creates data in the exact format of your TikTok Tracking Sheet
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsIntegration:
    """
    Google Sheets integration for follower tracking
    """
    
    def __init__(self):
        self.accounts_data = None
        self.va_mapping = {
            'CARLA': 'CARLA',
            'JAROLD': 'JAROLD', 
            'AARON': 'AARON',
            'JOSUHA': 'JOSUHA',
            'GRASHANG': 'GRASHANG',
            'JAIRIS': 'JAIRIS',
            'SAMUEL': 'SAMUEL',
            'LIYA': 'LIYA',
            'UNKNOWN': 'UNKNOWN'
        }
    
    def load_accounts(self, csv_file='miriam_accounts_clean.csv'):
        """
        Load accounts from CSV file
        """
        if os.path.exists(csv_file):
            self.accounts_data = pd.read_csv(csv_file)
            logger.info(f"✅ Loaded {len(self.accounts_data)} accounts from {csv_file}")
            return True
        else:
            logger.error(f"❌ Accounts file not found: {csv_file}")
            return False
    
    def create_tracking_sheet_format(self):
        """
        Create data in the exact format of your TikTok Tracking Sheet
        """
        if self.accounts_data is None:
            return None
        
        # Create the sheet structure similar to your original
        sheet_data = []
        
        # Header rows (similar to your original sheet)
        sheet_data.append(['Color', '0-19', '20-49', '50-99', '100-199', '200-499', '500+'] + [''] * 100)
        sheet_data.append([''] * 110)  # Empty row
        sheet_data.append(['Model', 'MIRIAM'] + [''] * 108)
        
        # VA row - distribute accounts across VAs
        va_row = ['Worker']
        va_accounts = {}
        
        # Group accounts by VA
        for _, account in self.accounts_data.iterrows():
            va = account['va_name']
            if va not in va_accounts:
                va_accounts[va] = []
            va_accounts[va].append(account)
        
        # Create VA distribution (similar to your original)
        va_order = ['CARLA', 'JAROLD', 'AARON', 'JOSUHA', 'GRASHANG', 'JAIRIS', 'SAMUEL', 'LIYA']
        
        for va in va_order:
            if va in va_accounts:
                va_row.append(va)
                # Add empty cells for spacing
                for _ in range(len(va_accounts[va]) - 1):
                    va_row.append('')
            else:
                va_row.append('')
        
        # Fill remaining cells
        while len(va_row) < 110:
            va_row.append('')
        
        sheet_data.append(va_row)
        
        # Profile picture row
        sheet_data.append(['Tiktok\nProfile picture'] + [''] * 109)
        
        # Account names row
        account_row = ['Account name']
        for _, account in self.accounts_data.iterrows():
            account_row.append(account['username'])
        
        # Fill remaining cells
        while len(account_row) < 110:
            account_row.append('')
        
        sheet_data.append(account_row)
        
        # Follower count row
        follower_row = ['Follower']
        for _, account in self.accounts_data.iterrows():
            follower_row.append(str(account['current_followers']))
        
        # Fill remaining cells
        while len(follower_row) < 110:
            follower_row.append('')
        
        sheet_data.append(follower_row)
        
        # Biography row (placeholder)
        bio_row = ['Tiktok\nBiography']
        for _, account in self.accounts_data.iterrows():
            bio_row.append(f"Bio for @{account['username']}")
        
        # Fill remaining cells
        while len(bio_row) < 110:
            bio_row.append('')
        
        sheet_data.append(bio_row)
        
        # Link row (placeholder)
        link_row = ['LINK']
        for _, account in self.accounts_data.iterrows():
            link_row.append(f"linktr.ee/{account['username']}")
        
        # Fill remaining cells
        while len(link_row) < 110:
            link_row.append('')
        
        sheet_data.append(link_row)
        
        # Social Media row
        social_row = ['Social Media']
        for _, account in self.accounts_data.iterrows():
            social_row.append('Tiktok')
        
        # Fill remaining cells
        while len(social_row) < 110:
            social_row.append('')
        
        sheet_data.append(social_row)
        
        # Date rows (last 30 days)
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            date_row = [date.strftime('%d.%m.%Y')] + [''] * 109
            sheet_data.append(date_row)
        
        return sheet_data
    
    def create_modern_tracking_sheet(self):
        """
        Create a modern, clean version of the tracking sheet
        """
        if self.accounts_data is None:
            return None
        
        # Create modern sheet structure
        sheet_data = []
        
        # Modern header
        sheet_data.append(['🎯 TikTok Follower Tracking Dashboard'])
        sheet_data.append(['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')])
        sheet_data.append([''])  # Empty row
        
        # Summary statistics
        total_followers = self.accounts_data['current_followers'].sum()
        avg_followers = self.accounts_data['current_followers'].mean()
        accounts_over_10k = len(self.accounts_data[self.accounts_data['current_followers'] >= 10000])
        
        sheet_data.append(['📊 SUMMARY STATISTICS'])
        sheet_data.append(['Total Accounts:', len(self.accounts_data)])
        sheet_data.append(['Total Followers:', f"{total_followers:,}"])
        sheet_data.append(['Average Followers:', f"{avg_followers:,.0f}"])
        sheet_data.append(['Accounts Over 10K:', accounts_over_10k])
        sheet_data.append([''])  # Empty row
        
        # VA Performance
        sheet_data.append(['👥 VA PERFORMANCE'])
        va_stats = self.accounts_data.groupby('va_name').agg({
            'username': 'count',
            'current_followers': 'sum'
        }).sort_values('current_followers', ascending=False)
        
        sheet_data.append(['VA', 'Accounts', 'Total Followers', 'Avg Followers'])
        for va, data in va_stats.iterrows():
            avg_followers_va = data['current_followers'] / data['username']
            sheet_data.append([va, data['username'], f"{data['current_followers']:,}", f"{avg_followers_va:,.0f}"])
        
        sheet_data.append([''])  # Empty row
        
        # Account details
        sheet_data.append(['📋 ACCOUNT DETAILS'])
        sheet_data.append(['Username', 'VA', 'Followers', 'Category', 'Status', 'Last Updated'])
        
        # Sort accounts by follower count
        sorted_accounts = self.accounts_data.sort_values('current_followers', ascending=False)
        
        for _, account in sorted_accounts.iterrows():
            # Determine category
            if account['current_followers'] == 0:
                category = 'Zero'
                status = '⚠️ Needs Attention'
            elif account['current_followers'] < 1000:
                category = 'Under 1K'
                status = '📈 Growth Potential'
            elif account['current_followers'] < 10000:
                category = '1K-10K'
                status = '✅ Good Performance'
            else:
                category = '10K+'
                status = '🏆 Top Performer'
            
            sheet_data.append([
                f"@{account['username']}",
                account['va_name'],
                f"{account['current_followers']:,}",
                category,
                status,
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ])
        
        return sheet_data
    
    def create_csv_for_google_sheets(self, output_file='google_sheets_ready.csv'):
        """
        Create CSV file ready for Google Sheets import
        """
        if self.accounts_data is None:
            return None
        
        # Create modern format
        modern_data = self.create_modern_tracking_sheet()
        
        # Convert to DataFrame
        df = pd.DataFrame(modern_data)
        
        # Save to CSV
        df.to_csv(output_file, index=False, header=False)
        
        logger.info(f"✅ Google Sheets ready CSV saved to: {output_file}")
        return output_file
    
    def create_original_format_csv(self, output_file='original_format_ready.csv'):
        """
        Create CSV in the original tracking sheet format
        """
        if self.accounts_data is None:
            return None
        
        # Create original format
        original_data = self.create_tracking_sheet_format()
        
        # Convert to DataFrame
        df = pd.DataFrame(original_data)
        
        # Save to CSV
        df.to_csv(output_file, index=False, header=False)
        
        logger.info(f"✅ Original format CSV saved to: {output_file}")
        return output_file
    
    def create_instructions_for_google_sheets(self):
        """
        Create instructions for importing into Google Sheets
        """
        instructions = f"""
# 📋 Google Sheets Import Instructions

## 🎯 How to Import Your Follower Tracking Data

### Option 1: Modern Format (Recommended)
1. Open your [Follower Test sheet](https://docs.google.com/spreadsheets/d/1S60I0SPAg3Y68DjZ5UUCIPaWBEXXhB9gZC4EIA1A-pA/edit?gid=0#gid=0)
2. Go to **File > Import**
3. Upload `google_sheets_ready.csv`
4. Choose **Replace current sheet**
5. Click **Import data**

### Option 2: Original Format
1. Open your [Follower Test sheet](https://docs.google.com/spreadsheets/d/1S60I0SPAg3Y68DjZ5UUCIPaWBEXXhB9gZC4EIA1A-pA/edit?gid=0#gid=0)
2. Go to **File > Import**
3. Upload `original_format_ready.csv`
4. Choose **Replace current sheet**
5. Click **Import data**

## 🎨 Formatting Tips

### Modern Format Features:
- ✅ Clean, professional layout
- ✅ Summary statistics at the top
- ✅ VA performance breakdown
- ✅ Account categorization
- ✅ Status indicators with emojis
- ✅ Easy to read and analyze

### Original Format Features:
- ✅ Matches your existing sheet structure
- ✅ VA distribution across columns
- ✅ Date rows for historical tracking
- ✅ Compatible with existing formulas

## 📊 What You'll Get:

### Summary Statistics:
- Total accounts: {len(self.accounts_data) if self.accounts_data is not None else 0}
- Total followers: {self.accounts_data['current_followers'].sum():,} if self.accounts_data is not None else 0
- Average followers: {self.accounts_data['current_followers'].mean():,.0f} if self.accounts_data is not None else 0

### VA Performance:
- Performance breakdown by VA
- Account distribution
- Follower totals per VA

### Account Details:
- All {len(self.accounts_data) if self.accounts_data is not None else 0} accounts listed
- Current follower counts
- Performance categories
- Status indicators

## 🚀 Next Steps:

1. **Import the data** using the instructions above
2. **Set up conditional formatting** for status indicators
3. **Create charts** for visual analysis
4. **Set up automated updates** with our scraping system
5. **Track growth over time** with daily snapshots

## 💡 Pro Tips:

- Use **conditional formatting** to highlight top performers
- Create **pivot tables** for VA analysis
- Set up **data validation** for consistent updates
- Use **charts** to visualize growth trends

---
*Generated by Professional Follower Tracking System*
*For support, contact the development team*
"""
        
        return instructions

def main():
    """
    Main function to create Google Sheets integration
    """
    print("🎯 GOOGLE SHEETS INTEGRATION")
    print("=" * 50)
    
    # Initialize integration
    integration = GoogleSheetsIntegration()
    
    # Load accounts
    if not integration.load_accounts():
        print("❌ Failed to load accounts")
        return
    
    print(f"✅ Loaded {len(integration.accounts_data)} accounts")
    
    # Create CSV files
    modern_file = integration.create_csv_for_google_sheets()
    original_file = integration.create_original_format_csv()
    
    # Create instructions
    instructions = integration.create_instructions_for_google_sheets()
    
    # Save instructions
    with open('google_sheets_import_instructions.md', 'w') as f:
        f.write(instructions)
    
    print(f"\n🎨 GOOGLE SHEETS INTEGRATION COMPLETE!")
    print("=" * 50)
    print(f"📁 Files created:")
    print(f"   📊 Modern format: {modern_file}")
    print(f"   📋 Original format: {original_file}")
    print(f"   📖 Instructions: google_sheets_import_instructions.md")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Open your Google Sheets")
    print(f"   2. Import {modern_file} for modern format")
    print(f"   3. Or import {original_file} for original format")
    print(f"   4. Follow instructions in google_sheets_import_instructions.md")
    
    return integration

if __name__ == "__main__":
    integration = main()
