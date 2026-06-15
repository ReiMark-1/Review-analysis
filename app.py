"""
app.py
======
Pure Flask API server. No terminal prompts on startup.
All movie search, selection, and analysis is driven by the React frontend.

Endpoints:
  GET  /api/health
  GET  /api/search?query=<title>          ← React search bar
  GET  /api/movie/<id>                    ← movie details
  GET  /api/analyze/<id>                  ← full movie sentiment analysis
                                            also saves 4 visuals to output_visuals/
  POST /api/analyze/text                  ← single custom text from React
"""

import os
import re
import textwrap
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from sentiment_analyzer import SentimentAnalyzer
from tmdb_api import search_movie, get_movie_details, get_movie_reviews

app = Flask(__name__)
CORS(app)

# ── Load model once on startup ────────────────────────────────────────────────
try:
    analyzer = SentimentAnalyzer()
    print("✓ Sentiment analyzer loaded successfully")
except FileNotFoundError as e:
    print(f"✗ Error: {e}")
    print("Please run model_trainer.py first to train the model")
    exit(1)

STOPWORDS_VISUAL = {
    'the','and','for','that','this','with','was','but','are','have',
    'its','not','all','his','her','they','one','had','been','their',
    'from','will','more','out','than','into','who','also','about',
    'film','movie','just','even','very','like','what','when','which',
    'there','some','time','would','could','should','really','much'
}


# ════════════════════════════════════════════════════════════════════════════
# VISUAL HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _slug(title):
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')


def _words_from_reviews(review_texts):
    words = []
    for text in review_texts:
        for w in re.findall(r'[a-zA-Z]+', text.lower()):
            if len(w) > 2 and w not in STOPWORDS_VISUAL:
                words.append(w)
    return words


def plot_wordcloud(pos_texts, neg_texts, out_dir, title):
    try:
        from wordcloud import WordCloud
    except ImportError:
        print("  ⚠  wordcloud not installed — skipping (pip install wordcloud)")
        return
    pos_words = ' '.join(_words_from_reviews(pos_texts))
    neg_words = ' '.join(_words_from_reviews(neg_texts))
    if not pos_words.strip() and not neg_words.strip():
        return
    wc_pos = WordCloud(width=700, height=400, background_color='white',
                       colormap='Greens', max_words=100).generate(pos_words or 'positive')
    wc_neg = WordCloud(width=700, height=400, background_color='white',
                       colormap='Reds',   max_words=100).generate(neg_words or 'negative')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.imshow(wc_pos, interpolation='bilinear'); ax1.axis('off')
    ax1.set_title('Positive Reviews – Word Cloud', fontsize=14, fontweight='bold', color='#27ae60')
    ax2.imshow(wc_neg, interpolation='bilinear'); ax2.axis('off')
    ax2.set_title('Negative Reviews – Word Cloud', fontsize=14, fontweight='bold', color='#c0392b')
    plt.suptitle(f'Vocabulary from TMDB Reviews — {title}', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'wordcloud.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_frequency_bar(pos_texts, neg_texts, out_dir, title, n=20):
    pos_freq = Counter(_words_from_reviews(pos_texts))
    neg_freq = Counter(_words_from_reviews(neg_texts))
    top_pos  = [w for w, _ in pos_freq.most_common(n)]
    top_neg  = [w for w, _ in neg_freq.most_common(n)]
    if not top_pos and not top_neg:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    if top_pos:
        ax1.barh(top_pos[::-1], [pos_freq[w] for w in top_pos[::-1]], color='#2ecc71', edgecolor='white')
    ax1.set_title('Top Words – Positive Reviews', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Frequency')
    if top_neg:
        ax2.barh(top_neg[::-1], [neg_freq[w] for w in top_neg[::-1]], color='#e74c3c', edgecolor='white')
    ax2.set_title('Top Words – Negative Reviews', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Frequency')
    plt.suptitle(f'Word Frequency from TMDB Reviews — {title}', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'frequency_bar.png'), dpi=150)
    plt.close()


def plot_movie_sentiment(overall_stats, out_dir, title):
    pos_pct = overall_stats['positive_percentage']
    neg_pct = overall_stats['negative_percentage']
    details = overall_stats['detailed_results']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Sentiment Analysis — {title}', fontsize=15, fontweight='bold', y=1.02)
    wedges, texts, autotexts = ax1.pie(
        [pos_pct, neg_pct], labels=['Positive', 'Negative'],
        colors=['#2ecc71', '#e74c3c'], autopct='%1.1f%%',
        startangle=90, pctdistance=0.75, wedgeprops=dict(width=0.5))
    for at in autotexts:
        at.set_fontsize(13); at.set_fontweight('bold')
    ax1.set_title('Overall Sentiment Split', fontsize=12, fontweight='bold')
    overall = ('POSITIVE 😊' if pos_pct > neg_pct else ('NEGATIVE 😞' if neg_pct > pos_pct else 'NEUTRAL 😐'))
    ax1.text(0, -1.35, f'Overall: {overall}', ha='center', fontsize=13, fontweight='bold',
             color='#2ecc71' if pos_pct > neg_pct else '#e74c3c')
    x = np.arange(len(details)); w = 0.38
    ax2.bar(x - w/2, [d['positive_probability'] for d in details], w, label='Positive', color='#2ecc71', alpha=0.85)
    ax2.bar(x + w/2, [d['negative_probability'] for d in details], w, label='Negative', color='#e74c3c', alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"R{d['review_number']}" for d in details], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Probability'); ax2.set_ylim(0, 1)
    ax2.axhline(0.5, color='grey', linewidth=0.8, linestyle='--')
    ax2.legend(fontsize=10)
    ax2.set_title('Per-Review Sentiment Probabilities', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'movie_sentiment.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_reviews_detail(overall_stats, out_dir, title):
    details = overall_stats['detailed_results']
    fig, ax = plt.subplots(figsize=(max(10, len(details) * 1.4), 4))
    fig.patch.set_facecolor('#f9f9f9'); ax.set_facecolor('#f9f9f9')
    for i, d in enumerate(details):
        col = '#2ecc71' if d['sentiment'] == 'positive' else '#e74c3c'
        ax.bar(i, d['confidence'], color=col, edgecolor='white', width=0.7)
        ax.text(i, d['confidence'] + 0.02, f"{d['confidence']*100:.0f}%",
                ha='center', va='bottom', fontsize=8, fontweight='bold')
        snippet = textwrap.shorten(d['review_text'], width=30, placeholder='…')
        ax.text(i, -0.08, snippet, ha='center', va='top', fontsize=6, rotation=30, color='#333')
    ax.set_ylim(0, 1.15); ax.set_xlim(-0.6, len(details) - 0.4)
    ax.set_xticks(range(len(details)))
    ax.set_xticklabels([f"R{d['review_number']}" for d in details], fontsize=9)
    ax.set_ylabel('Confidence', fontsize=11)
    ax.set_title(f'Per-Review Confidence — {title}', fontsize=13, fontweight='bold')
    ax.legend(handles=[mpatches.Patch(color='#2ecc71', label='Positive'),
                       mpatches.Patch(color='#e74c3c', label='Negative')], loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'reviews_detail.png'), dpi=150, bbox_inches='tight')
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# FLASK ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})


@app.route('/api/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    try:
        results = search_movie(query)
        return jsonify({'results': results[:10], 'total': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_route(movie_id):
    try:
        return jsonify(get_movie_details(movie_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/<int:movie_id>', methods=['GET'])
def analyze_movie_route(movie_id):
    """
    Full movie analysis triggered by the React frontend when a movie is selected.
    Fetches TMDB reviews, runs Naive Bayes on each, saves 4 PNGs, returns JSON.
    """
    try:
        movie        = get_movie_details(movie_id)
        reviews_data = get_movie_reviews(movie_id)

        print(f"\n{'='*60}")
        print(f"  🎬  Analysing: {movie.get('title')}")
        print(f"  📊  Found {len(reviews_data)} reviews from TMDB")
        print(f"{'='*60}")

        if not reviews_data:
            return jsonify({
                'success': False,
                'movie': {
                    'id': movie['id'], 'title': movie['title'],
                    'poster_path': movie.get('poster_path'),
                    'rating': movie.get('vote_average'),
                    'vote_count': movie.get('vote_count'),
                },
                'message': 'No reviews available for this movie on TMDB.',
            })

        # ── Run sentiment analysis on TMDB review content ─────────────────
        best_positive, best_negative = analyzer.find_positive_and_negative_examples(reviews_data)
        review_texts  = [r['content'] for r in reviews_data if r.get('content')]
        overall_stats = analyzer.analyze_batch(review_texts)

        pos_pct = overall_stats['positive_percentage']
        neg_pct = overall_stats['negative_percentage']
        overall_sentiment = ('POSITIVE' if pos_pct > neg_pct else
                             ('NEGATIVE' if neg_pct > pos_pct else 'NEUTRAL'))

        print(f"  😊 Positive: {overall_stats['positive_count']} ({pos_pct}%)")
        print(f"  😞 Negative: {overall_stats['negative_count']} ({neg_pct}%)")
        print(f"  → Overall: {overall_sentiment}\n")

        # ── Save 4 visuals using the TMDB review text ─────────────────────
        out_dir = os.path.join('output_visuals', _slug(movie['title']))
        os.makedirs(out_dir, exist_ok=True)

        details   = overall_stats['detailed_results']
        pos_texts = [d['review_text'] for d in details if d['sentiment'] == 'positive']
        neg_texts = [d['review_text'] for d in details if d['sentiment'] == 'negative']

        plot_wordcloud(pos_texts, neg_texts, out_dir, movie['title'])
        plot_frequency_bar(pos_texts, neg_texts, out_dir, movie['title'])
        plot_movie_sentiment(overall_stats, out_dir, movie['title'])
        plot_reviews_detail(overall_stats, out_dir, movie['title'])
        print(f"  ✓ Visuals saved → {out_dir}/")

        return jsonify({
            'success': True,
            'movie': {
                'id':           movie['id'],
                'title':        movie['title'],
                'poster_path':  movie.get('poster_path'),
                'rating':       movie.get('vote_average'),
                'vote_count':   movie.get('vote_count'),
                'release_date': movie.get('release_date'),
                'overview':     movie.get('overview'),
            },
            'sentiment_summary': {
                'total_reviews_analyzed': overall_stats['total_reviews'],
                'positive_count':         overall_stats['positive_count'],
                'negative_count':         overall_stats['negative_count'],
                'positive_percentage':    pos_pct,
                'negative_percentage':    neg_pct,
                'average_confidence':     overall_stats['average_confidence'],
                'overall_sentiment':      overall_sentiment,
                'detailed_results':       overall_stats['detailed_results'],
            },
            'example_positive_review': best_positive or {'message': 'No positive reviews found', 'content': None},
            'example_negative_review': best_negative or {'message': 'No negative reviews found', 'content': None},
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/text', methods=['POST'])
def analyze_custom_text():
    """Single custom text entry from the React frontend."""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'text field required'}), 400
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'text cannot be empty'}), 400
    result = analyzer.analyze_single(text)
    return jsonify({
        'sentiment':            result['sentiment'],
        'score':                result['confidence'],
        'positive_probability': result['positive_probability'],
        'negative_probability': result['negative_probability'],
    })


# ════════════════════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🚀  Movie Sentiment Analyser — Flask API")
    print("=" * 60)
    print("  No terminal prompts — use the React frontend to search movies.")
    print("\n  Endpoints:")
    print("    GET  /api/health")
    print("    GET  /api/search?query=<title>")
    print("    GET  /api/movie/<id>")
    print("    GET  /api/analyze/<id>")
    print("    POST /api/analyze/text")
    print("\n  Frontend → http://localhost:5173  (or wherever Vite runs)")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)