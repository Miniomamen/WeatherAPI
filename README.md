
# Weather API with Flask, Redis, and Flask-Limiter

This project is a Flask-based web application that fetches weather data for a given location from the Visual Crossing Weather API. The application implements caching using Redis and rate limiting using Flask-Limiter.

Solution to the roadmap.sh project Weather API https://roadmap.sh/projects/weather-api-wrapper-service

## Features

- **Weather Data Fetching**: Retrieves weather data for a specified location using the Visual Crossing Weather API.
- **Caching with Redis**: Caches the weather data in Redis to reduce API calls and improve performance.
- **Rate Limiting with Flask-Limiter**: Limits the number of API requests a user can make to prevent abuse.
- **Support for Current Weather and Forecasts**: Fetches current weather or weather forecasts for up to a specified number of days.
- **API Endpoints**: Provides API endpoints for current weather and forecast information.

## Requirements

- Python 3.x
- Flask
- Redis (Cloud or local instance)
- Visual Crossing Weather API Key
- SSL/TLS support for Redis connections (optional, depending on Redis setup)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Miniomamen/WeatherAPI.git
cd WeatherAPI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the project root directory and add the following:

```bash
API_KEY=your_visual_crossing_weather_api_key
API_BASE_URL=https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. Running the application

Ensure that Redis is running locally or on a remote server.

Start Redis manually:

#### For Linux or MacOS:

```bash
redis-server
```

#### For Windows (Using WSL or Redis for Windows):

```bash
redis-server
```

Run the Flask app:

```bash
python app.py
```

The application will run at `http://127.0.0.1:5000/`

## Usage

You can interact with the application through the web interface or by using `curl` to make API requests.

### Example: Get current weather for a city

```bash
curl "http://127.0.0.1:5000/weather/current?city=Wroclaw"
```

### Example: Get weather forecast for the next 3 days

```bash
curl "http://127.0.0.1:5000/weather/forecast?city=Wroclaw&days=3"
```

### Shutting down Redis

If Redis was started manually, you can stop it by running:

```bash
redis-cli shutdown
```

