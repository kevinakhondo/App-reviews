from google_play_scraper import Sort, reviews
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.banks import BANKS

class BankReviewScraper:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.banks = BANKS
    
    def scrape_all_reviews(self, bank_key, days_back=365):
        """Scrape ALL available reviews for a bank"""
        bank = self.banks[bank_key]
        print(f"\n🔍 Scraping ALL reviews for {bank['name']}...")
        
        all_reviews = []
        continuation_token = None
        batch_count = 0
        max_batches = 100  # Up to 20,000 reviews per bank
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        while batch_count < max_batches:
            try:
                if continuation_token is None:
                    result, continuation_token = reviews(
                        bank['app_id'],
                        lang='en',
                        country=bank['region'],
                        sort=Sort.NEWEST,
                        count=200
                    )
                else:
                    result, continuation_token = reviews(
                        bank['app_id'],
                        continuation_token=continuation_token
                    )
                
                if not result:
                    break
                
                batch_count += 1
                print(f"  Batch {batch_count}: +{len(result)} reviews")
                
                df = pd.DataFrame(result)
                
                # Handle date
                date_col = 'at' if 'at' in df.columns else 'date' if 'date' in df.columns else None
                if date_col:
                    df[date_col] = pd.to_datetime(df[date_col])
                    df = df[df[date_col] > cutoff_date]
                    if date_col != 'at':
                        df['at'] = df[date_col]
                else:
                    df['at'] = datetime.now()
                
                # Add metadata
                df['bank_name'] = bank['name']
                df['bank_key'] = bank_key
                df['country'] = bank['country']
                df['scraped_at'] = datetime.now()
                
                cols = ['reviewId', 'userName', 'content', 'score', 'thumbsUpCount', 'at', 'appVersion']
                available = [c for c in cols if c in df.columns]
                df = df[available + ['bank_name', 'bank_key', 'country', 'scraped_at']]
                
                all_reviews.append(df)
                
                # Check if we've gone past cutoff
                if date_col and len(df) > 0:
                    oldest = df[date_col].min()
                    if oldest < cutoff_date:
                        print(f"  → Reached date cutoff")
                        break
                
                if continuation_token is None:
                    print(f"  → No more pages")
                    break
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                break
        
        if all_reviews:
            combined = pd.concat(all_reviews, ignore_index=True)
            combined = combined.drop_duplicates(subset=['reviewId'])
            print(f"  ✓ {bank['name']}: {len(combined)} total reviews")
            return combined
        
        return pd.DataFrame()
    
    def scrape_all_banks(self, days_back=365):
        """Scrape ALL reviews for ALL banks"""
        print(f"\n{'='*70}")
        print(f"FETCHING ALL REVIEWS (Last {days_back} days)")
        print(f"{'='*70}")
        
        all_bank_reviews = []
        
        for bank_key in self.banks:
            df = self.scrape_all_reviews(bank_key, days_back)
            if not df.empty:
                all_bank_reviews.append(df)
            time.sleep(1)
        
        if all_bank_reviews:
            combined = pd.concat(all_bank_reviews, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.data_dir}/ALL_REVIEWS_{timestamp}.csv"
            combined.to_csv(filename, index=False)
            
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS: {len(combined):,} TOTAL REVIEWS")
            print(f"✅ Saved: {filename}")
            print(f"{'='*70}")
            
            print(f"\n📊 BREAKDOWN:")
            for bank, count in combined['bank_name'].value_counts().items():
                pct = count / len(combined) * 100
                print(f"  • {bank}: {count:,} reviews ({pct:.1f}%)")
            
            return combined
        
        print("\n❌ No reviews scraped")
        return pd.DataFrame()
    
    def get_latest_file(self):
        if not os.path.exists(self.data_dir):
            return None
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        if not files:
            return None
        files_with_paths = [f"{self.data_dir}/{f}" for f in files]
        return max(files_with_paths, key=os.path.getctime)
