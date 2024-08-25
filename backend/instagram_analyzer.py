# import requests
# from urllib.parse import urlparse, parse_qs

# def analyze_instagram_profile(access_token, instagram_url):
#     # Extract username from URL (note: this isn't used in the API call, but kept for consistency)
#     username = instagram_url.split('/')[-1].split('?')[0]

#     # Instagram Graph API endpoint
#     base_url = "https://graph.instagram.com/me"

#     # Parameters for the API request
#     params = {
#         "fields": "id,username,account_type,media_count,biography",
#         "access_token": access_token
#     }

#     try:
#         # Make the API request
#         response = requests.get(base_url, params=params)
#         response.raise_for_status()  # Raises an HTTPError for bad responses
#         profile_data = response.json()

#         # Get user's media
#         media_url = f"{base_url}/media"
#         media_params = {
#             "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username",
#             "access_token": access_token
#         }
#         media_response = requests.get(media_url, params=media_params)
#         media_response.raise_for_status()
#         media_data = media_response.json()

#         # Process and return the data
#         return {
#             'username': profile_data.get('username'),
#             'account_type': profile_data.get('account_type'),
#             'media_count': profile_data.get('media_count'),
#             'biography': profile_data.get('biography'),
#             'recent_media': media_data.get('data', [])[:10]  # Get up to 10 recent media items
#         }

#     except requests.exceptions.RequestException as e:
#         raise Exception(f"Error analyzing Instagram profile: {str(e)}")

# # You may need additional functions to handle authentication and token management
# def get_instagram_auth_url(app_id, redirect_uri):
#     base_url = "https://api.instagram.com/oauth/authorize"
#     params = {
#         "client_id": app_id,
#         "redirect_uri": redirect_uri,
#         "scope": "user_profile,user_media",
#         "response_type": "code"
#     }
#     return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

# import requests

# def get_access_token(client_id, client_secret, redirect_uri, code):
#     """
#     Exchange the authorization code for an access token from Instagram.

#     Parameters:
#         client_id (str): The client ID of your Instagram app.
#         client_secret (str): The client secret of your Instagram app.
#         grant_type (str): The grant type, which should be 'authorization_code' for this request.
#         redirect_uri (str): The redirect URI that was used in the authorization request.
#         code (str): The authorization code received from Instagram.

#     Returns:
#         dict: JSON response containing the access token if successful.
#         None: Returns None if there's an error.
#     """
#     # URL for the POST request
#     url = 'https://api.instagram.com/oauth/access_token'

#     # Parameters for the POST request
#     data = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'grant_type': 'authorization_code',
#         'redirect_uri': redirect_uri,
#         'code': code
#     }

#     try:
#         # Make the POST request
#         response = requests.post(url, data=data)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             # Return the JSON response containing the access token
#             return response.json().get("access_token")
#         else:
#             # If the request failed, print the status code and reason
#             print(f"Error: {response.status_code} - {response.text}")
#             return None
#     except Exception as e:
#         # Catch any exceptions that may occur during the request
#         print(f"An error occurred: {e}")
#         return None

# # instagram_analyzer.py

# import requests

# def get_instagram_profile_followers_and_followees(access_token):
#     # Define the URLs for Instagram API calls to get followers and followees
#     followers_url = f'https://graph.instagram.com/me/followed-by?access_token={access_token}'
#     followees_url = f'https://graph.instagram.com/me/follows?access_token={access_token}'
    
#     followers_response = requests.get(followers_url)
#     followees_response = requests.get(followees_url)
    
#     if followers_response.status_code != 200 or followees_response.status_code != 200:
#         raise Exception('Error fetching followers or followees data')
    
#     followers = followers_response.json().get('data', [])
#     followees = followees_response.json().get('data', [])
    
#     return followers, followees


# # Usage example (you would typically call these from your main application logic)
# # auth_url = get_instagram_auth_url(YOUR_APP_ID, YOUR_REDIRECT_URI)
# # access_token = get_access_token(YOUR_APP_ID, YOUR_APP_SECRET, YOUR_REDIRECT_URI, AUTH_CODE)
# # profile_data = analyze_instagram_profile(access_token, INSTAGRAM_PROFILE_URL)

import requests
import os

CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID')
CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:3000/callback'

def get_auth_url():
    return f"https://api.instagram.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user_profile,user_media&response_type=code"

def exchange_code_for_token(code):
    url = 'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    response = requests.post(url, data=data)
    return response.json().get('access_token')

def get_followers_and_followees(access_token):
    url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
    response = requests.get(url)
    user_data = response.json()
    
    # Note: The Basic Display API doesn't provide direct access to followers/followees
    # This is a placeholder to show where you'd make the API call if it were available
    followers = ["Follower 1", "Follower 2"]
    followees = ["Followee 1", "Followee 2"]
    
    return followers, followees