import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
    MAILJET_API_SECRET = os.getenv('MAILJET_API_SECRET')
    MAILJET_SENDER_EMAIL = 'no-reply@yourdomain.com'
    MAILJET_SENDER_NAME = 'Wise Wheel App'
    TEMPLATES_AUTO_RELOAD = True