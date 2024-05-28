import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-need_the_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    AUTHY_API_KEY = os.environ.get('AUTHY_API_KEY')
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')

