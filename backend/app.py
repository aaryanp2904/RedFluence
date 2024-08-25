from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
import praw
import os
from collections import Counter
from openai import OpenAI

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')

# Reddit App Credentials
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:5000/callback"
USER_AGENT = "script:red-influence:v1.0 (by u/LionsBro2907)"

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# PRAW instance (without user authentication yet)
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     redirect_uri=REDIRECT_URI,
                     user_agent=USER_AGENT)

@app.route('/get_active_subreddits', methods=['POST'])
def get_active_subreddits():
    data = request.json
    username = data['username']
    
    try:
        user = reddit.redditor(username)
        subreddits = []
        
        # Collect subreddits from user's recent comments and submissions
        for comment in user.comments.new(limit=100):
            subreddits.append(comment.subreddit.display_name)
        for submission in user.submissions.new(limit=100):
            subreddits.append(submission.subreddit.display_name)
        
        # Count occurrences and get the top 5 most active subreddits
        most_active = Counter(subreddits).most_common(5)
        top_subreddits = [subreddit for subreddit, _ in most_active]

        # Generate images for each subreddit
        images = []
        for subreddit in top_subreddits:
            prompt = f"An abstract representation of the {subreddit} subreddit"
            image_url = generate_image(prompt)
            images.append({"subreddit": subreddit, "image_url": image_url})

        return jsonify({
            'subreddits': top_subreddits,
            'images': images
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="256x256",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(image_url)
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        # Return a placeholder image URL
        return "https://via.placeholder.com/256x256?text=Image+Unavailable"


if __name__ == '__main__':
    app.run(debug=True)