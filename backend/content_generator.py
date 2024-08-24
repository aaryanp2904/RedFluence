import os
from openai import OpenAI
import requests

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_headlines(profile_data):
    interests = ', '.join(profile_data['followees'][:10])  # Use first 10 followees as interests
    prompt = f"""
    Generate 4 engaging news article headlines based on the following Instagram profile information:
    Username: {profile_data['username']}
    Biography: {profile_data['biography']}
    Interests: {interests}
    
    The headlines should be tailored to this user's interests and potentially controversial or sensational.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative headline generator."},
                {"role": "user", "content": prompt}
            ]
        )

        headlines = response.choices[0].message.content.strip().split('\n')
        return headlines[:4]  # Ensure we return exactly 4 headlines
    except Exception as e:
        raise Exception(f"Error generating headlines: {str(e)}")

def generate_article_and_image(chosen_headline, profile_data):
    interests = ', '.join(profile_data['followees'][:10])
    article_prompt = f"""
    Write a short, engaging news article based on the following headline and tailored to the user's interests:
    Headline: {chosen_headline}
    User Interests: {interests}
    
    The article should be approximately 3-4 paragraphs long and written in a style that appeals to the user based on their interests.
    """

    try:
        article_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a news article writer."},
                {"role": "user", "content": article_prompt}
            ]
        )

        article = article_response.choices[0].message.content.strip()

        # Generate image using DALL-E
        image_prompt = f"Create an image for a news article with the headline: {chosen_headline}"
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = image_response.data[0].url

        return article, image_url
    except Exception as e:
        raise Exception(f"Error generating article and image: {str(e)}")

# You can add more helper functions here if needed