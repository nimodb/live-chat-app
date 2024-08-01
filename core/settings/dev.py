from .common import *

DEBUG = True

SECRET_KEY = "django-insecure-%c)91v9-7b^4pcd+h9opr33yfg)3av*6=+=i974mhyhm-j6!!@"

INSTALLED_APPS += [
    "debug_toolbar",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
