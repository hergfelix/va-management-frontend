import pandas as pd

def clean_miriam_accounts():
    """
    Clean and organize the Miriam accounts data
    """
    # Load the extracted accounts
    df = pd.read_csv('miriam_accounts_extracted.csv')
    
    # Filter out bio text and keep only actual usernames
    clean_accounts = []
    
    for _, row in df.iterrows():
        username = row['username']
        
        # Skip if it's bio text (contains newlines or is too long)
        if ('\n' in username or 
            len(username) > 50 or 
            'IG:' in username or 
            'click' in username.lower() or
            'worth' in username.lower() or
            'curious' in username.lower()):
            continue
            
        # Skip if it's not a proper username
        if (username.startswith('@') or 
            username.startswith('your') or
            username.startswith('POV') or
            username.startswith('Good') or
            username.startswith('Life') or
            username.startswith('Sassy') or
            username.startswith('Moments') or
            username.startswith('She') or
            username.startswith('Just') or
            username.startswith('Not') or
            username.startswith('flirtatious') or
            username.startswith('ꜱᴜɳ') or
            username.startswith('good') or
            username.startswith('Be')):
            continue
        
        clean_accounts.append({
            'username': username,
            'va_name': row['va_name'],
            'current_followers': row['current_followers'],
            'column': row['column']
        })
    
    # Create clean DataFrame
    clean_df = pd.DataFrame(clean_accounts)
    
    print(f"🧹 CLEANED MIRIAM ACCOUNTS:")
    print(f"=" * 60)
    print(f"Original accounts: {len(df)}")
    print(f"Clean accounts: {len(clean_df)}")
    print()
    
    # Show clean accounts
    for i, (_, row) in enumerate(clean_df.iterrows(), 1):
        print(f"{i:2d}. @{row['username']:25s} | {row['va_name']:10s} | {row['current_followers']:>8,} followers")
    
    # Statistics
    if len(clean_df) > 0:
        total_followers = clean_df['current_followers'].sum()
        avg_followers = total_followers / len(clean_df)
        
        print(f"\n📈 CLEAN STATISTICS:")
        print(f"   Total accounts: {len(clean_df)}")
        print(f"   Total followers: {total_followers:,}")
        print(f"   Average followers: {avg_followers:,.0f}")
        print(f"   Largest: {clean_df['current_followers'].max():,}")
        print(f"   Smallest: {clean_df['current_followers'].min():,}")
        
        # VA breakdown
        print(f"\n👥 VA BREAKDOWN:")
        va_stats = clean_df.groupby('va_name').agg({
            'username': 'count',
            'current_followers': 'sum'
        }).round(0)
        va_stats.columns = ['Accounts', 'Total Followers']
        va_stats = va_stats.sort_values('Total Followers', ascending=False)
        
        for va, stats in va_stats.iterrows():
            print(f"   {va:10s}: {stats['Accounts']:2.0f} accounts, {stats['Total Followers']:>8,.0f} followers")
    
    # Save clean data
    clean_df.to_csv('miriam_accounts_clean.csv', index=False)
    print(f"\n💾 Saved clean data to: miriam_accounts_clean.csv")
    
    return clean_df

if __name__ == "__main__":
    clean_df = clean_miriam_accounts()
