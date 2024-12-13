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
from app.forms import RegistrationForm, LoginForm, RentalForm, PaymentForm, VerifyTokenForm, SendTokenForm
from app.models import User, Car, Rental
from flask_login import login_user, current_user, logout_user, login_required
from config import Config
from app.utils.firebase_helpers import send_firebase_otp


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

@main.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration.

    After successful registration, the user is redirected to the send_token route to initiate phone number verification.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Check for duplicate username and email
        if User.query.filter_by(username=form.username.data).first():
            flash('Username is already taken.', 'danger')
            return render_template('register.html', title='Register', form=form)

        if User.query.filter_by(email=form.email.data).first():
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

        # Redirect to send_token route to initiate phone verification
        return redirect(url_for('main.send_token'))

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

@main.route("/verify_token", methods=["GET", "POST"])
@login_required
def verify_token():
    """
    Verifies the OTP token submitted by the user.
    
    Uses VerifyTokenForm for user input and communicates with Firebase to verify the token.
    """
    form = VerifyTokenForm()

    if form.validate_on_submit():
        otp_token = form.token.data

        try:
            # Verify the token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(otp_token)
            if decoded_token:
                # Mark the current user as verified
                current_user.verified = True
                db.session.commit()

                flash('Phone number verified successfully!', 'success')
                return jsonify({"success": True, "message": "Phone number verified successfully!"})
            else:
                return jsonify({"success": False, "message": "Invalid or expired token."}), 400

        except ValueError as ve:
            print(f"Token verification failed: {ve}")
            return jsonify({"success": False, "message": "Invalid token format."}), 400

        except Exception as e:
            print(f"Verification error: {e}")
            return jsonify({"success": False, "message": "Verification failed. Please try again later."}), 500

    return render_template('verify_token.html', title="Verify OTP", form=form)

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

@main.route("/send_token", methods=["GET", "POST"])
@login_required
def send_token():
    """
    Initiates the OTP process for the user's phone number.

    Uses Firebase Authentication to handle OTP sending and user registration if needed.
    """
    phone_number = current_user.phone_number  # Assuming `phone_number` exists in your User model

    if not phone_number:
        flash('Phone number is missing. Please update your profile.', 'danger')
        return redirect(url_for('main.profile'))

    if request.method == "POST":
        try:
            # Check or create Firebase user for the phone number
            try:
                auth.get_user_by_phone_number(phone_number)
                flash('Phone number is already registered with Firebase.', 'info')
            except auth.UserNotFoundError:
                auth.create_user(phone_number=phone_number)
                flash('User created successfully in Firebase.', 'success')

            flash('Verification initiated. Follow the instructions sent to your phone.', 'info')
        except FirebaseError as e:
            print(f"Firebase error: {e}")
            flash('Failed to initiate verification. Please try again later.', 'danger')
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash('An unexpected error occurred. Please try again later.', 'danger')

        return redirect(url_for('main.verify_token'))  # Adjust as needed for your flow

    return render_template('send_token.html', title="Send OTP", phone_number=phone_number)


@main.route('/firebase-config', methods=['GET'])
def firebase_config():
    """
    Provides Firebase configuration to the frontend securely.
    """
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
    }

    missing_keys = [key for key, value in firebase_config.items() if not value]
    if missing_keys:
        return jsonify({"error": f"Missing environment variables: {', '.join(missing_keys)}"}), 500

    return jsonify(firebase_config)
