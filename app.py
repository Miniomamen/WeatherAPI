from flask import Flask, request, render_template
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

# Initialize Flask application
app = Flask(__name__)

# Setup Flask-Limiter with Redis as storage backend
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)

# Function to fetch weather data
def get_weather(city, unit_group="metric", forecast=False):
    if not API_KEY or not API_BASE_URL:
        raise ValueError("Missing API key or API URL")

    cache_key = f"weather:{city}:{forecast}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        try:
            # Decode Redis cached data from bytes to string
            cached_data_str = cached_data.decode('utf-8')
            return json.loads(cached_data_str)
        except json.JSONDecodeError:
            redis_client.delete(cache_key)

    forecast_param = "forecast" if forecast else "current"
    url = f"{API_BASE_URL}/{city}?unitGroup={unit_group}&key={API_KEY}&contentType=json&include={forecast_param}"

    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        redis_client.setex(cache_key, 43200, json.dumps(weather_data))
        return weather_data
    else:
        raise Exception(f"API request failed with status code: {response.status_code}")

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
                wind_speed = current_conditions.get('windSpeed', 'No data')  # Poprawiona nazwa
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
