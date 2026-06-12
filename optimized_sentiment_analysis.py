#!/usr/bin/env python3
"""
Optimized Sentiment Analysis - High Accuracy Focus
Streamlined version for quick results with major improvements
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
import xgboost as xgb
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')

warnings.filterwarnings('ignore')

def advanced_preprocessing(text):
    """Advanced text preprocessing"""
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in text.split() 
             if token not in stop_words and len(token) > 2]
    
    return ' '.join(tokens)

def create_features(df):
    """Create additional features"""
    features = pd.DataFrame()
    features['text_length'] = df['text'].str.len()
    features['word_count'] = df['text'].str.split().str.len()
    features['polarity'] = df['text'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    features['subjectivity'] = df['text'].apply(lambda x: TextBlob(str(x)).sentiment.subjectivity)
    return features

def main():
    print("🚀 Optimized Sentiment Analysis - High Accuracy Focus")
    print("=" * 55)
    
    # Load data
    try:
        df = pd.read_csv('text.csv')
        print(f"Dataset loaded: {len(df)} samples")
        
        if len(df) > 25000:
            df = df.sample(n=25000, random_state=42)
            print(f"Sampled to {len(df)} samples for faster processing")
            
    except FileNotFoundError:
        print("Creating sample data...")
        np.random.seed(42)
        texts = ["amazing product love it", "terrible worst experience", "good but okay", 
                "excellent service", "poor quality", "outstanding performance"] * 100
        labels = [2, 0, 1, 2, 0, 2] * 100
        df = pd.DataFrame({'text': texts, 'label': labels})
    
    # Preprocess
    print("Preprocessing...")
    df['processed'] = df['text'].apply(advanced_preprocessing)
    
    # Create features
    features = create_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['processed'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )
    
    # Optimize vectorizer
    print("Optimizing vectorizer...")
    vectorizer = CountVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Define optimized models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, C=2.0, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
        'SVM': SVC(kernel='rbf', C=5.0, probability=True, random_state=42),
        'Naive Bayes': MultinomialNB(alpha=0.1),
        'XGBoost': xgb.XGBClassifier(n_estimators=200, max_depth=6, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, random_state=42)
    }
    
    # Train models
    results = {}
    print("\nTraining optimized models...")
    print("-" * 30)
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)
        
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'predictions': y_pred,
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
        
        print(f"  Accuracy: {accuracy:.4f}")
    
    # Results
    best_model = max(results, key=lambda x: results[x]['accuracy'])
    best_accuracy = results[best_model]['accuracy']
    
    # Create visualizations
    plt.figure(figsize=(15, 10))
    
    # Model comparison
    plt.subplot(2, 2, 1)
    names = list(results.keys())
    accuracies = [results[m]['accuracy'] for m in names]
    colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
    plt.bar(names, accuracies, color=colors)
    plt.title('Model Accuracy Comparison')
    plt.xticks(rotation=45)
    plt.ylabel('Accuracy')
    plt.grid(True, alpha=0.3)
    
    # Best model confusion matrix
    plt.subplot(2, 2, 2)
    cm = results[best_model]['confusion_matrix']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {best_model}\nAccuracy: {best_accuracy:.4f}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    
    # Performance summary
    plt.subplot(2, 2, 3)
    performance = pd.DataFrame({
        'Model': names,
        'Accuracy': accuracies
    }).sort_values('Accuracy', ascending=False)
    plt.barh(performance['Model'], performance['Accuracy'], color='lightcoral')
    plt.title('Model Performance Ranking')
    plt.xlabel('Accuracy')
    
    # Improvement indicator
    plt.subplot(2, 2, 4)
    baseline = min(accuracies)
    improvement = [(acc - baseline) / baseline * 100 for acc in accuracies]
    plt.bar(names, improvement, color='green')
    plt.title('Improvement over Baseline (%)')
    plt.xticks(rotation=45)
    plt.ylabel('Improvement %')
    
    plt.tight_layout()
    plt.savefig('optimized_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save results
    import joblib
    joblib.dump(results[best_model]['model'], 'optimized_model.pkl')
    joblib.dump(vectorizer, 'optimized_vectorizer.pkl')
    
    # Print summary
    print(f"\n🎯 Best Model: {best_model}")
    print(f"📊 Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
    print(f"🚀 Improvement: {((best_accuracy - 0.8838) / 0.8838 * 100):.2f}% over original")
    print("💾 Models saved: optimized_model.pkl, optimized_vectorizer.pkl")
    print("📈 Visualization saved: optimized_results.png")
    
    return best_model, best_accuracy

if __name__ == "__main__":
    main()