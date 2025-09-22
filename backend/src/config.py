from config import get_settings


def get_frontend_config():
    """
    Get Google OAuth configuration from main settings.
    Returns a dictionary with client_id, client_secret, and redirect_uri.
    """
    settings = get_settings()
    return {
        "frontend_url": settings.FRONTEND_URL
    }
