from config import get_settings


def get_google_oauth_config():
    """
    Get Google OAuth configuration from main settings.
    Returns a dictionary with client_id, client_secret, and redirect_uri.
    """
    settings = get_settings()
    return {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI
    }
