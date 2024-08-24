import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Flask Backend!"

@app.route('/api/data', methods=['GET'])
def get_data():
    sample_data = {
        "message": "This is a sample response from the Flask API."
    }
    return jsonify(sample_data)

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(debug=True)
    logging.info("Flask application has stopped.")