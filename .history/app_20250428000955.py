''' 
Smart Mirror Backend Server

1. Provides webpage routes for the Smart Mirror UI
2. Serves backend data for stocks, sports, Spotify, and Google Calendar
3. Caches API responses to limit frequent requests
4. Built with Flask
'''

#import libraries and modules
from flask import Flask, render_template, jsonify, request, redirect
import time
from datetime import datetime, time as dt_time, timedelta, date
import pytz, os, requests
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

#initialize flask
app = Flask(__name__)

#load env vars from .env file
load_dotenv()

#prevent caching after every request from remote to always show updated data
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

#set current page to home module
current_page = "home"

'''
Mirror UI Routes
'''
@app.route('/mirror')
def mirror():
    #load main mirror frame (acts as host page for all modules)
    return render_template('mirror.html')

@app.route('/current_page')
def get_current_page():
    #return the name of the current active page
    return jsonify({"page": current_page})

@app.route('/set_page', methods=['POST'])
def set_current_page():
    #update the /mirror page based on user request (from /remote)
    global current_page
    data = request.get_json()
    page = data.get('page', 'home')
    current_page = page
    return jsonify({"status": "success", "current_page": current_page})


'''
UI Subpages
'''
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

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
    return render_template('stocks.html')

@app.route('/sports')
def sports():
    return render_template('sports.html')


'''
LED Color Slider Route
1. Listens for POST requests containing a JSON with color value in hex format
2. Extracts color value from JSON data
3. Writes color value to color.txt so it can be used by other scripts to update the strip
'''
@app.route('/set_led_color', methods=['POST'])
def set_led_color():
    #Parse JSON data from request
    data = request.get_json()
    #Extract color value from JSON, default to white if missing
    color_hex = data.get('color', '#ffffff')

    #Save color hex code to color.txt
    with open("/home/pi/smart-mirror/color.txt", 'w') as f:
        f.write(color_hex)

    #If successful, return response with said color
    return jsonify({'status': 'success', 'color_set_to': color_hex})

'''
Stocks Module API Endpoint
1. Listens for GET requests to retrieve stock data for already established symbols
2. Checks if cached stock data is still valid (within STOCK_CACHE_TTL seconds) due to freee API limits (25 requests per day)
3. If cache is valid, returns cached data immediately
4. If cache is expired or missing, fetches fresh data from Alpha Vantage API (may go over request limit)
5. Parses the last 5 days' closing prices and formats dates
6. Updates cache with the newly fetched data
7. Returns formatted stock data as JSON
'''
#caching setup for stock data
cached_stock_data = None
cached_stock_time = 0
STOCK_CACHE_TTL = 600  # seconds

@app.route('/stocks_data')
def stocks_data():
    #initialize cache variables
    global cached_stock_data, cached_stock_time

    now = time.time()

    #checks if data exists and still valid
    if cached_stock_data and (now - cached_stock_time) < STOCK_CACHE_TTL:
        return jsonify(cached_stock_data)

    #if no valid cache, get fresh data
    API_KEY = "A79E9AHKRPHVZROI"
    #set stocks you want to use, pre defined labels 4 letters
    STOCK_SYMBOLS = ['GOOGL', 'NVDA', 'INTC', 'NXPI']
    result = {}

    for symbol in STOCK_SYMBOLS:
        #build API request URL
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
        print(f"Fetching {symbol}: {url}")

        #sencd HTTP request to Alpha Vantage
        r = requests.get(url, timeout=10)
        data = r.json()

        #extract "Time Series (Daily) section since we only care about daily prices"
        time_series = data.get("Time Series (Daily)", {})
        
        #set range to most recent 5 days of trading data
        dates = sorted(time_series.keys(), reverse=True)[:5]

        labels, prices = [], []

        #sort in ascending order for correct chart order
        for date_ in sorted(dates):
            #extract the closing price
            close_price = float(time_series[date_]["4. close"])

            #format date as m/d - time doesnt matter
            month, day = date_.split("-")[1:]
            labels.append(f"{int(month)}/{int(day)}")
            prices.append(close_price)

        #store formatted data for current stock (symbol)
        result[symbol] = {"labels": labels, "prices": prices}

    #store data in cache with timestamp
    cached_stock_data = result
    cached_stock_time = now

    #return new stock data
    return jsonify(result)

'''
Sports API ROute
1. Listens for GET requests to provide 2 variables: today's MLB games and division standings
2. Checks if cached sports data is still valid (within SPORTS_CACHE_TTL seconds) (1000 requests per month)
3. If cache is valid, returns cached data immediately
4. If cache is expired or missing, fetches new data from Sportradar API
5. Parses today's games and formats game times in EST
6. Parses division standings including wins, losses, win %, GB(games behind), and last 10 games record
7. Updates cache with the newly fetched sports data
8. Returns formatted sports data as JSON
'''
#caching setup for sports data
cached_sports_data = None
cached_sports_time = 0
SPORTS_CACHE_TTL = 600  # seconds

@app.route('/sports_data')
def sports_data():
    #initialize cache variables
    global cached_sports_data, cached_sports_time

    now = time.time()

    #checks if data exists and still valid
    if cached_sports_data and (now - cached_sports_time) < SPORTS_CACHE_TTL:
        # Return cached sports if not expired
        print("✅ Returning cached sports data")
        return jsonify(cached_sports_data)

    #if no valid cache, get fresh data
    API_KEY = "PoeGaPJk98jwRXxUCxzL1BkR4Fg94PYlk6lIhuYb"
    tz = pytz.timezone("US/Eastern")
    today = date.today()

    #build API request URL
    games_url = f"https://api.sportradar.com/mlb/trial/v8/en/games/{today.year}/{today.month:02}/{today.day:02}/schedule.json?api_key={API_KEY}"
    standings_url = f"https://api.sportradar.com/mlb/trial/v8/en/seasons/{today.year}/REG/standings.json?api_key={API_KEY}"

    games, divisions = [], []

    try:
        #get today's games
        games_response = requests.get(games_url)
        if games_response.status_code == 200:
            data = games_response.json()
            for game in data.get('games', []):
                #format team names and convert game time to EST
                away = f"{game['away'].get('market', '')} {game['away']['name']}".strip()
                home = f"{game['home'].get('market', '')} {game['home']['name']}".strip()
                game_time_utc = datetime.fromisoformat(game['scheduled'])
                game_time_local = game_time_utc.astimezone(tz).strftime("%I:%M %p")
                games.append({'away': away, 'home': home, 'time': game_time_local})

        #get standings data
        standings_response = requests.get(standings_url)
        if standings_response.status_code == 200:
            data = standings_response.json()
            for league in data['league']['season']['leagues']:
                for division in league['divisions']:
                    teams = []
                    for team in division['teams']:
                        #extract team standings information
                        teams.append({
                            'rank': team['rank']['division'],
                            'name': team['name'],
                            'wins': team['win'],
                            'losses': team['loss'],
                            'win_p': f"{team['win_p']:.3f}",
                            'games_back': team['games_back'],
                            'last_10': f"{team['last_10_won']}-{team['last_10_lost']}"
                        })
                    divisions.append({'division_name': division['name'], 'teams': teams})

    #error handling; catch any errors during fetching/parsing data
    except Exception as e:
        print(f"Error fetching sports data: {e}")

    #store data in cache with timestamp 
    cached_sports_data = {'games': games, 'divisions': divisions}
    cached_sports_time = now

    #return new sports data
    return jsonify(cached_sports_data)

'''
Spotify Module API Routes
1. spotify_data: Fetches the currently playing Spotify track using a saved token (spotify_token.json)
2. callback: Handles Spotify OAuth callback and saves the access token for future use
'''
@app.route('/spotify_data')
def get_spotify_info():
    #authenticate credentials and get current playback info from Spotify
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='secrets/.spotify_token.json'
    )

    #check for cached token (spotify_token.json)
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        #if no valid token, redirect to spotify login
        return redirect(sp_oauth.get_authorize_url())

    #create spotify client using valid token
    sp = Spotify(auth_manager=sp_oauth)

    #fetch current track playing
    song = sp.current_playback()

    if song and song.get('item'):
        track = song['item']
        album = track.get('album', {})
        artists = track.get('artists', [])

        #return track info as json
        return jsonify({
            'name': track.get('name'),
            'artist': artists[0]['name'] if artists else 'N/A',
            'album': album.get('name'),
            'album_cover': album.get('images', [{}])[0].get('url', ''),
            'device': song.get('device', {}).get('name'),
            'duration_ms': track.get('duration_ms', 0),
            'progress_ms': song.get('progress_ms', 0)
        })

    #if no song is detected playing, just return null/empty for all
    return jsonify({'name': 'N/A', 'artist': 'N/A', 'album': 'N/A', 'album_cover': '', 'device': 'N/A'})

@app.route('/callback')
def spotify_callback():
    #handle OAuth callback from Spotify after user login
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://10.0.0.180:5000/callback',
        scope='user-read-playback-state user-read-currently-playing',
        cache_path='secrets/.spotify_token.json'
    )

    #extract auth code from query parameters
    code = request.args.get('code')

    #exchange auth code for token
    token_info = sp_oauth.get_access_token(code, as_dict=True)

    #redirect to /spotify if successful
    return redirect('/spotify') if token_info else "Authorization failed"

'''
Google Calendar API Route
1. Listens for GET requests to fetch calendar events from google cal
2. Checks for existing token to authenticate with Google Calendar API
3. If token is expired, refreshes it; if missing, requires full OAuth login
4. Connects to cal API using valid credentials
5. Fetches today's events from "Classes" calendar
6. Fetches upcoming personal events from "Other" calendar
7. Parses event times and formats them for easy display
8. Returns today's and upcoming events as JSON
'''
@app.route('/calendar_data')
def get_calendar_events():
    #authenticate and get calendar events
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    creds = None

    #check if saved token file exists and is valid
    if os.path.exists('secrets/token.json'):
        creds = Credentials.from_authorized_user_file('secrets/token.json', SCOPES)
        #refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    #if no valid token, start full OAauth authorization process
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('secrets/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('secrets/token.json', 'w') as token:
            token.write(creds.to_json())

    #build Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)

    #set timezone as EST and set date ranges
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    today = now.date()
    one_month_later = (today.replace(day=28) + timedelta(days=10)).replace(day=1)

    #start and end vars for today and future events
    start_today = tz.localize(datetime.combine(today, dt_time.min)).isoformat()
    end_today = tz.localize(datetime.combine(today, dt_time.max)).isoformat()
    start_future = tz.localize(datetime.combine(today + timedelta(days=1), dt_time.min)).isoformat()
    end_future = tz.localize(datetime.combine(one_month_later, dt_time.max)).isoformat()

    today_events, upcoming_events = [], []

    #get today's events from "Classes" calendar
    classes_result = service.events().list(
        calendarId='f68d2ac45e9ac7aba185ad08cc6d511542196634c495bca2cff141cf13e8e22f@group.calendar.google.com',
        timeMin=start_today,
        timeMax=end_today,
        timeZone='America/New_York',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for e in classes_result.get('items', []):
        #parse event start time and summary
        dt = datetime.fromisoformat(e['start'].get('dateTime', e['start'].get('date')).replace('Z', '')).astimezone(tz)
        today_events.append({'start': dt.strftime('%I:%M %p'), 'summary': e.get('summary', 'No Title')})

    #get upcoming events from "Other" calendar
    daniel_result = service.events().list(
        calendarId='9cf36c61af86479abe999f348c513dcdc1a190a54b22038fbba2f274401c8261@group.calendar.google.com',
        timeMin=start_future,
        timeMax=end_future,
        timeZone='America/New_York',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for e in daniel_result.get('items', []):
        #Parse date, start time, and summary
        dt = datetime.fromisoformat(e['start'].get('dateTime', e['start'].get('date')).replace('Z', '')).astimezone(tz)
        upcoming_events.append({'date': dt.strftime('%A, %B %d'), 'start': dt.strftime('%I:%M %p'), 'summary': e.get('summary', 'No Title')})

    #return today's and upcoming events as JSON
    return jsonify({'today': today_events, 'upcoming': upcoming_events})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)