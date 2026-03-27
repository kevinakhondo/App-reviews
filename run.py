#!/usr/bin/env python3
from scraper.review_scraper import BankReviewScraper
from models.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

def main():
    print("🏦 BankWatch Africa - MAXIMUM REVIEWS MODE")
    
    scraper = BankReviewScraper()
    df = scraper.scrape_all_banks(days_back=365)
    
    if df.empty:
        print("❌ Failed")
        return
    
    print(f"\n🤖 Analyzing {len(df):,} reviews with ML...")
    analyzer = SentimentAnalyzer()
    if not analyzer.load():
        analyzer.train(df)
    df = analyzer.analyze_df(df)
    
    print(f"\n📈 RESULTS:")
    print(df['sentiment'].value_counts())
    
    # Save analyzed data
    df.to_csv('data/ALL_REVIEWS_ANALYZED.csv', index=False)
    print(f"\n✅ Done! Analyzed data saved.")
    print(f"🌐 Dashboard: python3 -m streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()
