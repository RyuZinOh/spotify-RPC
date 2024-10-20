from flask import Flask, redirect, request, session, url_for, render_template
from flask_pymongo import PyMongo
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from keep_alive import keep_alive

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'https://spotify-rpc.onrender.com/callback'
SCOPE = 'user-read-currently-playing'
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'spotify_id' in session:
        return redirect(url_for('currently_playing', username=session['username']))
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    response_data = response.json()

    if 'error' in response_data:
        return f"Failed to get access token: {response_data['error_description']}"

    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')

    user_profile_url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = requests.get(user_profile_url, headers=headers)
    profile_data = profile_response.json()

    if 'error' in profile_data:
        return f"Failed to get user profile: {profile_data['error_description']}"

    spotify_id = profile_data['id']
    user_email = profile_data.get('email', 'unknown')
    profile_picture = profile_data['images'][0]['url'] if profile_data['images'] else None
    display_name = profile_data.get('display_name', 'Unknown User')

    user = mongo.db.she_knows.find_one({"spotify_id": spotify_id})
    if user is None:
        mongo.db.she_knows.insert_one({"spotify_id": spotify_id, "email": user_email, "access_token": access_token, "refresh_token": refresh_token, "profile_picture": profile_picture, "display_name": display_name})
    else:
        mongo.db.she_knows.update_one({"spotify_id": spotify_id}, {"$set": {"email": user_email, "access_token": access_token, "refresh_token": refresh_token, "profile_picture": profile_picture, "display_name": display_name}})

    session['spotify_id'] = spotify_id
    session['username'] = display_name
    return redirect(url_for('currently_playing', username=display_name))

@app.route('/currently_playing/<username>')
def currently_playing(username):
    if 'spotify_id' not in session:
        return redirect(url_for('login'))

    users = list(mongo.db.she_knows.find())
    current_user = mongo.db.she_knows.find_one({"display_name": username})
    if current_user:
        access_token = current_user['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)

        if response.status_code == 200:
            try:
                track_info = response.json()

                for user in users:
                    if user['display_name'] == username:
                        user['is_playing'] = track_info.get('is_playing', False)
                        user['track_name'] = track_info['item']['name'] if 'item' in track_info else None
                        user['artist_name'] = track_info['item']['artists'][0]['name'] if 'item' in track_info else None
                        user['track_thumbnail'] = track_info['item']['album']['images'][0]['url'] if 'item' in track_info else None
                        user['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break

                return render_template('currently_playing.html', users=users, current_user=current_user)

            except ValueError as e:
                print(f"JSON decoding error: {e}")
                print(f"Response content: {response.text}")
                return "Failed to decode JSON from Spotify API."
        
        elif response.status_code == 204:
            for user in users:
                if user['display_name'] == username:
                    user['is_playing'] = False
                    user['track_name'] = None
                    user['artist_name'] = None
                    user['track_thumbnail'] = None
                    user['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break

            return render_template('currently_playing.html', users=users, current_user=current_user)
        
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response content: {response.text}")
            return f"Error fetching data from Spotify: {response.status_code}."
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

keep_alive()
