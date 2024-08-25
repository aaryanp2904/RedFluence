# import os
# from openai import OpenAI
# import requests
# import torch
# from diffusers import FluxPipeline
# from PIL import Image
# import io

# # Initialize OpenAI client
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# def generate_headlines(profile_data):
#     # Extract relevant information from profile_data
#     username = profile_data['username']
#     bio = profile_data['biography']
#     account_type = profile_data['account_type']
#     media_count = profile_data['media_count']
    
#     # Create a prompt based on the available data
#     prompt = f"""
#     Generate 4 engaging news article headlines based on the following Instagram profile information:
#     Username: {username}
#     Biography: {bio}
#     Account Type: {account_type}
#     Number of Posts: {media_count}
    
#     The headlines should be tailored to this user's profile and potentially controversial or sensational.
#     """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a creative headline generator."},
#                 {"role": "user", "content": prompt}
#             ]
#         )
        
#         headlines = response.choices[0].message.content.strip().split('\n')
#         return headlines[:4]  # Ensure we return exactly 4 headlines
#     except Exception as e:
#         raise Exception(f"Error generating headlines: {str(e)}")

# def generate_article_and_image(chosen_headline, profile_data):
#     # Extract relevant information from profile_data
#     username = profile_data['username']
#     bio = profile_data['biography']
#     account_type = profile_data['account_type']
#     media_count = profile_data['media_count']
    
#     article_prompt = f"""
#     Write a short, engaging news article based on the following headline and Instagram profile information:
#     Headline: {chosen_headline}
#     Username: {username}
#     Biography: {bio}
#     Account Type: {account_type}
#     Number of Posts: {media_count}
    
#     The article should be approximately 3-4 paragraphs long and written in a style that relates to the user's Instagram presence.
#     """
    
#     try:
#         article_response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a news article writer."},
#                 {"role": "user", "content": article_prompt}
#             ]
#         )
        
#         article = article_response.choices[0].message.content.strip()
        
#         # Generate image using Flux
#         model_id = "black-forest-labs/FLUX.1-schnell"
#         pipe = FluxPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
#         pipe.enable_model_cpu_offload()
        
#         image_prompt = f"Create an image for a news article about an Instagram profile with the headline: {chosen_headline}"
#         seed = 42
#         image = pipe(
#             image_prompt,
#             output_type="pil",
#             num_inference_steps=4,
#             generator=torch.Generator("cpu").manual_seed(seed)
#         ).images[0]
        
#         # Convert PIL Image to base64 encoded string
#         buffered = io.BytesIO()
#         image.save(buffered, format="PNG")
#         img_str = base64.b64encode(buffered.getvalue()).decode()
        
#         # Create a data URL
#         image_url = f"data:image/png;base64,{img_str}"
        
#         return article, image_url
#     except Exception as e:
#         raise Exception(f"Error generating article and image: {str(e)}")

# def analyze_sentiment(text):
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a sentiment analyzer. Provide a brief sentiment analysis of the given text."},
#                 {"role": "user", "content": f"Analyze the sentiment of this text: {text}"}
#             ]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         raise Exception(f"Error analyzing sentiment: {str(e)}")

# def generate_hashtags(article):
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a hashtag generator for social media posts."},
#                 {"role": "user", "content": f"Generate 5 relevant hashtags for this article: {article}"}
#             ]
#         )
#         hashtags = response.choices[0].message.content.strip().split('\n')
#         return hashtags[:5]  # Ensure we return exactly 5 hashtags
#     except Exception as e:
#         raise Exception(f"Error generating hashtags: {str(e)}")