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
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'https://minasat-fitna.vercel.app',
    'https://fitna-frontend.vercel.app',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# CSRF trusted origins (should match CORS origins)
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS[:]

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)



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

# Cloudflare R2 / S3 Storage Config
AWS_ACCESS_KEY_ID = config('CLOUDFLARE_R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('CLOUDFLARE_R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = config('CLOUDFLARE_R2_ENDPOINT')
AWS_S3_REGION_NAME = 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
