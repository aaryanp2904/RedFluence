import requests
from urllib.parse import urlparse, parse_qs

def analyze_instagram_profile(access_token, instagram_url):
    # Extract username from URL (note: this isn't used in the API call, but kept for consistency)
    username = instagram_url.split('/')[-1].split('?')[0]

    # Instagram Graph API endpoint
    base_url = "https://graph.instagram.com/me"

    # Parameters for the API request
    params = {
        "fields": "id,username,account_type,media_count,biography",
        "access_token": access_token
    }

    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        profile_data = response.json()

        # Get user's media
        media_url = f"{base_url}/media"
        media_params = {
            "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username",
            "access_token": access_token
        }
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        media_data = media_response.json()

        # Process and return the data
        return {
            'username': profile_data.get('username'),
            'account_type': profile_data.get('account_type'),
            'media_count': profile_data.get('media_count'),
            'biography': profile_data.get('biography'),
            'recent_media': media_data.get('data', [])[:10]  # Get up to 10 recent media items
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error analyzing Instagram profile: {str(e)}")

# You may need additional functions to handle authentication and token management
def get_instagram_auth_url(app_id, redirect_uri):
    base_url = "https://api.instagram.com/oauth/authorize"
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": "user_profile,user_media",
        "response_type": "code"
    }
    return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

def get_access_token(app_id, app_secret, redirect_uri, code):
    token_url = "https://api.instagram.com/oauth/access_token"
    data = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

# Usage example (you would typically call these from your main application logic)
# auth_url = get_instagram_auth_url(YOUR_APP_ID, YOUR_REDIRECT_URI)
# access_token = get_access_token(YOUR_APP_ID, YOUR_APP_SECRET, YOUR_REDIRECT_URI, AUTH_CODE)
# profile_data = analyze_instagram_profile(access_token, INSTAGRAM_PROFILE_URL)