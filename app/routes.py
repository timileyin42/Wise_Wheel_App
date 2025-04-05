import os
import requests
import json
from flask import render_template, url_for, flash, redirect, request, jsonify, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, RentalForm, PaymentForm
from app.models import User, Car, Rental
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from config import Config
from app.utils import send_email


paystack_secret_key = Config.PAYSTACK_SECRET_KEY
paystack_public_key = Config.PAYSTACK_PUBLIC_KEY

main = Blueprint('main', __name__)
main = Blueprint('main', __name__, template_folder='../templates')


@main.route("/")
@main.route("/home")
def home():
    """
    Displays the home page showing all available cars for rent.

    This view fetches all cars from the database and passes them to the 'home.html' template.
    """
    cars = Car.query.all()
    return render_template('home.html', cars=cars)

@main.route('/debug-templates')
def debug_templates():
    with app.app_context():
        from flask import render_template
        try:
            # Test rendering
            test_render = render_template('home.html', cars=[])
            return "Template found and rendered successfully!"
        except Exception as e:
            return f"Template error: {str(e)}"

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return redirect(url_for('main.register'))
        
        # Create user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            phone_number=form.phone.data,
            is_verified=False
        )
        
        # Generate verification token
        token = user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        verification_url = url_for(
            'main.verify_email',
            token=token,
            _external=True
        )
        
        send_email(
            to_email=user.email,
            subject="Verify Your Email - WiseWheel",
            html_content=render_template(
                'email/verify_email.html',
                user=user,
                verification_url=verification_url
            )
        )
        
        flash('A verification email has been sent. Please check your inbox.', 'info')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user or datetime.utcnow() > user.token_expiration:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('main.register'))
    
    if user.verify_token(token):
        flash('Your email has been verified! You can now log in.', 'success')
    else:
        flash('Verification failed.', 'danger')
    
    return redirect(url_for('main.login'))

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('main.login'))
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check email and password', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/resend-verification', methods=['POST'])
@login_required
def resend_verification():
    if current_user.is_verified:
        return redirect(url_for('main.home'))
    
    token = current_user.generate_verification_token()
    db.session.commit()
    
    verification_url = url_for(
        'main.verify_email',
        token=token,
        _external=True
    )
    
    send_email(
        to_email=current_user.email,
        subject="Verify Your Email - WiseWheel",
        html_content=render_template(
            'email/verify_email.html',
            user=current_user,
            verification_url=verification_url
        )
    )
    
    flash('A new verification email has been sent.', 'info')
    return redirect(url_for('main.login'))

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
    """Show car details and handle rental booking"""
    car = Car.query.get_or_404(car_id)
    
    # Ensure car is available
    if not car.availability:
        flash('This car is no longer available', 'warning')
        return redirect(url_for('main.home'))
    
    form = RentalForm()
    
    if form.validate_on_submit():
        # Calculate rental duration and total cost
        rental_days = (form.end_date.data - form.start_date.data).days
        if rental_days <= 0:
            flash('End date must be after start date', 'danger')
            return redirect(url_for('main.car', car_id=car.id))
        
        total_amount = rental_days * car.price_per_day
        
        # Create rental record
        rental = Rental(
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_amount=total_amount,
            car_id=car.id,
            user_id=current_user.id
        )
        
        db.session.add(rental)
        db.session.commit()
        
        return redirect(url_for('main.payment', rental_id=rental.id))
    
    return render_template('car.html', car=car, form=form)

@main.route("/payment/<int:rental_id>", methods=['GET'])
@login_required
def payment(rental_id):
    """Show payment page for a rental"""
    rental = Rental.query.get_or_404(rental_id)
    
    # Verify rental belongs to current user
    if rental.user_id != current_user.id:
        flash('You are not authorized to view this page', 'danger')
        return redirect(url_for('main.home'))
    
    # Verify car is still available
    car = Car.query.get_or_404(rental.car_id)
    if not car.availability:
        flash('This car is no longer available', 'warning')
        return redirect(url_for('main.home'))
    
    return render_template(
        'payment.html',
        rental=rental,
        car=car,
        public_key=Config.PAYSTACK_PUBLIC_KEY)

@main.route("/create-checkout-session/<int:car_id>", methods=['POST'])  
@login_required
def create_checkout_session(car_id):
    car = Car.query.get_or_404(car_id)
    if car.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        result = paystack_initialize_transaction(
            email=current_user.email,
            amount=car.price_per_day,
            reference=f'car_{car.id}',
            callback_url=url_for('main.payment_success', car_id=car.id, _external=True)
        )
        
        if result.get('status'):
            return jsonify({
                'authorization_url': result['data']['authorization_url'],
                'access_code': result['data']['access_code']
            })
        else:
            return jsonify({'error': result.get('message', 'Payment initialization failed')}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route("/payment-success/<int:rental_id>")
@login_required
def payment_success(rental_id):
    """Handle successful payment callback"""
    rental = Rental.query.get_or_404(rental_id)
    
    if rental.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    car = Car.query.get_or_404(rental.car_id)
    car.availability = False
    rental.payment_status = True
    db.session.commit()
    
    # Send booking confirmation email
    send_booking_email(
        user=current_user,
        subject="Booking Confirmation",
        template='email/booking_confirmation.html',
        rental=rental,
        car=car
    )
    
    flash('Payment successful! Your booking is confirmed.', 'success')
    return redirect(url_for('main.booking_confirmation', rental_id=rental.id))

@main.route("/booking-confirmation/<int:rental_id>")
@login_required
def booking_confirmation(rental_id):
    """Show booking confirmation details"""
    rental = Rental.query.get_or_404(rental_id)
    
    if rental.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('booking_confirmation.html', rental=rental)

@main.route("/payment-cancel/<int:rental_id>")
@login_required
def payment_cancel(rental_id):
    """Handle payment cancellation"""
    rental = Rental.query.get_or_404(rental_id)
    
    if rental.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    # Delete the rental record if payment was cancelled
    if not rental.payment_status:
        db.session.delete(rental)
        db.session.commit()
        flash('Booking cancelled', 'info')
    
    return redirect(url_for('main.home'))

@main.route("/my-bookings")
@login_required
def my_bookings():
    """Show current user's booking history"""
    # Get all rentals for current user, ordered by most recent
    rentals = Rental.query.filter_by(user_id=current_user.id)\
                         .order_by(Rental.start_date.desc())\
                         .all()
    
    # Separate into upcoming and past rentals
    now = datetime.utcnow()
    upcoming = [r for r in rentals if r.start_date > now]
    past = [r for r in rentals if r.start_date <= now]
    
    return render_template('my_bookings.html', 
                         upcoming=upcoming, 
                         past=past)


@main.route("/cancel-booking/<int:rental_id>", methods=['POST'])
@login_required
def cancel_booking(rental_id):
    """Cancel a booking with proper constraints"""
    rental = Rental.query.get_or_404(rental_id)
    
    # Authorization check
    if rental.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    # Time constraint - can't cancel within 24 hours of start
    if datetime.utcnow() > rental.start_date - timedelta(hours=24):
        flash('Cannot cancel booking within 24 hours of rental start', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    # Refund logic would go here (integration with Paystack refund API)
    
    # Mark car as available again
    car = Car.query.get_or_404(rental.car_id)
    car.availability = True
    
    # Send cancellation email
    send_booking_email(
        user=current_user,
        subject="Booking Cancellation",
        template='email/cancel_booking.html',
        rental=rental
    )
    
    # Delete the rental record
    db.session.delete(rental)
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('main.my_bookings'))

def send_booking_email(user, subject, template, **kwargs):
    """Send booking-related emails using Mailjet"""
    # Render the HTML template
    html_content = render_template(template, user=user, **kwargs)
    
    # Mailjet API request
    mailjet_url = "https://api.mailjet.com/v3.1/send"
    auth = (current_app.config['MAILJET_API_KEY'], 
            current_app.config['MAILJET_API_SECRET'])
    
    data = {
        "Messages": [{
            "From": {
                "Email": current_app.config['MAILJET_SENDER_EMAIL'],
                "Name": current_app.config['MAILJET_SENDER_NAME']
            },
            "To": [{
                "Email": user.email,
                "Name": user.username
            }],
            "Subject": subject,
            "HTMLPart": html_content
        }]
    }
    
    try:
        response = requests.post(
            mailjet_url,
            json=data,
            auth=auth,
            timeout=10  # seconds
        )
        
        if response.status_code != 200:
            current_app.logger.error(
                f"Mailjet API error: {response.status_code} - {response.text}"
            )
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")


def paystack_initialize_transaction(email, amount, reference, callback_url):
    paystack_secret_key = Config.PAYSTACK_SECRET_KEY
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": str(int(amount * 100)),  # Paystack expects amount in kobo
        "reference": reference,
        "callback_url": callback_url
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@main.route('/template-test')
def template_test():
    try:
        return render_template('home.html', cars=[])
    except Exception as e:
        return f"Template error: {str(e)}"
