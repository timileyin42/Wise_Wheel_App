import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

login_manager.login_message_category = 'info'

def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',       # Path for static files
        static_url_path='/static'     # URL prefix for static files
    )
    app.config.from_object('config.Config')

    print("Static folder (Flask app):", app.static_folder)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Initialize Firebase Admin
    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS environment variable is not set.")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")

    # Register blueprints
    from app.routes import main
    main.static_folder = 'static'
    app.register_blueprint(main, template_folder='../templates', url_prefix='/')

    return app

