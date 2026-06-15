import { useState, useRef } from 'react';
import axios from 'axios';

const API = 'http://localhost:5000';

/* ─── Styles ──────────────────────────────────────────────────────────────── */
const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #09090e;
    --surface:  #111118;
    --card:     #16161f;
    --border:   #252535;
    --pos:      #22c55e;
    --neg:      #ef4444;
    --accent:   #818cf8;
    --text:     #e4e4f0;
    --muted:    #5a5a78;
    --subtle:   #2a2a40;
  }

  html, body, #root {
    height: 100%; background: var(--bg);
    color: var(--text); font-family: 'DM Sans', sans-serif;
  }

  /* Layout */
  .shell { display: flex; height: 100vh; overflow: hidden; }

  .sidebar {
    width: 340px; flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column;
    overflow: hidden;
  }

  .main {
    flex: 1; overflow-y: auto;
    padding: 40px 48px;
  }

  /* Sidebar header */
  .sb-header {
    padding: 28px 24px 20px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .sb-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 26px; letter-spacing: 0.06em;
    color: var(--text); margin-bottom: 14px;
  }
  .sb-title span { color: var(--accent); }

  /* Search */
  .search-wrap { position: relative; }
  .search-input {
    width: 100%; background: var(--card);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 38px 10px 14px;
    font-family: 'DM Sans', sans-serif; font-size: 14px;
    color: var(--text); outline: none;
    transition: border-color 0.15s;
  }
  .search-input::placeholder { color: var(--muted); }
  .search-input:focus { border-color: var(--accent); }
  .search-btn {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    background: none; border: none; cursor: pointer;
    color: var(--muted); font-size: 16px; padding: 2px;
    transition: color 0.15s;
  }
  .search-btn:hover { color: var(--accent); }

  /* Results list */
  .results-list {
    flex: 1; overflow-y: auto; padding: 8px 0;
  }
  .results-list::-webkit-scrollbar { width: 4px; }
  .results-list::-webkit-scrollbar-thumb { background: var(--subtle); border-radius: 2px; }

  .result-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 24px; cursor: pointer;
    transition: background 0.12s; border-left: 3px solid transparent;
  }
  .result-item:hover { background: var(--card); }
  .result-item.active {
    background: var(--card);
    border-left-color: var(--accent);
  }
  .result-poster {
    width: 36px; height: 54px; object-fit: cover;
    border-radius: 4px; background: var(--subtle); flex-shrink: 0;
  }
  .result-poster-placeholder {
    width: 36px; height: 54px; border-radius: 4px;
    background: var(--subtle); flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .result-info { min-width: 0; }
  .result-name {
    font-size: 13px; font-weight: 500; color: var(--text);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .result-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }

  .sb-empty {
    padding: 32px 24px; text-align: center;
    font-size: 13px; color: var(--muted); line-height: 1.6;
  }
  .sb-spinner {
    padding: 24px; display: flex; justify-content: center;
  }

  /* Main header */
  .main-header { margin-bottom: 36px; }
  .eyebrow {
    font-size: 11px; font-weight: 500; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 10px;
  }
  .main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(44px, 6vw, 68px);
    line-height: 0.9; letter-spacing: 0.03em; color: var(--text);
  }
  .main-title span { color: var(--accent); }
  .main-sub {
    margin-top: 14px; font-size: 14px; font-weight: 300;
    color: var(--muted); line-height: 1.6; max-width: 480px;
  }

  /* Movie hero */
  .movie-hero {
    display: flex; gap: 28px; align-items: flex-start;
    margin-bottom: 32px;
    animation: fadeUp 0.3s ease both;
  }
  .movie-poster {
    width: 110px; height: 165px; object-fit: cover;
    border-radius: 10px; flex-shrink: 0;
    background: var(--subtle);
  }
  .movie-poster-ph {
    width: 110px; height: 165px; border-radius: 10px;
    background: var(--subtle); flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 40px;
  }
  .movie-info { flex: 1; padding-top: 4px; }
  .movie-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px; letter-spacing: 0.04em; line-height: 1;
    color: var(--text); margin-bottom: 6px;
  }
  .movie-meta-row {
    display: flex; flex-wrap: wrap; gap: 12px;
    font-size: 12px; color: var(--muted); margin-bottom: 12px;
  }
  .movie-meta-row span { display: flex; align-items: center; gap: 4px; }
  .movie-overview {
    font-size: 13px; font-weight: 300; color: var(--muted);
    line-height: 1.65; max-width: 520px;
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden;
  }

  /* Loading */
  .loading-bar {
    height: 3px; background: var(--border); border-radius: 99px;
    overflow: hidden; margin-bottom: 28px;
  }
  .loading-bar-fill {
    height: 100%; width: 40%;
    background: var(--accent); border-radius: 99px;
    animation: slide 1.2s ease-in-out infinite;
  }
  @keyframes slide {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(350%); }
  }

  /* Stats grid */
  .stats-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 28px;
    animation: fadeUp 0.35s ease 0.05s both;
  }
  .stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px 18px;
  }
  .stat-label {
    font-size: 10px; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 6px;
  }
  .stat-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px; letter-spacing: 0.04em; line-height: 1;
  }
  .stat-val.pos { color: var(--pos); }
  .stat-val.neg { color: var(--neg); }
  .stat-val.neutral { color: var(--accent); }
  .stat-val.plain { color: var(--text); }

  /* Sentiment bar */
  .sentiment-bar-wrap {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px 22px;
    margin-bottom: 28px;
    animation: fadeUp 0.35s ease 0.1s both;
  }
  .bar-label-row {
    display: flex; justify-content: space-between;
    font-size: 12px; color: var(--muted); margin-bottom: 10px;
  }
  .bar-track {
    height: 8px; background: var(--border); border-radius: 99px; overflow: hidden;
    display: flex;
  }
  .bar-pos {
    height: 100%; background: var(--pos); border-radius: 99px 0 0 99px;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
  }
  .bar-neg {
    height: 100%; background: var(--neg); border-radius: 0 99px 99px 0;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
  }

  /* Reviews */
  .section-title {
    font-size: 11px; font-weight: 500; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 14px;
  }
  .reviews-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 14px; margin-bottom: 28px;
    animation: fadeUp 0.35s ease 0.15s both;
  }
  .review-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px; overflow: hidden;
  }
  .review-card.pos-card { border-top: 2px solid var(--pos); }
  .review-card.neg-card { border-top: 2px solid var(--neg); }
  .review-tag {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 10px; font-weight: 500; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 3px 8px;
    border-radius: 4px; margin-bottom: 10px;
  }
  .review-tag.pos { background: rgba(34,197,94,0.12); color: var(--pos); }
  .review-tag.neg { background: rgba(239,68,68,0.12);  color: var(--neg); }
  .review-author { font-size: 12px; color: var(--muted); margin-bottom: 8px; }
  .review-text {
    font-size: 13px; font-weight: 300; line-height: 1.65;
    color: var(--text); opacity: 0.85;
    display: -webkit-box; -webkit-line-clamp: 5;
    -webkit-box-orient: vertical; overflow: hidden;
  }
  .review-conf {
    margin-top: 10px; font-size: 11px; color: var(--muted);
  }

  /* Per-review list */
  .detail-list {
    display: flex; flex-direction: column; gap: 8px;
    margin-bottom: 28px;
    animation: fadeUp 0.35s ease 0.2s both;
  }
  .detail-row {
    display: flex; align-items: center; gap: 12px;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 10px 14px;
  }
  .detail-num {
    font-size: 11px; color: var(--muted); width: 22px; flex-shrink: 0;
  }
  .detail-badge {
    font-size: 10px; font-weight: 500; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 2px 7px; border-radius: 4px;
    flex-shrink: 0; width: 64px; text-align: center;
  }
  .detail-badge.pos { background: rgba(34,197,94,0.12); color: var(--pos); }
  .detail-badge.neg { background: rgba(239,68,68,0.12);  color: var(--neg); }
  .detail-track {
    flex: 1; height: 4px; background: var(--border); border-radius: 99px; overflow: hidden;
  }
  .detail-fill {
    height: 100%; border-radius: 99px;
    transition: width 0.6s cubic-bezier(0.16,1,0.3,1);
  }
  .detail-fill.pos { background: var(--pos); }
  .detail-fill.neg { background: var(--neg); }
  .detail-pct { font-size: 12px; color: var(--text); width: 38px; text-align: right; flex-shrink: 0; }
  .detail-snippet {
    font-size: 11px; color: var(--muted); flex: 1.5;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }

  /* Custom text */
  .custom-section {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 22px;
    margin-bottom: 28px;
    animation: fadeUp 0.35s ease 0.25s both;
  }
  .custom-textarea {
    width: 100%; background: var(--bg);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 12px 14px; font-family: 'DM Sans', sans-serif;
    font-size: 14px; font-weight: 300; color: var(--text);
    resize: vertical; min-height: 90px; outline: none;
    transition: border-color 0.15s; margin-bottom: 12px;
  }
  .custom-textarea::placeholder { color: var(--muted); }
  .custom-textarea:focus { border-color: var(--accent); }
  .custom-row { display: flex; justify-content: space-between; align-items: center; }
  .custom-result {
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  }
  .custom-badge {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px; letter-spacing: 0.06em;
  }
  .custom-badge.pos { color: var(--pos); }
  .custom-badge.neg { color: var(--neg); }
  .custom-score { font-size: 12px; color: var(--muted); }

  /* Buttons */
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--accent); color: #fff;
    border: none; border-radius: 8px;
    padding: 9px 20px; font-family: 'DM Sans', sans-serif;
    font-size: 13px; font-weight: 500;
    cursor: pointer; transition: opacity 0.15s, transform 0.15s;
    white-space: nowrap;
  }
  .btn:hover:not(:disabled) { opacity: 0.85; transform: translateY(-1px); }
  .btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }
  .btn-sm { padding: 7px 14px; font-size: 12px; }

  /* Spinner */
  .spinner {
    width: 13px; height: 13px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.25);
    border-top-color: #fff;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Error */
  .err-box {
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px; padding: 12px 16px;
    font-size: 13px; color: #f87171; margin-bottom: 20px;
  }

  /* Idle screen */
  .idle {
    display: flex; flex-direction: column;
    align-items: flex-start; justify-content: center;
    min-height: 60vh;
  }
  .idle-hint {
    font-size: 14px; font-weight: 300; color: var(--muted);
    line-height: 1.7; margin-top: 20px; max-width: 400px;
  }
  .idle-hint strong { color: var(--text); font-weight: 500; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* Scrollbar */
  .main::-webkit-scrollbar { width: 5px; }
  .main::-webkit-scrollbar-thumb { background: var(--subtle); border-radius: 2px; }
`;

/* ─── Helpers ─────────────────────────────────────────────────────────────── */
const IMG = (path) =>
  path ? `https://image.tmdb.org/t/p/w185${path}` : null;

const truncate = (str, n) =>
  str && str.length > n ? str.slice(0, n) + '…' : str;

/* ─── Spinner ─────────────────────────────────────────────────────────────── */
const Spin = () => <span className="spinner" />;

/* ─── App ─────────────────────────────────────────────────────────────────── */
export default function App() {
  const [query,          setQuery]          = useState('');
  const [searchResults,  setSearchResults]  = useState([]);
  const [searching,      setSearching]      = useState(false);

  const [selectedMovie,  setSelectedMovie]  = useState(null);
  const [analysisData,   setAnalysisData]   = useState(null);
  const [analysing,      setAnalysing]      = useState(false);
  const [error,          setError]          = useState(null);

  const [customText,     setCustomText]     = useState('');
  const [customResult,   setCustomResult]   = useState(null);
  const [customLoading,  setCustomLoading]  = useState(false);

  const searchRef = useRef();

  /* Search TMDB */
  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setError(null);
    try {
      const { data } = await axios.get(`${API}/api/search`, { params: { query } });
      setSearchResults(data.results || []);
    } catch {
      setError('Search failed. Is the Flask server running?');
    } finally {
      setSearching(false);
    }
  };

  const handleSearchKey = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  /* Select movie → trigger analysis */
  const handleSelectMovie = async (movie) => {
    setSelectedMovie(movie);
    setAnalysisData(null);
    setAnalysing(true);
    setError(null);
    setCustomResult(null);
    try {
      const { data } = await axios.get(`${API}/api/analyze/${movie.id}`);
      if (!data.success) {
        setError(data.message || 'No reviews found for this movie.');
      } else {
        setAnalysisData(data);
      }
    } catch (e) {
      setError(e.response?.data?.error || 'Analysis failed.');
    } finally {
      setAnalysing(false);
    }
  };

  /* Custom text analysis */
  const handleCustomAnalyze = async () => {
    if (!customText.trim()) return;
    setCustomLoading(true);
    setCustomResult(null);
    try {
      const { data } = await axios.post(`${API}/api/analyze/text`, { text: customText });
      setCustomResult(data);
    } catch {
      setCustomResult({ error: 'Analysis failed.' });
    } finally {
      setCustomLoading(false);
    }
  };

  const summary  = analysisData?.sentiment_summary;
  const bestPos  = analysisData?.example_positive_review;
  const bestNeg  = analysisData?.example_negative_review;
  const details  = summary?.detailed_results || [];
  const isPos    = summary?.overall_sentiment === 'POSITIVE';
  const isNeg    = summary?.overall_sentiment === 'NEGATIVE';

  return (
    <>
      <style>{STYLES}</style>
      <div className="shell">

        {/* ── Sidebar ─────────────────────────────────────────────────── */}
        <aside className="sidebar">
          <div className="sb-header">
            <div className="sb-title">🎬 Sentiment<br /><span>Analyser</span></div>
            <div className="search-wrap">
              <input
                ref={searchRef}
                className="search-input"
                placeholder="Search a movie…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleSearchKey}
              />
              <button className="search-btn" onClick={handleSearch}>
                {searching ? <Spin /> : '↵'}
              </button>
            </div>
          </div>

          <div className="results-list">
            {searching && (
              <div className="sb-spinner"><Spin /></div>
            )}
            {!searching && searchResults.length === 0 && (
              <div className="sb-empty">
                Search for a movie above to get started.
              </div>
            )}
            {!searching && searchResults.map((m) => (
              <div
                key={m.id}
                className={`result-item ${selectedMovie?.id === m.id ? 'active' : ''}`}
                onClick={() => handleSelectMovie(m)}
              >
                {IMG(m.poster_path)
                  ? <img className="result-poster" src={IMG(m.poster_path)} alt={m.title} />
                  : <div className="result-poster-placeholder">🎞</div>
                }
                <div className="result-info">
                  <div className="result-name">{m.title}</div>
                  <div className="result-meta">
                    {(m.release_date || '').slice(0, 4)}
                    {m.vote_average ? ` · ⭐ ${m.vote_average.toFixed(1)}` : ''}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* ── Main ────────────────────────────────────────────────────── */}
        <main className="main">

          {/* No movie selected yet */}
          {!selectedMovie && !analysing && (
            <div className="idle">
              <p className="eyebrow">Naive Bayes · TMDB Reviews</p>
              <h1 className="main-title">Movie<br /><span>Sentiment</span></h1>
              <p className="idle-hint">
                <strong>Search for a movie</strong> in the sidebar, then select it
                to run a full Naive Bayes sentiment analysis on its TMDB reviews.
                <br /><br />
                You can also type your own review below and analyse it instantly.
              </p>
            </div>
          )}

          {/* Loading */}
          {analysing && (
            <>
              <div className="loading-bar"><div className="loading-bar-fill" /></div>
              <p style={{ fontSize: 14, color: 'var(--muted)' }}>
                Fetching reviews and running sentiment analysis…
              </p>
            </>
          )}

          {/* Error */}
          {error && <div className="err-box">⚠ {error}</div>}

          {/* Movie hero + results */}
          {!analysing && selectedMovie && (
            <>
              {/* Movie info */}
              <div className="movie-hero">
                {IMG(analysisData?.movie?.poster_path || selectedMovie.poster_path)
                  ? <img className="movie-poster"
                      src={IMG(analysisData?.movie?.poster_path || selectedMovie.poster_path)}
                      alt={selectedMovie.title} />
                  : <div className="movie-poster-ph">🎞</div>
                }
                <div className="movie-info">
                  <div className="movie-title">{selectedMovie.title}</div>
                  <div className="movie-meta-row">
                    {(selectedMovie.release_date || '').slice(0,4) && (
                      <span>📅 {selectedMovie.release_date.slice(0,4)}</span>
                    )}
                    {selectedMovie.vote_average && (
                      <span>⭐ {selectedMovie.vote_average.toFixed(1)}</span>
                    )}
                    {summary && (
                      <span>💬 {summary.total_reviews_analyzed} reviews analysed</span>
                    )}
                  </div>
                  {(analysisData?.movie?.overview || selectedMovie.overview) && (
                    <p className="movie-overview">
                      {analysisData?.movie?.overview || selectedMovie.overview}
                    </p>
                  )}
                </div>
              </div>

              {/* Stats */}
              {summary && (
                <>
                  <div className="stats-grid">
                    <div className="stat-card">
                      <div className="stat-label">Overall</div>
                      <div className={`stat-val ${isPos ? 'pos' : isNeg ? 'neg' : 'neutral'}`}>
                        {summary.overall_sentiment}
                      </div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-label">Positive</div>
                      <div className="stat-val pos">{summary.positive_percentage}%</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-label">Negative</div>
                      <div className="stat-val neg">{summary.negative_percentage}%</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-label">Avg Confidence</div>
                      <div className="stat-val plain">
                        {(summary.average_confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  {/* Sentiment bar */}
                  <div className="sentiment-bar-wrap">
                    <div className="bar-label-row">
                      <span>😊 Positive — {summary.positive_count} reviews</span>
                      <span>😞 Negative — {summary.negative_count} reviews</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-pos" style={{ width: `${summary.positive_percentage}%` }} />
                      <div className="bar-neg" style={{ width: `${summary.negative_percentage}%` }} />
                    </div>
                  </div>

                  {/* Best examples */}
                  {(bestPos?.content || bestNeg?.content) && (
                    <>
                      <p className="section-title">Best examples</p>
                      <div className="reviews-grid">
                        {bestPos?.content && (
                          <div className="review-card pos-card">
                            <span className="review-tag pos">✓ Positive</span>
                            <div className="review-author">— {bestPos.author}</div>
                            <div className="review-text">{bestPos.content}</div>
                            <div className="review-conf">
                              Confidence: {(bestPos.confidence * 100).toFixed(1)}%
                            </div>
                          </div>
                        )}
                        {bestNeg?.content && (
                          <div className="review-card neg-card">
                            <span className="review-tag neg">✗ Negative</span>
                            <div className="review-author">— {bestNeg.author}</div>
                            <div className="review-text">{bestNeg.content}</div>
                            <div className="review-conf">
                              Confidence: {(bestNeg.confidence * 100).toFixed(1)}%
                            </div>
                          </div>
                        )}
                      </div>
                    </>
                  )}

                  {/* Per-review detail */}
                  {details.length > 0 && (
                    <>
                      <p className="section-title">All reviews</p>
                      <div className="detail-list">
                        {details.map((d) => (
                          <div key={d.review_number} className="detail-row">
                            <span className="detail-num">#{d.review_number}</span>
                            <span className={`detail-badge ${d.sentiment === 'positive' ? 'pos' : 'neg'}`}>
                              {d.sentiment}
                            </span>
                            <div className="detail-track">
                              <div
                                className={`detail-fill ${d.sentiment === 'positive' ? 'pos' : 'neg'}`}
                                style={{ width: `${d.confidence * 100}%` }}
                              />
                            </div>
                            <span className="detail-pct">{(d.confidence * 100).toFixed(0)}%</span>
                            <span className="detail-snippet">{truncate(d.review_text, 60)}</span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </>
              )}
            </>
          )}

          {/* Custom text analysis — always visible */}
          <div className="custom-section">
            <p className="section-title" style={{ marginBottom: 12 }}>
              Analyse custom text
            </p>
            <textarea
              className="custom-textarea"
              placeholder="Type or paste any review text to analyse it instantly…"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
            />
            <div className="custom-row">
              <div className="custom-result">
                {customResult && !customResult.error && (
                  <>
                    <span className={`custom-badge ${customResult.sentiment === 'positive' ? 'pos' : 'neg'}`}>
                      {customResult.sentiment === 'positive' ? 'POSITIVE' : 'NEGATIVE'}
                    </span>
                    <span className="custom-score">
                      {customResult.sentiment === 'positive' ? '😊' : '😞'}&nbsp;
                      Score: {(customResult.score * 100).toFixed(1)}%
                      &nbsp;·&nbsp;
                      Pos {(customResult.positive_probability * 100).toFixed(0)}%
                      &nbsp;/&nbsp;
                      Neg {(customResult.negative_probability * 100).toFixed(0)}%
                    </span>
                  </>
                )}
                {customResult?.error && (
                  <span style={{ fontSize: 13, color: '#f87171' }}>{customResult.error}</span>
                )}
              </div>
              <button
                className="btn btn-sm"
                onClick={handleCustomAnalyze}
                disabled={customLoading || !customText.trim()}
              >
                {customLoading ? <><Spin /> Analysing…</> : '→ Analyse'}
              </button>
            </div>
          </div>

        </main>
      </div>
    </>
  );
}