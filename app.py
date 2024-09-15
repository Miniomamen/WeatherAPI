from flask import Flask, jsonify, request, render_template
import os
import requests
import redis
import json
from dotenv import load_dotenv
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file
load_dotenv()

# Get environment variables
API_KEY = os.getenv('API_KEY')
API_BASE_URL = os.getenv('API_BASE_URL')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Initialize Flask app
app = Flask(__name__)

# Setup Flask-Limiter with Redis as the storage backend
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)

# Function to fetch weather data from API or cache
def get_weather(city, unit_group="metric", forecast=False):
    if not API_KEY or not API_BASE_URL:
        raise ValueError("Missing API key or API URL")

    # Create a cache key based on city and forecast option
    cache_key = f"weather:{city}:{forecast}"
    cached_data = redis_client.get(cache_key)

    # If cached data exists, return it
    if cached_data:
        try:
            return json.loads(cached_data.decode('utf-8'))
        except json.JSONDecodeError:
            redis_client.delete(cache_key)

    # Fetch from the API if cache doesn't exist
    forecast_param = "forecast" if forecast else "current"
    url = f"{API_BASE_URL}/{city}?unitGroup={unit_group}&key={API_KEY}&contentType=json&include={forecast_param}"

    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        redis_client.setex(cache_key, 43200, json.dumps(weather_data))  # Cache for 12 hours
        return weather_data
    else:
        raise Exception(f"API request failed with status code: {response.status_code}")

# Route for current weather
@app.route('/weather/current', methods=['GET'])
def current_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        weather_data = get_weather(city)
        current_conditions = weather_data.get('currentConditions', {})
        return jsonify({
            "city": city,
            "datetime": current_conditions.get('datetime', 'No data'),
            "temperature": current_conditions.get('temp', 'No data'),
            "humidity": current_conditions.get('humidity', 'No data'),
            "wind_speed": current_conditions.get('windspeed', 'No data'),
            "description": current_conditions.get('conditions', 'No data')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for weather forecast
@app.route('/weather/forecast', methods=['GET'])
def weather_forecast():
    city = request.args.get('city')
    days = int(request.args.get('days', 1))
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        weather_data = get_weather(city, forecast=True)
        forecast_data = weather_data.get('days', [])[:days]
        return jsonify({
            "city": city,
            "forecast": forecast_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home page with form
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Limit 5 requests per minute
def index():
    if request.method == 'POST':
        city = request.form.get('city')
        forecast_days = int(request.form.get('forecast_days', 0))
        forecast = forecast_days > 0
        try:
            weather_data = get_weather(city, forecast=forecast)
            if forecast:
                forecast_data = weather_data.get('days', [])[:forecast_days]
                return render_template('weather.html', city=city, forecast=forecast_data)
            else:
                current_conditions = weather_data['currentConditions']
                temperature = current_conditions.get('temp', 'No data')
                humidity = current_conditions.get('humidity', 'No data')
                wind_speed = current_conditions.get('windspeed', 'No data')
                description = current_conditions.get('conditions', 'No data')
                datetime_str = current_conditions.get('datetime', 'No data')

                current_datetime = datetime.strptime(datetime_str, "%H:%M:%S").replace(
                    year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                return render_template('weather.html', city=city, datetime=formatted_datetime,
                                       temperature=f"{temperature}°C", humidity=f"{humidity}%",
                                       wind_speed=f"{wind_speed} km/h", description=description)
        except Exception as e:
            return render_template('weather.html', error=str(e))

    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
