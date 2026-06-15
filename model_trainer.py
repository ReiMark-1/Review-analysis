"""
model_trainer.py
================
Trains a Naive Bayes classifier on NLTK's movie_reviews corpus.
Saves → models/sentiment_model.pkl
Output visual → output_visuals/model/dashboard.png  (accuracy summary card)

Run ONCE before app.py:
    python model_trainer.py
"""

import os
import pickle
import random

import nltk
from nltk.corpus import movie_reviews
from nltk.classify import NaiveBayesClassifier
from nltk.classify import accuracy as nltk_accuracy
from nltk.probability import FreqDist
from nltk.metrics import ConfusionMatrix

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

for pkg in ('movie_reviews', 'stopwords', 'punkt'):
    nltk.download(pkg, quiet=True)

STOPWORDS  = set(nltk.corpus.stopwords.words('english'))
OUTPUT_DIR = os.path.join('output_visuals', 'model')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('models', exist_ok=True)


# ── Feature helpers ───────────────────────────────────────────────────────────

def get_top_words(num_words=3000):
    all_words = []
    for fid in movie_reviews.fileids():
        for w in movie_reviews.words(fid):
            w = w.lower()
            if w.isalpha() and w not in STOPWORDS and len(w) > 2:
                all_words.append(w)
    return [w for w, _ in FreqDist(all_words).most_common(num_words)]


def extract_features(word_list, top_words_set):
    present = set(w.lower() for w in word_list if w.isalpha())
    return {f'contains({w})': (w in present) for w in top_words_set}


def build_dataset(top_words):
    tws = set(top_words)
    pos = [(extract_features(movie_reviews.words(fid), tws), 'pos')
           for fid in movie_reviews.fileids('pos')]
    neg = [(extract_features(movie_reviews.words(fid), tws), 'neg')
           for fid in movie_reviews.fileids('neg')]
    dataset = pos + neg
    random.shuffle(dataset)
    return dataset


# ── Train ─────────────────────────────────────────────────────────────────────

def train(dataset):
    split      = int(len(dataset) * 0.8)
    train_set  = dataset[:split]
    test_set   = dataset[split:]
    print(f"  Training on {len(train_set)} | Testing on {len(test_set)}")
    classifier = NaiveBayesClassifier.train(train_set)
    acc        = nltk_accuracy(classifier, test_set)

    # Confusion matrix numbers (for dashboard display)
    gold   = [l for _, l in test_set]
    preds  = [classifier.classify(f) for f, _ in test_set]
    cm     = ConfusionMatrix(gold, preds)
    print(f"  ✓ Accuracy: {acc * 100:.2f}%")
    print("\n  Confusion Matrix:")
    print(cm)

    return classifier, train_set, test_set, acc


# ── Dashboard PNG ─────────────────────────────────────────────────────────────

def plot_dashboard(acc, train_size, test_size):
    """
    Single summary card showing model training results.
    This is the only visual output of model_trainer.py.
    Movie-specific visuals (wordcloud, frequency bar, etc.) are
    generated later in app.py using the actual TMDB reviews.
    """
    fig = plt.figure(figsize=(11, 5))
    fig.patch.set_facecolor('#1a1a2e')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#1a1a2e')
    ax.axis('off')

    # Title
    ax.text(0.5, 0.92,
            '🎬  Naive Bayes Sentiment Classifier — Model Training Summary',
            transform=ax.transAxes, ha='center', va='center',
            fontsize=14, fontweight='bold', color='white')

    # Divider line
    ax.axhline(y=0.80, xmin=0.05, xmax=0.95,
               color='#444466', linewidth=1, transform=ax.transAxes)

    # Stats row
    stats = [
        ('Corpus',        'NLTK movie_reviews',  '#3498db'),
        ('Total Reviews', '2,000',               '#9b59b6'),
        ('Train Set',     f'{train_size:,}',      '#f39c12'),
        ('Test Set',      f'{test_size:,}',        '#e67e22'),
        ('Accuracy',      f'{acc * 100:.2f}%',    '#2ecc71'),
        ('Algorithm',     'Naive Bayes',           '#e74c3c'),
    ]
    for i, (lbl, val, col) in enumerate(stats):
        x = 0.06 + i * 0.165
        ax.text(x, 0.55, val, transform=ax.transAxes,
                ha='center', va='center',
                fontsize=15, fontweight='bold', color=col)
        ax.text(x, 0.32, lbl, transform=ax.transAxes,
                ha='center', va='center', fontsize=9, color='#aaaaaa')

    # Footer note
    ax.text(0.5, 0.10,
            'Movie-specific visuals (word clouds, frequency bars, sentiment charts) '
            'are generated per movie when app.py runs.',
            transform=ax.transAxes, ha='center', va='center',
            fontsize=8, color='#666688', style='italic')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'dashboard.png')
    plt.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Saved → {path}")


# ── Save model ────────────────────────────────────────────────────────────────

def save_model(classifier, top_words, acc, test_set):
    path = os.path.join('models', 'sentiment_model.pkl')
    with open(path, 'wb') as f:
        pickle.dump({'classifier': classifier, 'top_words': top_words,
                     'accuracy': acc, 'test_set': test_set}, f)
    print(f"  ✓ Model saved → {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🎬  Naive Bayes Sentiment Classifier — Trainer")
    print("=" * 60)

    print("\n[1/4] Building vocabulary (top 3,000 words)…")
    top_words = get_top_words(3000)
    print(f"      Vocabulary size: {len(top_words)}")

    print("\n[2/4] Building dataset…")
    dataset = build_dataset(top_words)
    print(f"      Total examples: {len(dataset)}")

    print("\n[3/4] Training…")
    classifier, train_set, test_set, acc = train(dataset)

    print("\n[4/4] Saving dashboard + model…")
    plot_dashboard(acc, train_size=len(train_set), test_size=len(test_set))
    save_model(classifier, top_words, acc, test_set)

    print("\n" + "=" * 60)
    print(f"  ✅  Done!")
    print(f"      Visual  → output_visuals/model/dashboard.png")
    print(f"      Model   → models/sentiment_model.pkl")
    print(f"  Next step → python app.py")
    print("=" * 60 + "\n")