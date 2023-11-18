# Tutaj bedzie nasz skrypcik pythonowy do laczania pythona z js

from flask import Flask, render_template, jsonify, request

index_path = 'index.html'
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


def run_all():
    app.run(host="127.0.0.1", port=80, debug=True)
