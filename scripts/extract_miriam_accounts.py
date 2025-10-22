import pandas as pd
import os

def extract_miriam_accounts():
    """
    Extract Miriam accounts from the CSV file
    """
    csv_path = '/Users/felixhergenroeder/Downloads/Tiktok Tracking Sheet - MIRIAMUS.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path)
    
    print(f"📋 CSV Structure: {len(df)} rows, {len(df.columns)} columns")
    
    # Find the account names row
    accounts = []
    
    # Look through the first 10 rows to find account data
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        non_empty = row.dropna()
        
        if len(non_empty) > 5:  # Row with multiple values
            values = [str(v).strip() for v in non_empty.values if str(v).strip()]
            
            # Check if this row contains account names
            if any('miriam' in v.lower() for v in values[:10]):
                print(f"✅ Found account row {i+1}: {values[:5]}...")
                
                # Extract account names and followers
                if i + 1 < len(df):
                    follower_row = df.iloc[i + 1]
                    
                    for j, (account, followers) in enumerate(zip(row, follower_row)):
                        if pd.notna(account) and str(account).strip():
                            account_name = str(account).strip()
                            
                            # Filter for actual account names
                            if (account_name.lower() != 'account name' and 
                                'miriam' in account_name.lower() and 
                                len(account_name) > 3 and
                                not account_name.startswith('Tiktok') and
                                not account_name.startswith('LINK') and
                                not account_name.startswith('Social')):
                                
                                try:
                                    follower_count = int(followers) if pd.notna(followers) and str(followers).replace(',', '').isdigit() else 0
                                    
                                    # Determine VA based on column position
                                    va_mapping = {
                                        1: 'CARLA', 2: 'JAROLD', 3: 'AARON', 4: 'JOSUHA', 
                                        5: 'GRASHANG', 6: 'JAIRIS', 7: 'SAMUEL', 8: 'LIYA'
                                    }
                                    va_name = va_mapping.get(j, 'UNKNOWN')
                                    
                                    accounts.append({
                                        'username': account_name,
                                        'va_name': va_name,
                                        'current_followers': follower_count,
                                        'column': j
                                    })
                                    
                                except Exception as e:
                                    print(f"   Error processing {account_name}: {e}")
                                    continue
    
    print(f"\n📊 EXTRACTED {len(accounts)} MIRIAM ACCOUNTS:")
    print("=" * 60)
    
    for i, acc in enumerate(accounts, 1):
        print(f"{i:2d}. @{acc['username']:25s} | {acc['va_name']:10s} | {acc['current_followers']:>8,} followers")
    
    if accounts:
        total_followers = sum(acc['current_followers'] for acc in accounts)
        avg_followers = total_followers / len(accounts)
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total accounts: {len(accounts)}")
        print(f"   Total followers: {total_followers:,}")
        print(f"   Average followers: {avg_followers:,.0f}")
        print(f"   Largest: {max(accounts, key=lambda x: x['current_followers'])['current_followers']:,}")
        print(f"   Smallest: {min(accounts, key=lambda x: x['current_followers'])['current_followers']:,}")
    
    # Save to CSV
    if accounts:
        accounts_df = pd.DataFrame(accounts)
        output_file = 'miriam_accounts_extracted.csv'
        accounts_df.to_csv(output_file, index=False)
        print(f"\n💾 Saved to: {output_file}")
    
    return accounts

if __name__ == "__main__":
    accounts = extract_miriam_accounts()
