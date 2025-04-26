from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime, time, timedelta
import pytz, os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
load_dotenv()

@app.after_request
def add_header(res):
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    return res

current_page = "home"

# --- Mirror Routes ---
@app.route('/mirror')
def mirror():
    return render_template('mirror.html')

@app.route('/current_page')
def get_current_page():
    return jsonify({"page": current_page})

@app.route('/set_page', methods=['POST'])
def set_current_page():
    global current_page
    data = request.get_json()
    page = data.get('page', 'home')
    current_page = page
    return jsonify({"status": "success", "current_page": current_page})

# --- UI Pages ---
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/spotify')
def spotify_page():
    return render_template('spotify.html')

@app.route('/remote')
def remote():
    return render_template('remote.html')

@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html')

# --- Spotify Backend ---
@app.route('/spotify_data')
def get_spotify_info():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='.spotify_token.json'
    )

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        return redirect(sp_oauth.get_authorize_url())

    sp = Spotify(auth_manager=sp_oauth)
    song = sp.current_playback()

    if song and song.get('item'):
        track = song.get('item', {})
        album = track.get('album', {})
        artist_list = track.get('artists', [])
        return jsonify({
            'name': track.get('name'),
            'artist': artist_list[0]['name'] if artist_list else 'N/A',
            'album': album.get('name'),
            'album_cover': album.get('images')[0]['url'] if album.get('images') else '',
            'device': song.get('device', {}).get('name'),
            'duration_ms': track.get('duration_ms', 0),
            'progress_ms': song.get('progress_ms', 0)
        })

    return jsonify({
        'name': 'N/A', 'artist': 'N/A', 'album': 'N/A',
        'album_cover': '', 'device': 'N/A'
    })

@app.route('/spotify_login')
def spotify_login():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='.spotify_token.json'
    )
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def spotify_callback():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='.spotify_token.json'
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    return redirect('/spotify') if token_info else "Authorization failed."

# --- Calendar Backend ---
@app.route('/calendar_data')
def get_calendar_events():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    today = now.date()
    
    # crude "next month" trick
    one_month_later = today.replace(day=28) + timedelta(days=10)
    one_month_later = one_month_later.replace(day=1)

    start_today = tz.localize(datetime.combine(today, time.min)).isoformat()
    end_today = tz.localize(datetime.combine(today, time.max)).isoformat()
    start_future = tz.localize(datetime.combine(today + timedelta(days=1), time.min)).isoformat()
    end_future = tz.localize(datetime.combine(one_month_later, time.max)).isoformat()

    today_events = []
    upcoming_events = []

    # ✅ Classes calendar (only shows in Today's Events)
    classes_result = service.events().list(
        calendarId='f68d2ac45e9ac7aba185ad08cc6d511542196634c495bca2cff141cf13e8e22f@group.calendar.google.com',
        timeMin=start_today,
        timeMax=end_today,
        timeZone='America/New_York',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for e in classes_result.get('items', []):
        raw_start = e['start'].get('dateTime', e['start'].get('date'))
        dt = datetime.fromisoformat(raw_start.replace('Z', '')).astimezone(tz)
        pretty = dt.strftime('%I:%M %p')
        summary = e.get('summary', 'No Title')
        today_events.append({'start': pretty, 'summary': summary})

    # ✅ "Daniel Kim" (now "Other") calendar — for Upcoming Events
    daniel_result = service.events().list(
        calendarId='9cf36c61af86479abe999f348c513dcdc1a190a54b22038fbba2f274401c8261@group.calendar.google.com',
        timeMin=start_future,
        timeMax=end_future,
        timeZone='America/New_York',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for e in daniel_result.get('items', []):
        raw_start = e['start'].get('dateTime', e['start'].get('date'))
        dt = datetime.fromisoformat(raw_start.replace('Z', '')).astimezone(tz)
        date_label = dt.strftime('%A, %B %d')
        time_label = dt.strftime('%I:%M %p')
        summary = e.get('summary', 'No Title')
        upcoming_events.append({'date': date_label, 'start': time_label, 'summary': summary})

    return jsonify({'today': today_events, 'upcoming': upcoming_events})


# --- Start Server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
