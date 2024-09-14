from flask import Flask

app = Flask(__name__)

# Endpoint '/weather' zwracający testowe dane pogodowe
@app.route('/weather', methods=['GET'])
def get_weather():
    return {
        "city": "Test City",
        "temperature": "25°C",
        "description": "Sunny"
    }

if __name__ == '__main__':
    app.run(debug=True)
