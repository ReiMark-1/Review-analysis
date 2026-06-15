# Movie Sentiment Analyser

A React-powered front-end and Flask back-end for analyzing TMDB movie reviews with a Naive Bayes sentiment classifier.

## Project structure

- `App.jsx` - React UI for searching movies, displaying sentiment results, and analysing custom text.
- `backend/app.py` - Flask API server that loads the trained sentiment model, fetches TMDB movie data, and returns analysis results.
- `backend/model_trainer.py` - Trains a Naive Bayes sentiment model on the NLTK `movie_reviews` corpus and saves the model to `models/sentiment_model.pkl`.
- `backend/sentiment_analyzer.py` - Loads the trained model and classifies TMDB review text.
- `backend/tmdb_api.py` - Requests movie search, details, and review data from The Movie Database (TMDB).

## Requirements

- Python 3.8+ (for backend)
- `pip` packages:
  - `flask`
  - `flask_cors`
  - `requests`
  - `python-dotenv`
  - `nltk`
  - `matplotlib`
  - `wordcloud` (optional, only for word cloud visuals)

- TMDB API key
- A React project or bundler configured to use `App.jsx` as the main application component.

## Setup

1. Install backend dependencies:

```bash
pip install flask flask_cors requests python-dotenv nltk matplotlib wordcloud
```

2. Create a `.env` file in the `backend/` folder with your TMDB API key:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

3. Train the sentiment model once before starting the server:

```bash
cd backend
python model_trainer.py
```

This will create:
- `models/sentiment_model.pkl`
- `output_visuals/model/dashboard.png`

## Running the backend

From the `backend` folder:

```bash
python app.py
```

The backend listens on port `5000` and serves the API used by `App.jsx`.

## Frontend usage

`App.jsx` is built to call the backend at `http://localhost:5000`.

If your React app is configured differently, update the `API` constant at the top of `App.jsx`.

Features:
- Search TMDB movies by title
- Select a movie to analyse its TMDB review sentiment
- View summary stats, best example reviews, and review-level sentiment details
- Analyse custom text instantly

## API endpoints

- `GET /api/health` - health check
- `GET /api/search?query=<title>` - search movies
- `GET /api/movie/<id>` - get movie details
- `GET /api/analyze/<id>` - analyse reviews for a movie
- `POST /api/analyze/text` - analyse custom review text

## Notes

- If `backend/app.py` cannot find `models/sentiment_model.pkl`, run `python model_trainer.py` first.
- `backend/tmdb_api.py` requires a valid `TMDB_API_KEY`.
- The React UI uses `axios` to call the Flask API.

## Optional enhancements

- Add a `requirements.txt` or `package.json` for dependency management.
- Add a formal React project structure around `App.jsx`.
- Add backend tests or error handling for TMDB rate limits.
