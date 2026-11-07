import streamlit as st
import pickle
import pandas as pd
import requests

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=(10, 30))
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    
    except requests.exceptions.Timeout:
        print(f"TMDB timeout for movie ID: {movie_id}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"TMDB API error: {e}")
        return None


def recommend(movie):
    movie_index = int(movies[movies['title'] == movie].index[0])
    distances = similarity[movie_index]
    movies_list = sorted([(i, float(score)) for i, score in enumerate(distances)], 
                key=lambda x: x[1], reverse=True)[1:6]    
    
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # Fetch Poster from API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title("Movie Recommendation System")

selected_movie_name = st.selectbox(
    "Choose a movie you like:",
    movies['title'].values
)


if st.button("Recommend", type="primary"):
    names, posters = recommend(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    for i, col in enumerate(columns):
        with col:
            st.text(names[i])
            
            if posters[i] is not None:
                st.image(posters[i])
            else:
                st.write("Poster not available")
                