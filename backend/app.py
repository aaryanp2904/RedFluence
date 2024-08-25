from flask import Flask, request, jsonify
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

# PRAW instance (without user authentication)
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     redirect_uri=REDIRECT_URI,
                     user_agent=USER_AGENT)

@app.route('/get_active_subreddits', methods=['POST'])
def get_active_subreddits():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    try:
        user = reddit.redditor(username)
        activities = {}
        
        # Collect subreddits and comments from user's recent activity
        for comment in user.comments.new(limit=50):
            if comment.subreddit.display_name in activities:
                activities[comment.subreddit.display_name].append(comment.body)
            else:
                activities[comment.subreddit.display_name] = [comment.body]
        for submission in user.submissions.new(limit=50):
            if submission.subreddit.display_name in activities:
                activities[submission.subreddit.display_name].append(f"Submission Titled: {submission.title}")
            else:
                activities[submission.subreddit.display_name] = [f"Submission Titled: {submission.title}"]

        # Sort activities by the number of posts/comments and get top 5
        top_5_activities = sorted(activities.items(), key=lambda x: len(x[1]), reverse=True)[:5]

        # Generate stories and images for each subreddit
        stories_and_images = []
        for subreddit, posts in top_5_activities:
            story = generate_story(subreddit, posts)
            image_prompt = generate_img_prompt(story)
            image_url = generate_image(image_prompt)
            stories_and_images.append({
                "subreddit": subreddit,
                "story": story,
                "image_url": image_url
            })

        return jsonify({
            'subreddits': [subreddit for subreddit, _ in top_5_activities],
            'stories_and_images': stories_and_images
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_img_prompt(story):
    try:
        prompt = f"""
        Based on the following story, create a DALL-E image generation prompt that captures the essence of the story. It should not contain any
        text. The image should be realistic and thought-provoking, suitable for the clickbait article nature of the story. The prompt should be less than 800 characters:

        {story}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a prompt engineer tasked with generating images to match controversial Reddit posts."},
                {"role": "user", "content": prompt}
            ]
        )

        prompt = response.choices[0].message.content.strip()

        return prompt
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        return story

def generate_story(subreddit, posts):
    try:
        prompt = f"""
        Based on the following information about a Reddit user's activity:
        - Most active subreddit: r/{subreddit}
        - Their posts: {'\n\n'.join(posts[:5])}  # Limit to first 5 posts for brevity

        Generate a reddit post containing a fake story or headline that is either strongly against or strongly
        supportive of the opinions displayed by this user and their posts on r/{subreddit}. It should
        be engaging and provocative, like a clickbait article. Feel free to start rumors or create a controversial story about characters or people that are related to
        this subreddit.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative writer tasked with generating engaging Reddit Posts based on Reddit user activity."},
                {"role": "user", "content": prompt}
            ]
        )

        story = response.choices[0].message.content.strip()
        return story
    except Exception as e:
        print(f"Error generating story: {e}")
        return f"A mysterious tale unfolds in the realm of r/{subreddit}."

def generate_image(story):
    try:
        prompt = f"A surreal and thought-provoking illustration inspired by this reddit post: {story}"
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"Image generated: {image_url}")
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return "https://via.placeholder.com/256x256?text=Image+Unavailable"

if __name__ == '__main__':
    app.run(debug=True)