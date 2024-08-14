from flask import Flask, request, redirect, url_for, session, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = 'hehehehenhibataungasecretkeyhahahaha'

from dotenv import load_dotenv
load_dotenv()


sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope='playlist-modify-public'
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    mood = request.form.get('mood')
    if not mood:
        return "Please provide a mood", 400

    mood_to_genre = {
        "happy": "pop",
        "sad": "blues",
        "energetic": "rock",
        "calm": "classical",
        "relaxed": "chillout",
        "motivated": "motivational rock",
        "romantic": "love songs",
        "angry": "heavy metal",
        "focused": "instrumental",
        "nostalgic": "classic rock",
        "adventurous": "world music",
        "melancholic": "dark indie",
        "joyful": "uplifting pop",
        "dreamy": "dream pop",
        "productive": "lo-fi beats",
        "sleepy": "ambient",
        "reflective": "singer-songwriter",
        "festive": "holiday music",
        "tense": "tension music",
        "excited": "high-energy pop",
        "inspired": "indie folk",
        "serene": "new age",
        "heartbroken": "soul",
        "confident": "hip-hop",
        "curious": "experimental",
        "spiritual": "gospel",
        "rebellious": "punk rock",
        "playful": "pop punk"
    }

    genre = mood_to_genre.get(mood.lower(), "pop")

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.search(q=f'genre:{genre}', type='track', limit=20)
    tracks = [{
        'name': track['name'],
        'artist': ', '.join([artist['name'] for artist in track['artists']]),
        'album_image': track['album']['images'][0]['url'],
        'url': track['external_urls']['spotify']
    } for track in results['tracks']['items']]

    # Create a new playlist in your Spotify account
    user_id = sp.current_user()['id']
    playlist_name = f"{mood.capitalize()} Mood Playlist"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name)
    sp.playlist_add_items(playlist_id=playlist['id'], items=[track['uri'] for track in results['tracks']['items']])

    playlist_url = playlist['external_urls']['spotify']
    return render_template('playlist.html', playlist_name=playlist_name, playlist_url=playlist_url, tracks=tracks)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
