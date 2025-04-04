from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import (DataRequired, Length, Email, EqualTo, Regexp, 
                               ValidationError)
import phonenumbers
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', 
               message='Username can only contain letters, numbers and underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)',
               message='Password must contain at least 1 digit, 1 lowercase, 1 uppercase, and 1 special character')
    ])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

    def validate_phone(self, phone):
        try:
            parsed = phonenumbers.parse(phone.data, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError('Invalid phone number')
            
            # Check if phone number already exists
            user = User.query.filter_by(phone_number=phone.data).first()
            if user:
                raise ValidationError('That phone number is already registered.')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError('Invalid phone number format')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RentalForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', 
                          validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', 
                        validators=[DataRequired()])
    submit = SubmitField('Book Now')

# Remove VerifyTokenForm since we're using email verification now

class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[
        DataRequired(),
        Length(min=16, max=16),
        Regexp(r'^\d{16}$', message='Card number must be 16 digits')
    ])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[
        DataRequired(),
        Regexp(r'^(0[1-9]|1[0-2])\/?([0-9]{2})$', 
               message='Invalid expiry date format (MM/YY)')
    ])
    cvv = StringField('CVV', validators=[
        DataRequired(),
        Regexp(r'^\d{3,4}$', message='CVV must be 3 or 4 digits')
    ])
    card_holder_name = StringField('Card Holder Name', 
                                  validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Pay Now')

# New form for resending verification email
class ResendVerificationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Verification Email')