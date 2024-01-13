# Tutaj bedzie nasz skrypcik pythonowy do laczania pythona z js
# Aby to zrobić robimy REST API

# docker-compose up -d
from flask import Flask, render_template, jsonify, request
import requests
import solve_engine

index_path = 'index.html'
map_path = 'map.html'
app = Flask(__name__)


@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    report = solve_engine.find_solution(data['services'], data['parameters']) # to musza byc slowniki

    return jsonify(report)


@app.route('/filter-cities', methods=['POST'])
def filter_cities():
    data = request.get_json()
    cities_data = []
    for city_name in data.get('cities', []):
        lat, lon = get_lat_lon_from_city_name(city_name)
        if lat and lon:
            cities_data.append({"lat": lat, "lon": lon})
    return jsonify(cities_data)


def get_lat_lon_from_city_name(city_name):
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
    return render_template(map_path)


def run_all():
    app.run(host="127.152.0.1", port=80, debug=True)
