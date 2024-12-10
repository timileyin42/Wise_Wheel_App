import os
import requests
import paystack
import json
import firebase_admin

from firebase_admin import auth
from firebase_admin import exceptions
from firebase_admin.exceptions import FirebaseError
from flask import render_template, url_for, flash, redirect, request, jsonify, send_from_directory, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, RentalForm, PaymentForm, VerifyTokenForm
from app.models import User, Car, Rental
from flask_login import login_user, current_user, logout_user, login_required
from config import Config
from app.utils.firebase_helpers import send_firebase_otp, verify_firebase_otp



paystack_secret_key = Config.PAYSTACK_SECRET_KEY
paystack.secret_key = paystack_secret_key
main = Blueprint(
    'main',
    __name__,
    template_folder='../templates',  # Path to templates folder
    static_folder='../static',      # Path to static folder
    static_url_path='/static'       # URL prefix for static files
)
print("Static folder (Blueprint):", os.path.abspath(os.path.join(__file__, '../static')))

@main.route("/")
@main.route("/home")
def home():
    """
    Displays the home page showing all available cars for rent.

    This view fetches all cars from the database and passes them to the 'home.html' template.
    """
    cars = Car.query.all()
    return render_template('home.html', cars=cars)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        print("Form is valid.")

        # Check for duplicate username and email
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username is already taken.', 'danger')
            return render_template('register.html', title='Register', form=form)

        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already registered.', 'danger')
            return render_template('register.html', title='Register', form=form)

        # Hash password and format phone number
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        phone_number = form.phone_number.data.strip()
        if not phone_number.startswith('+'):
            phone_number = f"+{phone_number}"

        # Save user to the database
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, phone_number=phone_number)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)  # Log in the user
            flash('Registration successful. Please verify your phone number.', 'info')
        except Exception as e:
            db.session.rollback()
            flash('Database error. Please try again.', 'danger')
            return render_template('register.html', title='Register', form=form)

        # Redirect to phone verification
        return redirect(url_for('main.verify_token'))

    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.verified:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.profile'))
            else:
                flash('Please verify your phone number first.', 'warning')
        else:
            flash('Login failed. Please check email and password.', 'danger')

    return render_template('login.html', title='Login', form=form)


@main.route("/profile")
@login_required
def profile():
    """
    Displays the user's profile.
    """
    user = current_user  # Gets the currently logged-in user
    return render_template('profile.html', title='Profile', user=user)


@main.route("/logout")
def logout():
    """
    Logs out the currently logged-in user and redirects to the home page.
    """

    logout_user()
    return redirect(url_for('main.home'))

@main.route("/car/<int:car_id>", methods=['GET', 'POST'])
@login_required
def car(car_id):
    """
    Shows details of a specific car and allows users to book it.

    On GET, displays the car details. On POST, validates the booking form data and redirects to the payment page.
    Requires the user to be logged in.
    """
    car = Car.query.get_or_404(car_id)
    form = RentalForm()
    if form.validate_on_submit():
        return redirect(url_for('main.payment', car_id=car.id))
    return render_template('car.html', title=car.model, car=car, form=form)

@main.route("/payment/<int:car_id>", methods=['GET', 'POST'])
@login_required
def payment(car_id):
    """
    Displays the payment page for a selected car.

    Fetches the car details and passes them along with the PayStack public key to the 'payment.html' template.
    Requires the user to be logged in.
    """

    car = Car.query.get_or_404(car_id)
    car_details = {'model': car.model, 'year': car.year, 'maker': car.maker, 'price_per_day': car.price_per_day}
    return render_template('payment.html', car=car, public_key=Config.PAYSTACK_PUBLIC_KEY)

@main.route("/verify_token", methods=['GET', 'POST'])
@login_required
def verify_token():
    if request.method == 'GET':
        # Render the token verification page
        return render_template('verify_token.html', phone_number=current_user.phone_number)

    if request.method == 'POST':
        data = request.get_json()
        otp_token = data.get('token')

        if not otp_token:
            return jsonify({"error": "Token is required"}), 400

        try:
            # Verify the token using Firebase
            decoded_token = auth.verify_id_token(otp_token)
            if decoded_token:
                current_user.verified = True
                db.session.commit()
                flash('Phone number verified successfully!', 'success')
                return jsonify({"success": "Verification complete"}), 200
            else:
                return jsonify({"error": "Invalid or expired token"}), 400
        except Exception as e:
            return jsonify({"error": f"Verification failed: {str(e)}"}), 500


@main.route("/create-checkout-session/<int:car_id>", methods=['POST'])
@login_required
def create_checkout_session(car_id):
    """
    Initializes a new transaction on PayStack for the selected car.

    Creates a checkout session with the car's price and the user's email, then returns the session ID.
    Requires the user to be logged in.
    """

    car = Car.query.get_or_404(car_id)
    session = paystack.Transaction.initialize(reference=f'car_{car.id}',
            amount=int(car.price_per_day * 100),
            email=current_user.email,
            callback_url=url_for('main.success', car_id=car.id, _external=True))
    return jsonify({'id': session['data']['reference']})

@main.route("/success/<int:car_id>")
@login_required
def success(car_id):
    """
    Marks a car as unavailable after a successful payment.

    Updates the car's availability status in the database and flashes a success message.
    Redirects to the home page.
    Requires the user to be logged in.
    """

    car = Car.query.get_or_404(car_id)
    car.availability = False
    db.session.commit()
    flash('Payment successful! Your car has been booked.', 'success')
    return redirect(url_for('main.home'))

@main.route("/cancel")
@login_required
def cancel():
    """
    Handles payment cancellation.

    Flashes a cancellation message and redirects to the home page.
    Requires the user to be logged in.
    """

    flash('Payment canceled. Please try again.', 'try again')
    return redirect(url_for('main.home'))

@main.route("/send_token", methods=['POST'])
@login_required
def send_token():
    """
    Initiates the OTP process for the user's phone number.

    This route ensures that the user's phone number is registered in Firebase and prepares
    the backend for OTP verification. The client-side will handle sending the OTP via Firebase SDK.
    """

    phone_number = current_user.phone  # Assuming `phone` is a field in your User model

    try:
        # Check if the user exists in Firebase by phone number
        try:
            auth.get_user_by_phone_number(phone_number)
            flash('Phone number already registered with Firebase.', 'info')
        except auth.UserNotFoundError:
            # Create a user in Firebase if not already present
            auth.create_user(phone_number=phone_number)
            flash('User created in Firebase. Proceed with OTP verification.', 'info')

        # You can track this action or create a session if needed
        # Optionally, store a verification status flag in the User model
        current_user.verification_status = 'initiated'  # Add this in your User model if needed
        db.session.commit()

        # Inform the frontend to trigger the OTP process
        flash('Verification initiated. Follow the instructions sent to your phone.', 'info')
    except FirebaseError as e:
        print(f"Error initializing verification: {e}")
        flash('Failed to initiate verification. Please try again.', 'danger')

    return redirect(url_for('main.verify_token'))

@main.route('/firebase-config', methods=['GET'])
def firebase_config():
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }

    # Check if any of the environment variables are missing
    missing_keys = [key for key, value in firebase_config.items() if not value]
    if missing_keys:
        return jsonify({"error": f"Missing environment variables: {', '.join(missing_keys)}"}), 500

    return jsonify(firebase_config)
