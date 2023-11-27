# Tutaj bedzie nasz skrypcik pythonowy do laczania pythona z js
# Aby to zrobić robimy REST API

# docker-compose up -d
from flask import Flask, render_template, jsonify, request

index_path = 'index.html'
map_path = 'map.html'
app = Flask(__name__)


@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    print(data)
    return jsonify(data)


# Display front page
@app.route('/')
def index():
    return render_template(index_path)


@app.route('/map')
def map_page():
    return render_template(map_path)


def run_all():
    app.run(host="0.0.0.0", port=80, debug=True)
