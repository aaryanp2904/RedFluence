import instaloader
from instaloader.exceptions import ProfileNotExistsException, PrivateProfileNotFollowedException

def analyze_instagram_profile(instagram_url):
    # Extract username from URL
    username = instagram_url.split('/')[-1].split('?')[0]

    # Initialize Instaloader
    L = instaloader.Instaloader()

    try:
        # Load profile
        profile = instaloader.Profile.from_username(L.context, username)

        # Collect data
        followees = []
        for followee in profile.get_followees():
            followees.append(followee.username)
            if len(followees) >= 100:  # Limit to first 100 followees
                break

        return {
            'username': username,
            'followees': followees,
            'biography': profile.biography,
            'followers_count': profile.followers,
            'following_count': profile.followees,
            'is_private': profile.is_private
        }
    except ProfileNotExistsException:
        raise ValueError(f"The profile {username} does not exist.")
    except PrivateProfileNotFollowedException:
        raise ValueError(f"The profile {username} is private and cannot be accessed.")
    except Exception as e:
        raise Exception(f"Error analyzing Instagram profile: {str(e)}")

# You can add more helper functions here if needed