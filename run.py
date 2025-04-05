#!/usr/bin/env python
from app import create_app, db
from app.models import User, Car, Rental
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Make shell context for Flask CLI"""
    return {
        'db': db,
        'User': User,
        'Car': Car,
        'Rental': Rental,
        # Add other models as needed
    }

if __name__ == '__main__':
    # Configuration
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True,  # Handle multiple requests simultaneously
        # ssl_context='adhoc'  # Uncomment for HTTPS during development
    )