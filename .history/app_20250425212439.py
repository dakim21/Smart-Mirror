from flask import Flask, render_template, jsonify, request, redirect
import time
from datetime import datetime, time as dt_time, timedelta, date
import pytz, os
import requests
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

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

@app.route('/stocks')
def stocks():
    return render_template('stock_chart.html')

@app.route('/sports')
def sports():
    return render_template('sports.html')

# --- Stocks Data Backend ---
cached_stock_data = None
cached_stock_time = 0
STOCK_CACHE_TTL = 600  # seconds (10 minutes)

@app.route('/stocks_data')
def stocks_data():
    global cached_stock_data, cached_stock_time

    now = time.time()
    if cached_stock_data and (now - cached_stock_time) < STOCK_CACHE_TTL:
        print("✅ Returning cached stock data")
        return jsonify(cached_stock_data)

    API_KEY = "A79E9AHKRPHVZROI"
    STOCK_SYMBOLS = ['GOOGL', 'NVDA', 'INTC', 'NXPI']

    result = {}

    for symbol in STOCK_SYMBOLS:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
        print(f"Fetching {symbol}: {url}")
        r = requests.get(url)
        data = r.json()

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            print(f"No time series data for {symbol}")
            result[symbol] = {"labels": [], "prices": []}
            continue

        dates = sorted(time_series.keys(), reverse=True)[:5]

        labels = []
        prices = []

        for date_ in sorted(dates):
            if date_ not in time_series:
                continue
            close_price = float(time_series[date_]["4. close"])
            month, day = date_.split("-")[1:]
            labels.append(f"{int(month)}/{int(day)}")
            prices.append(close_price)

        result[symbol] = {
            "labels": labels,
            "prices": prices
        }

    cached_stock_data = result
    cached_stock_time = now
    print("✅ Stock data updated and cached")
    return jsonify(result)

# --- Sports Backend ---
cached_sports_data = None
cached_sports_time = 0
SPORTS_CACHE_TTL = 600  # seconds (10 minutes)

@app.route('/sports_data')
def sports_data():
    global cached_sports_data, cached_sports_time

    now = time.time()
    if cached_sports_data and (now - cached_sports_time) < SPORTS_CACHE_TTL:
        print("✅ Returning cached sports data")
        return jsonify(cached_sports_data)

    API_KEY = "PoeGaPJk98jwRXxUCxzL1BkR4Fg94PYlk6lIhuYb"
    tz = pytz.timezone("US/Eastern")
    today = date.today()
    year, month, day = today.year, today.month, today.day

    games_url = f"https://api.sportradar.com/mlb/trial/v8/en/games/{year}/{month:02}/{day:02}/schedule.json?api_key={API_KEY}"
    standings_url = f"https://api.sportradar.com/mlb/trial/v8/en/seasons/{year}/REG/standings.json?api_key={API_KEY}"

    games = []
    divisions = []

    try:
        games_response = requests.get(games_url)
        if games_response.status_code == 200:
            data = games_response.json()
            for game in data.get('games', []):
                away = f"{game['away'].get('market', '')} {game['away']['name']}".strip()
                home = f"{game['home'].get('market', '')} {game['home']['name']}".strip()
                game_time_utc = datetime.fromisoformat(game['scheduled'])
                game_time_local = game_time_utc.astimezone(tz).strftime("%I:%M %p")
                games.append({
                    'away': away,
                    'home': home,
                    'time': game_time_local
                })

        standings_response = requests.get(standings_url)
        if standings_response.status_code == 200:
            data = standings_response.json()
            for league in data['league']['season']['leagues']:
                for division in league['divisions']:
                    teams = []
                    for team in division['teams']:
                        teams.append({
                            'rank': team['rank']['division'],
                            'name': team['name'],
                            'wins': team['win'],
                            'losses': team['loss'],
                            'win_p': f"{team['win_p']:.3f}",
                            'games_back': team['games_back'],
                            'last_10': f"{team['last_10_won']}-{team['last_10_lost']}"
                        })
                    divisions.append({
                        'division_name': division['name'],
                        'teams': teams
                    })

    except Exception as e:
        print(f"Error fetching sports data: {e}")

    cached_sports_data = {'games': games, 'divisions': divisions}
    cached_sports_time = now
    print("✅ Sports data updated and cached")
    return jsonify(cached_sports_data)

# --- Spotify Backend ---
@app.route('/spotify_data')
def get_spotify_info():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='secrets/.spotify_token.json'
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
        cache_path='secrets/.spotify_token.json'
    )
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def spotify_callback():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='secrets/.spotify_token.json'
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    return redirect('/spotify') if token_info else "Authorization failed."

# --- Calendar Backend ---
@app.route('/calendar_data')
def get_calendar_events():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    if os.path.exists('secrets/token.json'):
        creds = Credentials.from_authorized_user_file('secrets/token.json', SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('secrets/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('secrets/token.json', 'w') as token:
                token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    today = now.date()

    one_month_later = today.replace(day=28) + timedelta(days=10)
    one_month_later = one_month_later.replace(day=1)

    start_today = tz.localize(datetime.combine(today, dt_time.min)).isoformat()
    end_today = tz.localize(datetime.combine(today, dt_time.max)).isoformat()
    start_future = tz.localize(datetime.combine(today + timedelta(days=1), dt_time.min)).isoformat()
    end_future = tz.localize(datetime.combine(one_month_later, dt_time.max)).isoformat()

    today_events = []
    upcoming_events = []

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