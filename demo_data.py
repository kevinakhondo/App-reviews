import pandas as pd
import random
from datetime import datetime, timedelta

def generate_demo_reviews():
    banks = [
        {"name": "Equity Bank", "country": "Kenya", "key": "equity_bank"},
        {"name": "KCB Bank", "country": "Kenya", "key": "kcb"},
        {"name": "GTBank", "country": "Nigeria", "key": "gtbank"},
        {"name": "Access Bank", "country": "Nigeria", "key": "access_bank"}
    ]
    
    negative_reviews = [
        "App keeps crashing when I try to login", "Terrible customer service", 
        "Transactions fail constantly", "UI is confusing", "Very slow app",
        "Security concerns with this app", "Can't download statements", 
        "Biometric login broken", "Hidden fees everywhere"
    ]
    
    neutral_reviews = [
        "App works fine but could be faster", "Basic features only",
        "Sometimes works sometimes doesn't", "Average banking app",
        "Okay for checking balance", "Decent but not great"
    ]
    
    positive_reviews = [
        "Excellent app, very fast", "Love the new design", "Best banking app",
        "Great customer service", "Secure and reliable", "Easy to use",
        "Quick loan approvals", "Love the notifications"
    ]
    
    all_reviews = []
    
    for bank in banks:
        # Generate 50 reviews per bank with different sentiment distributions
        if bank["name"] == "GTBank":
            weights = [0.4, 0.3, 0.3]  # More negative
        elif bank["name"] == "Access Bank":
            weights = [0.2, 0.3, 0.5]  # More positive
        else:
            weights = [0.3, 0.3, 0.4]  # Balanced
        
        for i in range(50):
            sentiment = random.choices(['Negative', 'Neutral', 'Positive'], weights=weights)[0]
            
            if sentiment == 'Negative':
                content = random.choice(negative_reviews)
                score = random.choice([1, 2])
            elif sentiment == 'Neutral':
                content = random.choice(neutral_reviews)
                score = 3
            else:
                content = random.choice(positive_reviews)
                score = random.choice([4, 5])
            
            review = {
                'reviewId': f"{bank['key']}_{i}",
                'userName': f"User{i}",
                'content': content,
                'score': score,
                'thumbsUpCount': random.randint(0, 20),
                'at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'appVersion': '5.2.1',
                'bank_name': bank['name'],
                'bank_key': bank['key'],
                'country': bank['country'],
                'scraped_at': datetime.now()
            }
            all_reviews.append(review)
    
    df = pd.DataFrame(all_reviews)
    df.to_csv('data/reviews_20260327_demo.csv', index=False)
    print(f"✓ Generated {len(df)} demo reviews")
    return df

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    generate_demo_reviews()
