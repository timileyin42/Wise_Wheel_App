from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
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

    db.init_app(app)

    migrate = Migrate(app, db)

    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes import main
    main.static_folder = 'static' 
    app.register_blueprint(main, template_folder='../templates')

    return app

