from .base import *
import dj_database_url

DEBUG = False

# Allowed Hosts from environment variable (comma-separated)
_allowed_hosts = config('ALLOWED_HOSTS', default='')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]
ALLOWED_HOSTS.extend(['.railway.app'])

# Trust X-Forwarded-Host from the reverse proxy
USE_X_FORWARDED_HOST = True

# CORS - only allow specified origins in production
CORS_ALLOW_ALL_ORIGINS = False
_cors_origins = config('CORS_ALLOWED_ORIGINS', default='')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]

# Hardcode the actual domains to fix CORS
CORS_ALLOWED_ORIGINS.extend([
    'https://minasat-fitna.vercel.app',
    'https://fitna-frontend.vercel.app',
    'http://localhost:5173',
    'http://localhost:8000',
])

# CSRF trusted origins (should match CORS origins)
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS[:]

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Whitenoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cloudinary storage for media files in production
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
