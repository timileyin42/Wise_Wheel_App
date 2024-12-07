import os
import requests
import paystack
import json
from authy.api import AuthyApiClient
from flask import render_template, url_for, flash, redirect, request, jsonify, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, RentalForm, VerifyTokenForm, PaymentForm
from app.models import User, Car, Rental
from flask_login import login_user, current_user, logout_user, login_required
from config import Config
from twilio.rest import Client

account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

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
        print(f"Checking username: {existing_user}")

        if existing_user:
            flash('Username is already taken.', 'danger')
            print("Duplicate username found.")
            return render_template('register.html', title='Register', form=form)

        existing_email = User.query.filter_by(email=form.email.data).first()
        print(f"Checking email: {existing_email}")

        if existing_email:
            flash('Email is already registered.', 'danger')
            print("Duplicate email found.")
            return render_template('register.html', title='Register', form=form)

        print("Hashing password.")
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        phone_number = form.phone.data.strip()
        if not phone_number.startswith('+'):
            phone_number = f"+{phone_number}"
            print(f"Formatted phone number: {phone_number}")

        # Save user to database
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            print("User successfully added.")
        except Exception as e:
            print("Database error:", e)
            flash('Database error. Please try again.', 'danger')
            return render_template('register.html', title='Register', form=form)

        # Send SMS verification
        try:
            print("Sending verification SMS.")
            verification = client.verify \
                .services(Config.VERIFY_SERVICE_ID) \
                .verifications \
                .create(to=phone_number, channel="sms")
            print("Verification status:", verification.status)

            if verification.status == "queued":
                flash('A verification code has been sent to your phone.', 'info')
            else:
                flash('Failed to send verification code.', 'danger')
        except Exception as e:
            print("Verification error:", e)
            flash('Error sending verification code.', 'danger')
            return render_template('register.html', title='Register', form=form)

        return redirect(url_for('main.login'))

    print("Form errors: ", form.errors)
    return render_template('register.html', title='Register', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    """
    Manages user login.

    On GET, displays the login form. On POST, validates the form data, checks if the user exists and the password matches,
    logs the user in, and redirects to the home page or the previously requested page.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.profile'))
        else:
            flash('Login failed. Please check email and password', 'try again')
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

@main.route("/payment/<int:car_id>", methods=['GET'])
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

@main.route("/verify_token", methods=['POST'])
@login_required
def verify_token():
    """
    Verifies the twilio token sent via SMS to the user's phone.

    On POST, validates the token against the user's Authy ID. Upon successful verification, redirects to the home page.
    Requires the user to be logged in.
    """

    form = VerifyTokenForm()
    if form.validate_on_submit():
        token = form.token.data
        verification_check = client.verify \
            .services(Config.VERIFY_SERVICE_ID) \
            .verification_checks \
            .create(to=phone_number, code=token)

        if verification_check.status == "approved":
            flash('Token verified successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Failed to verify token.', 'error')

    return render_template('verify_token.html', form=form)

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
    Sends a verification token to the user's phone via SMS.

    Uses the user's Authy ID to send the token and redirects to the verify token page.
    Requires the user to be logged in.
    """

    verification = client.verify \
            .services(Config.VERIFY_SERVICE_ID) \
            .verifications \
            .create(to=phone_number, channel="sms")

    if verification.status == "queued":
        flash('Verification token sent to your phone.', 'info')
    else:
        flash('Failed to send verification token.', 'try again!')
    return redirect(url_for('main.verify_token'))
