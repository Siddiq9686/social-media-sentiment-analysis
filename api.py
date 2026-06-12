# Social Media Sentiment Analysis API

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pickle
import os
import numpy as np
from textblob import TextBlob
from scipy.sparse import hstack
import joblib

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:8010", "http://localhost:8010"]}})

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ["http://127.0.0.1:8010", "http://localhost:8010"]:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

# Function to process posts (same as in the training script)
def process_tweet(tweet):
    # Check if post is a string, if not return empty string
    if not isinstance(tweet, str):
        return ""
    # Convert to lowercase and remove special characters
    return " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])", " ", tweet.lower()).split())

# Function to create features for a single text
def create_features_for_single(text):
    features = pd.DataFrame(index=[0])
    features['text_length'] = len(text)
    features['word_count'] = len(text.split())
    features['polarity'] = TextBlob(text).sentiment.polarity
    features['subjectivity'] = TextBlob(text).sentiment.subjectivity
    return features

# Check if model exists, if not, train it
model_path = 'sentiment_model.pkl'
vectorizer_path = 'count_vectorizer.pkl'
transformer_path = 'tfidf_transformer.pkl'

if not (os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(transformer_path)):
    # Import necessary libraries for training
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB

    print("Training new model...")

    # Load training data
    train_data = pd.read_csv('text.csv')
    # Sample to speed up training on very large datasets
    if len(train_data) > 25000:
        train_data = train_data.sample(n=25000, random_state=42).reset_index(drop=True)
    # Process posts
    train_data['processed_tweets'] = train_data['text'].apply(process_tweet)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        train_data["processed_tweets"], 
        train_data["label"], 
        test_size=0.2, 
        random_state=42,
        stratify=train_data["label"]
    )
    
    # Feature extraction
    count_vect = CountVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))
    transformer = TfidfTransformer(norm='l2', sublinear_tf=True)
    
    # Transform training data (TF-IDF)
    X_train_counts = count_vect.fit_transform(X_train)
    X_train_tfidf = transformer.fit_transform(X_train_counts)
    
    # Create engineered features on original text using matching indices
    features_all = pd.DataFrame()
    features_all['text_length'] = train_data['text'].str.len()
    features_all['word_count'] = train_data['text'].str.split().str.len()
    features_all['polarity'] = train_data['text'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    features_all['subjectivity'] = train_data['text'].apply(lambda x: TextBlob(str(x)).sentiment.subjectivity)
    
    features_train = features_all.loc[X_train.index]
    
    # Combine TF-IDF with engineered features to match inference-time shape
    from scipy.sparse import hstack as _hstack
    X_train_combined = _hstack([X_train_tfidf, features_train.values])
    
    # Train Multinomial Naive Bayes model for faster training
    model = MultinomialNB()
    model.fit(X_train_combined, y_train)

    # Save model and transformers
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(count_vect, f)
    with open(transformer_path, 'wb') as f:
        pickle.dump(transformer, f)

    print("Model trained and saved successfully!")

else:
    # Load pre-trained model and transformers
    model = joblib.load(model_path)
    count_vect = joblib.load(vectorizer_path)
    transformer = joblib.load(transformer_path)

    print("Pre-trained model loaded successfully!")

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_sentiment():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    # Get post from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No text provided'}), 400
    # Accept both 'text' and legacy 'tweet' keys
    tweet = data.get('text') if data.get('text') is not None else data.get('tweet')
    if tweet is None:
        return jsonify({'error': 'No text provided'}), 400
    
    # Process post
    processed_tweet = process_tweet(tweet)

    # Transform tweet
    tweet_counts = count_vect.transform([processed_tweet])
    tweet_tfidf = transformer.transform(tweet_counts)

    # Create features
    features = create_features_for_single(tweet)

    # Select input shape dynamically to match trained model
    expected_features = getattr(model, 'n_features_in_', None)
    if expected_features is None:
        expected_features = tweet_tfidf.shape[1]
    # Decide whether to include engineered features
    if expected_features == tweet_tfidf.shape[1] + features.values.shape[1]:
        tweet_input = hstack([tweet_tfidf, features.values])
    elif expected_features == tweet_tfidf.shape[1]:
        tweet_input = tweet_tfidf
    else:
        # Fallback to TF-IDF only
        tweet_input = tweet_tfidf

    # Predict class index and probabilities from 6-way model
    prediction_idx = model.predict(tweet_input)[0]
    proba = model.predict_proba(tweet_input)[0]

    # Map numeric classes to six emotions
    six_class_map = {
        0: 'sad',
        1: 'happy',
        2: 'love',
        3: 'anger',
        4: 'fear',
        5: 'surprise'
    }

    # Aggregate to Positive/Negative/Neutral using raw probabilities
    pos_prob = float(proba[1] if six_class_map[1] == 'happy' else 0) \
        + float(proba[2] if six_class_map[2] == 'love' else 0) \
        + float(proba[5] if six_class_map[5] == 'surprise' else 0)
    neg_prob = float(proba[0] if six_class_map[0] == 'sad' else 0) \
        + float(proba[3] if six_class_map[3] == 'anger' else 0) \
        + float(proba[4] if six_class_map[4] == 'fear' else 0)
    neu_prob = max(0.0, 1.0 - pos_prob - neg_prob)

    # Convert to integer percentages that sum to 100
    pos_pct = pos_prob * 100.0
    neg_pct = neg_prob * 100.0
    neu_pct = neu_prob * 100.0
    # Initial rounded values
    three_scores = {
        'positive': int(round(pos_pct)),
        'negative': int(round(neg_pct)),
        'neutral': int(round(neu_pct))
    }
    # Normalize to ensure exact 100 after rounding
    total = sum(three_scores.values())
    if total != 100:
        # Adjust the largest bucket by the difference
        diff = 100 - total
        max_key = max(three_scores, key=three_scores.get)
        three_scores[max_key] = max(0, three_scores[max_key] + diff)

    # Final sentiment is the max among the three categories
    final_sentiment = max(three_scores, key=three_scores.get)

    return jsonify({
        'sentiment': final_sentiment,
        'scores': three_scores
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001, debug=False)