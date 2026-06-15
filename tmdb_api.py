# tmdb_api.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_movie(query):
    """Search for a movie by title"""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'language': 'en-US',
        'page': 1
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get('results'):
        return data['results']
    return []

def get_movie_details(movie_id):
    """Get detailed information about a movie"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_movie_reviews(movie_id):
    """Get ALL review data for a movie from TMDB"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/reviews"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    reviews_data = []
    if data.get('results'):
        for review in data['results']:
            reviews_data.append({
                'author': review.get('author'),
                'content': review.get('content'),
                'rating': review.get('author_details', {}).get('rating'),
                'created_at': review.get('created_at')
            })
    
    return reviews_data