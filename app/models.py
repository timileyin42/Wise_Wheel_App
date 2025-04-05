from datetime import datetime, timedelta
from app import db, login_manager
from flask_login import UserMixin
import secrets
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user instance from the database based on the given user ID.
    Args:
        user_id (int): The ID of the user to load.
    Returns:
        User: The loaded user instance if found, None otherwise.
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Represents a user in the system.
    Attributes:
        id (int): Unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        image_file (str): The filename for the user's profile picture.
        password (str): The encrypted password of the user.
        phone_number (str): The user's phone number.
        is_verified (bool): Whether the user's email is verified.
        rentals (list): A relationship to Rental instances.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), unique=True)
    token_expiration = db.Column(db.DateTime)
    rentals = db.relationship('Rental', backref='renter', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user') 

    def generate_verification_token(self, expires_in=3600):
        """Generate email verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        return self.verification_token
    
    def verify_token(self, token):
        """Verify the email verification token"""
        if self.verification_token != token:
            return False
        if datetime.utcnow() > self.token_expiration:
            return False
        self.is_verified = True
        self.verification_token = None
        db.session.commit()
        return True

    def set_password(self, plain_text_password):
        """Hash and set password"""
        self.password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, plain_text_password):
        """Check password against hash"""
        return bcrypt.check_password_hash(self.password, plain_text_password)
    @property
    def is_verified(self):
        return self.verified

class Car(db.Model):
    """
    Represents a car available for rent.
    Attributes:
        id (int): Unique identifier for the car.
        maker (str): The make of the car.
        model (str): The model of the car.
        year (int): The manufacturing year of the car.
        price_per_day (float): The daily rental price.
        availability (bool): Whether the car is available.
    """
    id = db.Column(db.Integer, primary_key=True)
    maker = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    image_file = db.Column(db.String(20), nullable=False, default='car_default.jpg')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Rental(db.Model):
    """
    Represents a rental booking.
    Attributes:
        id (int): Unique identifier.
        start_date (datetime): Rental start date.
        end_date (datetime): Rental end date.
        total_amount (float): Total cost.
        payment_status (bool): Payment status.
        car_id (int): Associated car ID.
        user_id (int): Associated user ID.
    """
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

