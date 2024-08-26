from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import praw
import os
from collections import Counter
from openai import OpenAI
import json

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

# User preferences storage (in-memory for demonstration)
user_preferences = {}

# Conversation history storage
conversation_history = {}

@app.route('/get_active_subreddits', methods=['GET'])
def get_active_subreddits():
    username = request.args.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    def generate_initial_insights(top_5_activities):
        prompt = f"""Given this dictionary of subreddits and the comments / submissions of the user, give me insights and a summary of what the user's biggest
        interests are and what they seem to be talking about the most. For each subreddit, if you were to create a controversial or engaging post for this user
        detail what you would talk about and why you would talk about that. Do not output in an MD format, output like a normal block of text making sure to spread
        over multiple lines: {top_5_activities}"""

        messages = conversation_history.get(username, [])
        messages.append({"role": "system", "content": "You are an analyst who finds out what a reddit user is more interested in and engaged by"})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        title = response.choices[0].message.content.strip()
        
        # Update conversation history
        messages.append({"role": "assistant", "content": title})
        conversation_history[username] = messages

        return title
    
    def generate():
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
                    activities[comment.subreddit.display_name].append(f"Submission Titled: {submission.title}")
                else:
                    activities[comment.subreddit.display_name] = [f"Submission Titled: {submission.title}"]

            # Sort activities by the number of posts/comments and get top 5
            top_5_activities = sorted(activities.items(), key=lambda x: len(x[1]), reverse=True)[:5]

            initial_insights = generate_initial_insights(top_5_activities)

            print()
            print()
            print(f"Initial INSIGHTS:   {initial_insights}")

            yield f"data: {json.dumps({'insights': initial_insights})}\n\n"

            for subreddit, posts in top_5_activities:
                story = generate_story(username, subreddit, posts)
                image_prompt = generate_img_prompt(username, story)
                image_url = generate_image(image_prompt)
                print(story)

                prompt = f"""Given the below story, create a provocative, clickbait reddit post title so that people click on the post but do not make it too
                flashy or overuse emojis, it still needs to be believable. Output only the title, DO NOT start with \"Title: \": {story}"""

                messages = conversation_history.get(username, [])
                messages.append({"role": "system", "content": "You are a clickbait article creator"})
                messages.append({"role": "user", "content": prompt})

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )

                title = response.choices[0].message.content.strip()
                
                # Update conversation history
                messages.append({"role": "assistant", "content": title})
                conversation_history[username] = messages

                yield f"data: {json.dumps({
                    "subreddit": subreddit,
                    "title": title,
                    "story": story,
                    "image_url": image_url
                })}\n\n"

            # Initialize user preferences if not exist
            if username not in user_preferences:
                user_preferences[username] = {
                    'clicked_articles': [],
                    'subreddit_preferences': Counter(),
                    'keyword_preferences': Counter()
                }

            yield "data: DONE\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), content_type='text/event-stream')

@app.route('/track_article_click', methods=['POST'])
def track_article_click():
    data = request.json
    username = data.get('username')
    article = data.get('article')

    if not username or not article:
        return jsonify({'error': 'Username and article data are required'}), 400

    try:
        # Update user preferences
        user_prefs = user_preferences.get(username, {
            'clicked_articles': [],
            'subreddit_preferences': Counter(),
            'keyword_preferences': Counter()
        })

        user_prefs['clicked_articles'].append(article)
        user_prefs['subreddit_preferences'][article['subreddit']] += 1
        
        # Extract keywords from title and story
        keywords = extract_keywords(article['title'] + " " + article['story'])
        user_prefs['keyword_preferences'].update(keywords)

        user_preferences[username] = user_prefs

        # Generate AI insights
        ai_insights = generate_ai_insights(username, article)

        return jsonify({
            'message': 'Article click tracked successfully',
            'ai_insights': ai_insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def extract_keywords(text):
    # This is a basic keyword extraction. In a real application, you'd use more sophisticated NLP techniques.
    words = text.lower().split()
    stop_words = set(['the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'but'])
    return [word for word in words if word not in stop_words and len(word) > 3]

def generate_ai_insights(username, clicked_article):
    user_prefs = user_preferences.get(username, {})
    
    if not user_prefs or len(user_prefs['clicked_articles']) == 0:
        return "Not enough data to generate insights yet."

    prompt = f"""
    The user '{username}' has just clicked on the following article:
    
    Subreddit: {clicked_article['subreddit']}
    Title: {clicked_article['title']}
    Story: {clicked_article['story']}

    Based on this interaction, provide insights on the user's interests and how to better engage them in the future.
    Consider how this click changes our understanding of the user's preferences.
    Suggest ways to create more engaging content for this user based on this new information. Do not output in an MD 
    format, output like a normal block of text making sure to spread over multiple lines
    """

    messages = conversation_history.get(username, [])
    messages.append({"role": "system", "content": "You are an AI analyst providing insights on user engagement based on their interactions with Reddit content."})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    insights = response.choices[0].message.content.strip()

    # Update conversation history
    # messages.append({"role": "assistant", "content": insights})
    conversation_history[username] = messages

    return insights

def generate_img_prompt(username, story):
    try:
        prompt = f"""
        Based on the following story, create a DALL-E image generation prompt that captures the essence of the story. It should NOT contain any form of 
        text or alphabetic characters at all. The image should be realistic and thought-provoking, suitable for the clickbait article nature of the story. 
        The image should NOT be over the top and should look like a news article image. The prompt should be less than 800 characters and should be in line with
        the safety system of DALL-E and ChatGPT:

        {story}
        """

        messages = conversation_history.get(username, [])
        messages.append({"role": "system", "content": "You are a prompt engineer tasked with generating DALL-E image prompts that make believable images for controversial Reddit posts."})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        prompt = response.choices[0].message.content.strip()

        # Update conversation history
        messages.append({"role": "assistant", "content": prompt})
        conversation_history[username] = messages

        return prompt
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        return story

def generate_story(username, subreddit, posts):
    try:
        prompt = f"""
        Based on the following information about a Reddit user's activity:
        - Most active subreddit: r/{subreddit}
        - Their posts: {'\n\n'.join(posts[:5])}  # Limit to first 5 posts for brevity

        Generate a reddit post containing a fake story or headline that is either strongly against or strongly
        supportive of the opinions displayed by this user and their posts on r/{subreddit}. It should be engaging 
        and provocative, like a clickbait article but not too unbelievable. Feel free to start rumors or create a 
        controversial story about characters or people that are related to this subreddit. Do not include a title, give
        me only the post body itself.
        """

        messages = conversation_history.get(username, [])

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages + [{"role": "system", "content": "You are a creative writer tasked with generating engaging Reddit Posts based on Reddit user activity."},
                                 {"role": "user", "content": prompt}]
        )

        story = response.choices[0].message.content.strip()

        # Update conversation history
        messages.append({"role": "assistant", "content": story})
        conversation_history[username] = messages

        return story
    except Exception as e:
        print(f"Error generating story: {e}")
        return f"A mysterious tale unfolds in the realm of r/{subreddit}."

def generate_image(story):
    #return "https://via.placeholder.com/256x256?text=Image+Unavailable"
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