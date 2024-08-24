from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from content_generator import generate_headlines, generate_article_and_image
from instagram_analyzer import analyze_instagram_profile, get_instagram_auth_url, get_access_token
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Set this in your .env file
CORS(app)

# Instagram App credentials
INSTAGRAM_APP_ID = os.getenv('INSTAGRAM_APP_ID')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')
INSTAGRAM_REDIRECT_URI = os.getenv('INSTAGRAM_REDIRECT_URI')

@app.route('/auth/instagram')
def auth_instagram():
    auth_url = get_instagram_auth_url(INSTAGRAM_APP_ID, INSTAGRAM_REDIRECT_URI)
    return redirect(auth_url)

@app.route('/auth/instagram/callback')
def instagram_callback():
    code = request.args.get('code')
    if code:
        try:
            access_token = get_access_token(INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET, INSTAGRAM_REDIRECT_URI, code)
            session['instagram_access_token'] = access_token
            return redirect(url_for('index'))  # Redirect to your frontend
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Authentication failed'}), 400

@app.route('/analyze', methods=['POST'])
def analyze():
    access_token = session.get('instagram_access_token')
    if not access_token:
        return jsonify({'error': 'Not authenticated with Instagram'}), 401

    instagram_url = request.json.get('instagram_url')
    if not instagram_url:
        return jsonify({'error': 'No Instagram URL provided'}), 400

    try:
        profile_data = analyze_instagram_profile(access_token, instagram_url)
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
            port=int(os.getenv('PORT', 5000)))# , ssl_context=('server.crt', 'server.key')) 
    #ssl_context=(os.getenv("SERVER_CRT"), os.getenv("SERVER_KEY")))