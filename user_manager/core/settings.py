import os

# Database
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NETWORK = os.environ["DB_NETWORK"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]


# Auth
CIPHER_KEY = os.environ["CIPHER_KEY"]
CIPHER_IV = os.environ["CIPHER_IV"]
JWT_SIGNING_KEY = os.environ["JWT_SIGNING_KEY"]

# Email
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]


# Misc
ENVIRONMENT = os.environ["ENVIRONMENT"]
PRODUCTION_URL = os.environ["PRODUCTION_URL"]
LOCAL_URL = os.environ["LOCAL_URL"]
NINETY_SIX_HOURS = 96 * 60 * 60
