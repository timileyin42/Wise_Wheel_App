from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    """
    Form for user registration.

    Fields:
    - username: A string with minimum length of 2 and maximum length of 20 characters.
    - email: A string that must contain a valid email address.
    - password: A string that must meet the DataRequired validator.
    - confirm_password: Must be equal to the password field.
    - phone: A string with minimum length of 10 and maximum length of 15 characters, validated against a regular expression for E.164 phone number format.
    - submit: A submit button labeled "Sign Up".
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^\+?[1-9]\d{9,14}$', message="Invalid phone number format.")
    ])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    """
    Form for user login.

    Fields:
    - email: A string that must contain a valid email address.
    - password: A string that must meet the DataRequired validator.
    - remember: A boolean field to remember the user.
    - submit: A submit button labeled "Login".
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RentalForm(FlaskForm):
    """
    Form for booking a car rental.

    Fields:
    - start_date: A date field for the start date of the rental, required.
    - end_date: A date field for the end date of the rental, required.
    - submit: A submit button labeled "Book Now".
    """
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Book Now')

class VerifyTokenForm(FlaskForm):
    """
    Form for verifying a token.

    Fields:
    - token: An integer field for the token to be verified, required.
    - submit: A submit button labeled "Verify".
    """
    token = IntegerField('Token', validators=[DataRequired()])
    submit = SubmitField('Verify')

class PaymentForm(FlaskForm):
    """
    Form for processing payments.

    Fields:
    - card_number: A string field for the card number, required, with a length constraint of exactly 16 characters.
    - expiry_date: A string field for the card's expiry date, required, with a length constraint of exactly 5 characters (MM/YY).
    - cvv: A string field for the CVV, required, with a length constraint of 3 or 4 characters.
    - card_holder_name: A string field for the card holder's name, required.
    - email: A string field for the customer's email, required, with a valid email format.
    - submit: A submit button labeled "Pay Now".
    """
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired(), Length(min=5, max=5)])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4)])
    card_holder_name = StringField('Card Holder Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Pay Now')
