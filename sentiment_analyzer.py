"""
sentiment_analyzer.py
=====================
Loads the trained Naive Bayes model and classifies TMDB reviews.
Reads the 'content' field from each TMDB review JSON dict.
"""

import os
import re
import pickle

import nltk
nltk.download('stopwords', quiet=True)
STOPWORDS = set(nltk.corpus.stopwords.words('english'))


def _extract_features(text, top_words_set):
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    words = {w for w in words if w not in STOPWORDS and len(w) > 2}
    return {f'contains({w})': (w in words) for w in top_words_set}


def _label_to_sentiment(label):
    return 'positive' if label == 'pos' else 'negative'


class SentimentAnalyzer:

    def __init__(self, model_path='models/sentiment_model.pkl'):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at '{model_path}'. "
                "Please run model_trainer.py first."
            )
        with open(model_path, 'rb') as f:
            payload = pickle.load(f)

        self._classifier    = payload['classifier']
        self._top_words     = payload['top_words']
        self._top_words_set = set(self._top_words)
        print(f"  Vocabulary size : {len(self._top_words)}")

    def _predict_one(self, text):
        features = _extract_features(text, self._top_words_set)
        dist     = self._classifier.prob_classify(features)
        label    = dist.max()
        pos_prob = dist.prob('pos')
        neg_prob = dist.prob('neg')
        return label, pos_prob, neg_prob

    def analyze_single(self, review_text):
        label, pos_prob, neg_prob = self._predict_one(review_text)
        confidence = pos_prob if label == 'pos' else neg_prob
        return {
            'sentiment':            _label_to_sentiment(label),
            'confidence':           round(float(confidence), 4),
            'positive_probability': round(float(pos_prob),   4),
            'negative_probability': round(float(neg_prob),   4),
        }

    def analyze_batch(self, reviews):
        """Input: list of plain text strings (the 'content' fields from TMDB JSON)."""
        if not reviews:
            return {'error': 'No reviews provided', 'total_reviews': 0}

        detailed_results = []
        confidences      = []
        positive_count   = 0

        for i, text in enumerate(reviews):
            label, pos_prob, neg_prob = self._predict_one(text)
            confidence = pos_prob if label == 'pos' else neg_prob
            confidences.append(confidence)
            if label == 'pos':
                positive_count += 1

            detailed_results.append({
                'review_number':        i + 1,
                'review_text':          text[:200] + '…' if len(text) > 200 else text,
                'sentiment':            _label_to_sentiment(label),
                'confidence':           round(float(confidence), 4),
                'positive_probability': round(float(pos_prob),   4),
                'negative_probability': round(float(neg_prob),   4),
            })

        total          = len(reviews)
        negative_count = total - positive_count
        avg_confidence = sum(confidences) / total

        return {
            'total_reviews':       total,
            'positive_count':      positive_count,
            'negative_count':      negative_count,
            'positive_percentage': round((positive_count / total) * 100, 2),
            'negative_percentage': round((negative_count / total) * 100, 2),
            'average_confidence':  round(float(avg_confidence), 3),
            'detailed_results':    detailed_results,
        }

    def find_positive_and_negative_examples(self, reviews_data):
        """Input: raw TMDB review JSON list — reads 'content' from each dict."""
        if not reviews_data:
            print("  No reviews data provided")
            return None, None

        print(f"  Processing {len(reviews_data)} TMDB reviews…")

        positive_reviews = []
        negative_reviews = []

        for review_data in reviews_data:
            text = review_data.get('content', '') or ''
            if not text.strip():
                continue

            label, pos_prob, neg_prob = self._predict_one(text)
            confidence = pos_prob if label == 'pos' else neg_prob

            entry = {
                'author':               review_data.get('author', 'Unknown'),
                'content':              text,
                'rating':               review_data.get('rating'),
                'created_at':           review_data.get('created_at'),
                'sentiment':            _label_to_sentiment(label),
                'confidence':           round(float(confidence), 4),
                'positive_probability': round(float(pos_prob),   4),
                'negative_probability': round(float(neg_prob),   4),
            }

            if label == 'pos':
                positive_reviews.append(entry)
            else:
                negative_reviews.append(entry)

        print(f"  Found {len(positive_reviews)} positive "
              f"and {len(negative_reviews)} negative reviews")

        positive_reviews.sort(key=lambda x: x['confidence'], reverse=True)
        negative_reviews.sort(key=lambda x: x['confidence'], reverse=True)

        best_positive = positive_reviews[0] if positive_reviews else None
        best_negative = negative_reviews[0] if negative_reviews else None

        if best_positive is None:
            print("  Warning: No positive reviews found")
        if best_negative is None:
            print("  Warning: No negative reviews found")

        return best_positive, best_negative