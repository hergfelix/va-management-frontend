"""
Professional Follower Tracking Dashboard
Modern, clean, and professional-looking follower tracking system
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import json
import os

# Set professional styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class ProfessionalFollowerDashboard:
    """
    Professional follower tracking dashboard
    """
    
    def __init__(self):
        self.accounts_data = None
        self.follower_history = None
        self.va_performance = None
        
    def load_data(self, accounts_file='miriam_accounts_clean.csv', test_results_file='test_scraper_results.csv'):
        """
        Load account and follower data
        """
        # Load accounts
        if os.path.exists(accounts_file):
            self.accounts_data = pd.read_csv(accounts_file)
            print(f"✅ Loaded {len(self.accounts_data)} accounts from {accounts_file}")
        else:
            print(f"❌ Accounts file not found: {accounts_file}")
            return False
            
        # Load test results if available
        if os.path.exists(test_results_file):
            test_results = pd.read_csv(test_results_file)
            print(f"✅ Loaded {len(test_results)} test results from {test_results_file}")
            
            # Merge test results with accounts data
            self.accounts_data = self.accounts_data.merge(
                test_results[['username', 'followers', 'scraped_at']], 
                on='username', 
                how='left', 
                suffixes=('_old', '_new')
            )
            
            # Use new follower count if available
            self.accounts_data['current_followers'] = self.accounts_data['followers'].fillna(
                self.accounts_data['current_followers']
            )
        else:
            print(f"⚠️ Test results file not found: {test_results_file}")
        
        return True
    
    def create_summary_stats(self):
        """
        Create professional summary statistics
        """
        if self.accounts_data is None:
            return None
            
        stats = {
            'total_accounts': len(self.accounts_data),
            'total_followers': self.accounts_data['current_followers'].sum(),
            'average_followers': self.accounts_data['current_followers'].mean(),
            'largest_account': self.accounts_data['current_followers'].max(),
            'smallest_account': self.accounts_data['current_followers'].min(),
            'accounts_over_10k': len(self.accounts_data[self.accounts_data['current_followers'] >= 10000]),
            'accounts_over_1k': len(self.accounts_data[self.accounts_data['current_followers'] >= 1000]),
            'zero_followers': len(self.accounts_data[self.accounts_data['current_followers'] == 0])
        }
        
        return stats
    
    def create_va_breakdown(self):
        """
        Create VA performance breakdown
        """
        if self.accounts_data is None:
            return None
            
        va_stats = self.accounts_data.groupby('va_name').agg({
            'username': 'count',
            'current_followers': ['sum', 'mean', 'max']
        }).round(0)
        
        va_stats.columns = ['Accounts', 'Total_Followers', 'Avg_Followers', 'Max_Followers']
        va_stats = va_stats.sort_values('Total_Followers', ascending=False)
        
        return va_stats
    
    def create_follower_distribution_chart(self):
        """
        Create professional follower distribution chart
        """
        if self.accounts_data is None:
            return None
            
        # Create follower ranges
        def get_follower_range(followers):
            if followers == 0:
                return '0'
            elif followers < 1000:
                return '1-999'
            elif followers < 5000:
                return '1K-5K'
            elif followers < 10000:
                return '5K-10K'
            elif followers < 50000:
                return '10K-50K'
            else:
                return '50K+'
        
        self.accounts_data['follower_range'] = self.accounts_data['current_followers'].apply(get_follower_range)
        
        # Create chart
        fig = px.bar(
            self.accounts_data['follower_range'].value_counts().sort_index(),
            title="📊 Follower Distribution Across Accounts",
            labels={'index': 'Follower Range', 'value': 'Number of Accounts'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            title_font_size=20,
            title_x=0.5,
            xaxis_title="Follower Range",
            yaxis_title="Number of Accounts",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_top_accounts_chart(self, top_n=10):
        """
        Create top performing accounts chart
        """
        if self.accounts_data is None:
            return None
            
        top_accounts = self.accounts_data.nlargest(top_n, 'current_followers')
        
        fig = px.bar(
            top_accounts,
            x='current_followers',
            y='username',
            orientation='h',
            title=f"🏆 Top {top_n} Accounts by Follower Count",
            labels={'current_followers': 'Followers', 'username': 'Account'},
            color='current_followers',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            title_font_size=20,
            title_x=0.5,
            xaxis_title="Follower Count",
            yaxis_title="Account",
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400 + (top_n * 30)
        )
        
        return fig
    
    def create_va_performance_chart(self):
        """
        Create VA performance comparison chart
        """
        va_stats = self.create_va_breakdown()
        if va_stats is None:
            return None
            
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Followers', 'Average Followers', 'Number of Accounts', 'Max Followers'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Total Followers
        fig.add_trace(
            go.Bar(x=va_stats.index, y=va_stats['Total_Followers'], name='Total Followers', marker_color='#1f77b4'),
            row=1, col=1
        )
        
        # Average Followers
        fig.add_trace(
            go.Bar(x=va_stats.index, y=va_stats['Avg_Followers'], name='Avg Followers', marker_color='#ff7f0e'),
            row=1, col=2
        )
        
        # Number of Accounts
        fig.add_trace(
            go.Bar(x=va_stats.index, y=va_stats['Accounts'], name='Accounts', marker_color='#2ca02c'),
            row=2, col=1
        )
        
        # Max Followers
        fig.add_trace(
            go.Bar(x=va_stats.index, y=va_stats['Max_Followers'], name='Max Followers', marker_color='#d62728'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="👥 VA Performance Breakdown",
            title_font_size=20,
            title_x=0.5,
            showlegend=False,
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_growth_simulation(self, days=30):
        """
        Create simulated growth projection
        """
        if self.accounts_data is None:
            return None
            
        # Simulate growth for top 5 accounts
        top_accounts = self.accounts_data.nlargest(5, 'current_followers')
        
        fig = go.Figure()
        
        for _, account in top_accounts.iterrows():
            # Simulate growth (random walk with slight upward trend)
            current_followers = account['current_followers']
            growth_rate = np.random.normal(0.02, 0.05, days)  # 2% average daily growth
            
            followers_over_time = [current_followers]
            for rate in growth_rate:
                new_followers = followers_over_time[-1] * (1 + rate)
                followers_over_time.append(max(0, new_followers))
            
            dates = pd.date_range(start=datetime.now(), periods=days+1, freq='D')
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=followers_over_time,
                mode='lines+markers',
                name=f"@{account['username']}",
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="📈 Projected Growth (30 Days)",
            title_font_size=20,
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Follower Count",
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500
        )
        
        return fig
    
    def create_professional_report(self):
        """
        Create a comprehensive professional report
        """
        if self.accounts_data is None:
            return "No data available"
            
        stats = self.create_summary_stats()
        va_stats = self.create_va_breakdown()
        
        report = f"""
# 🎯 TikTok Follower Tracking Report
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

## 📊 Executive Summary
- **Total Accounts:** {stats['total_accounts']:,}
- **Total Followers:** {stats['total_followers']:,}
- **Average Followers:** {stats['average_followers']:,.0f}
- **Largest Account:** {stats['largest_account']:,} followers
- **Accounts Over 10K:** {stats['accounts_over_10k']:,}
- **Accounts Over 1K:** {stats['accounts_over_1k']:,}

## 👥 VA Performance
"""
        
        for va, data in va_stats.iterrows():
            report += f"- **{va}:** {data['Accounts']:.0f} accounts, {data['Total_Followers']:,.0f} total followers, {data['Avg_Followers']:,.0f} avg\n"
        
        report += f"""
## 🏆 Top Performing Accounts
"""
        
        top_5 = self.accounts_data.nlargest(5, 'current_followers')
        for i, (_, account) in enumerate(top_5.iterrows(), 1):
            report += f"{i}. **@{account['username']}** - {account['current_followers']:,} followers ({account['va_name']})\n"
        
        report += f"""
## 📈 Growth Opportunities
- **Zero Followers:** {stats['zero_followers']} accounts need attention
- **Under 1K:** {len(self.accounts_data[self.accounts_data['current_followers'] < 1000])} accounts with growth potential
- **Top Performers:** {stats['accounts_over_10k']} accounts exceeding 10K followers

---
*Report generated by Professional Follower Tracking System*
"""
        
        return report
    
    def save_dashboard_data(self, output_dir='dashboard_data'):
        """
        Save all dashboard data and charts
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save summary stats
        stats = self.create_summary_stats()
        with open(f'{output_dir}/summary_stats.json', 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        # Save VA breakdown
        va_stats = self.create_va_breakdown()
        va_stats.to_csv(f'{output_dir}/va_breakdown.csv')
        
        # Save accounts data
        self.accounts_data.to_csv(f'{output_dir}/accounts_data.csv', index=False)
        
        # Save charts
        charts = {
            'follower_distribution': self.create_follower_distribution_chart(),
            'top_accounts': self.create_top_accounts_chart(),
            'va_performance': self.create_va_performance_chart(),
            'growth_simulation': self.create_growth_simulation()
        }
        
        for name, chart in charts.items():
            if chart is not None:
                chart.write_html(f'{output_dir}/{name}.html')
        
        # Save report
        report = self.create_professional_report()
        with open(f'{output_dir}/professional_report.md', 'w') as f:
            f.write(report)
        
        print(f"✅ Dashboard data saved to {output_dir}/")
        return output_dir

def main():
    """
    Main function to create and display the professional dashboard
    """
    print("🎯 PROFESSIONAL FOLLOWER TRACKING DASHBOARD")
    print("=" * 60)
    
    # Initialize dashboard
    dashboard = ProfessionalFollowerDashboard()
    
    # Load data
    if not dashboard.load_data():
        print("❌ Failed to load data")
        return
    
    # Create and display summary
    stats = dashboard.create_summary_stats()
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Total Accounts: {stats['total_accounts']:,}")
    print(f"   Total Followers: {stats['total_followers']:,}")
    print(f"   Average Followers: {stats['average_followers']:,.0f}")
    print(f"   Largest Account: {stats['largest_account']:,}")
    print(f"   Accounts Over 10K: {stats['accounts_over_10k']:,}")
    
    # Create VA breakdown
    va_stats = dashboard.create_va_breakdown()
    print(f"\n👥 VA PERFORMANCE:")
    for va, data in va_stats.iterrows():
        print(f"   {va:10s}: {data['Accounts']:2.0f} accounts, {data['Total_Followers']:>8,.0f} followers")
    
    # Save dashboard data
    output_dir = dashboard.save_dashboard_data()
    
    print(f"\n🎨 PROFESSIONAL DASHBOARD CREATED!")
    print(f"   📁 Data saved to: {output_dir}/")
    print(f"   📊 Charts: follower_distribution.html, top_accounts.html, va_performance.html")
    print(f"   📈 Growth simulation: growth_simulation.html")
    print(f"   📋 Report: professional_report.md")
    
    return dashboard

if __name__ == "__main__":
    dashboard = main()
