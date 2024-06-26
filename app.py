# Tutaj bedzie nasz skrypcik pythonowy do laczania pythona z js
# Aby to zrobić robimy REST API

# docker-compose up -d
from flask import Flask, render_template, jsonify, request
import requests
index_path = 'index.html'
map_path = 'map.html'
app = Flask(__name__)


@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    print(data)
    return jsonify(data)

@app.route('/filter-cities', methods=['POST'])
def filter_cities():
    data = request.get_json()
    cities_data = []
    for city_name in data.get('cities', []):
        lat, lon = get_lat_lon_from_city_name(city_name)
        if lat and lon:
            cities_data.append({"city": city_name, "lat": lat, "lon": lon})
    print(cities_data)
    print(jsonify(cities_data))
    return jsonify(cities_data)

def get_lat_lon_from_city_name(city_name):
    # Upewnij się, że klucz API jest poprawny i dodany do URL
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        if results:
            return results[0]['lat'], results[0]['lon']
    return None, None

# Display front page
@app.route('/')
def index():
    return render_template(index_path)


@app.route('/map')
def map_page():
    return render_template('map.html')


def run_all():
    app.run(host="0.0.0.0", port=80, debug=True)
