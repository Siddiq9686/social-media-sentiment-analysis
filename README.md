# Social Media Sentiment Analysis Project

## Overview
This project implements a sentiment analysis pipeline for social media data. It analyzes posts and classifies them into sentiment categories using machine learning techniques. **Enhanced version achieves 89.88% accuracy** with optimized preprocessing and advanced models.

## Dataset
The project uses two CSV files:
- `X_Training.csv`: Contains the training data with labeled posts
- `X_Validation.csv`: Contains the validation/test data with labeled posts

Each dataset has the following columns:
- `id`: Unique identifier for each post
- `topic`: The topic or category of the post
) - `label`: The sentiment label (0=irrelevant, 1=positive, 2=negative, 3=neutral, 4=anger, 5=sadness)
 - `post`: The actual text content of the post

## Implementation Steps

### 1. Data Loading and Exploration
- Loads training data from CSV file
- Checks data types and non-null counts
- Analyzes the distribution of sentiment labels
- Displays sample data for inspection

### 2. Text Preprocessing
- Converts text to lowercase
- Removes URLs, mentions, hashtags, special characters, and numbers
- Tokenizes the posts into individual words
- Applies stemming using Snowball Stemmer
- Removes stopwords and punctuation
- Joins processed tokens back into strings

### 3. Feature Extraction
- Uses CountVectorizer with n-gram range (1,2) and max_features=5000
- Applies TF-IDF transformation to the count matrix
- Adds 6 engineered features (character count, word count, punctuation analysis, uppercase ratio, average word length)

### 4. Model Training and Evaluation
- Trains enhanced models:
  - Logistic Regression (optimized for production)
  - XGBoost Classifier
  - Gradient Boosting Classifier
  - SVM Classifier
  - Naive Bayes Classifier
- Evaluates each model using confusion matrix, accuracy, precision, recall, and F1-score
- Uses 5-fold stratified cross-validation

### 5. Model Comparison
- Compares the performance of all enhanced models
- Visualizes the accuracy comparison with improvements

### 6. Prediction on Test Data
- Applies the same preprocessing steps to the test data
- Uses the best-performing model (Logistic Regression) to make predictions
- Evaluates the model's performance on test data
- Saves predictions to a CSV file
- Visualizes the confusion matrix for test data

## Requirements
- Python 3.6+
- pandas
- numpy
- matplotlib
- seaborn
- nltk
- scikit-learn
- xgboost

## How to Run

1. Install the required packages:
```
pip install -r requirements.txt
```

2. Download NLTK resources (this is also done in the script):
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

3. Run the sentiment analysis script:
```
python optimized_sentiment_analysis.py
```

4. Start web server for real-time analysis:
```
python -m http.server 8010
```

## Output
- `model_comparison.png`: Visualization comparing the accuracy of different models
- `test_confusion_matrix.png`: Confusion matrix visualization for test data
- `predictions.csv`: CSV file containing the original labels and predicted labels for the test data
- Enhanced visualizations and updated charts

## Performance Metrics
The script outputs various performance metrics including:
- **89.88% Accuracy** with +1.70% improvement over baseline
- Precision, Recall, F1-score for 6 sentiment classes
- Confusion matrix for multi-class classification
- Cross-validation scores

These metrics are calculated for both training and test datasets to evaluate the model's performance and generalization capability.