from flask import Flask, request, jsonify
from flask_cors import CORS
from instagram_analyzer import analyze_instagram_profile
from content_generator import generate_headlines, generate_article_and_image
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    instagram_url = request.json.get('instagram_url')
    if not instagram_url:
        return jsonify({'error': 'No Instagram URL provided'}), 400

    try:
        profile_data = analyze_instagram_profile(instagram_url)
        if not profile_data:
            return jsonify({'error': 'Failed to analyze Instagram profile'}), 400

        headlines = generate_headlines(profile_data)
        return jsonify({'profile_data': profile_data, 'headlines': headlines})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    chosen_headline = request.json.get('chosen_headline')
    profile_data = request.json.get('profile_data')

    if not chosen_headline or not profile_data:
        return jsonify({'error': 'Missing headline or profile data'}), 400

    try:
        article, image_url = generate_article_and_image(chosen_headline, profile_data)
        return jsonify({'article': article, 'image_url': image_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development',
            port=int(os.getenv('PORT', 5000)))