from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

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
        authy_id (str): The Authy ID for SMS verification.
        rentals (list): A relationship to Rental instances representing bookings made by the user.

    Methods:
        set_password(plain_text_password): Sets the user's password hash.
        check_password(plain_text_password): Checks a plain text password against the stored hash.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    authy_id = db.Column(db.String(50))
    rentals = db.relationship('Rental', backref='renter', lazy=True)

    def set_password(self, plain_text_password):
        """Hash a plain text password and store it in this user's record."""
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, plain_text_password):
        """Check a plain text password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, plain_text_password)

class Car(db.Model):
    """
    Represents a car available for rent.

    Attributes:
        id (int): Unique identifier for the car.
        maker (str): The make of the car.
        model (str): The model of the car.
        year (int): The manufacturing year of the car.
        price_per_day (float): The daily rental price of the car.
        availability (bool): Indicates whether the car is available for rent.
    """

    id = db.Column(db.Integer, primary_key=True)
    maker = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)

class Rental(db.Model):
    """
    Represents a rental booking made by a user for a car.

    Attributes:
        id (int): Unique identifier for the rental.
        start_date (datetime): The start date and time of the rental period.
        end_date (datetime): The end date and time of the rental period.
        total_amount (float): The total cost of the rental.
        payment_status (bool): Indicates whether the rental has been paid for.
        car_id (int): The ID of the car rented.
        user_id (int): The ID of the user who made the booking.
    """

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
