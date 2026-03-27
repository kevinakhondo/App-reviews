import pandas as pd
import numpy as np
import re
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

class SentimentAnalyzer:
    def __init__(self, model_dir="data"):
        self.model_dir = model_dir
        self.vectorizer = None
        self.model = None
        self.model_path = f"{model_dir}/model.pkl"
        self.vect_path = f"{model_dir}/vectorizer.pkl"
    
    def clean_text(self, text):
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        words = text.split()
        words = [w for w in words if len(w) > 2]
        return ' '.join(words)
    
    def prepare_data(self, df):
        df = df.copy()
        df['clean'] = df['content'].apply(self.clean_text)
        def to_sentiment(score):
            if score <= 2: return 0
            elif score == 3: return 1
            else: return 2
        df['sentiment_code'] = df['score'].apply(to_sentiment)
        df = df[df['clean'].str.len() > 0]
        return df
    
    def train(self, df):
        print("Training model...")
        data = self.prepare_data(df)
        X = data['clean']
        y = data['sentiment_code']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        self.model = LogisticRegression(max_iter=1000, class_weight='balanced')
        self.model.fit(X_train_vec, y_train)
        acc = accuracy_score(y_test, self.model.predict(X_test_vec))
        print(f"Accuracy: {acc:.2%}")
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vect_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        return acc
    
    def load(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vect_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vect_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            return True
        return False
    
    def predict(self, texts):
        if self.model is None:
            if not self.load():
                raise ValueError("No model")
        if isinstance(texts, str):
            texts = [texts]
        clean = [self.clean_text(t) for t in texts]
        vec = self.vectorizer.transform(clean)
        preds = self.model.predict(vec)
        labels = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
        return [labels[p] for p in preds]
    
    def analyze_df(self, df):
        df = df.copy()
        df['sentiment'] = self.predict(df['content'].tolist())
        return df
