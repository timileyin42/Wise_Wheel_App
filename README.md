# WiseWheel Rental Web Application

## Project Description

This is a car rental web application built using the Flask framework. it allow user to Register, Log in, and book cars for rental. The applications integrate with several external APIs for authentication, payment processing, and location services

## Features

- User Registration and Authentication
- Car Listing and Booking
- Google Maps integration for Location Services
- Two-Factor Authentication with Twilio Authy
- Payment Processing with Paystack
- Google Calendar Integration for Booking Management

## Technology Stack

- Python with Flask Framework
- HTML, CSS, JavaScript(with PyScript)

# Key Funtionalities

### User Management

1. **User Registration**:
   - Users can create an account by providing a username, email, phone number, and password.
   - Email validation ensures that the email address provided is in the correct format.
   - Phone number validation ensures the phone number is within a specified length and format.

2. **User Login**:
   - Registered users can log in using their email and password.
   - Option to remember the user with a "Remember Me" checkbox.
   - Integration with Twilio Authy for two-factor authentication (2FA).

3. **User Authentication**:
   - Secure password storage using hashing with Flask-Bcrypt.
   - User sessions are managed using Flask-Login.
   - Users are required to verify their identity using an Authy token sent via SMS.

### Car Management

4. **Car Listing**:
   - Display a list of available cars for rental with details such as maker, model, year, and daily rental price.
   - Only cars marked as available can be rented.

5. **Car Booking**:
   - Users can select a car and book it for a specified rental period by providing start and end dates.
   - Calculation of total rental cost based on the rental period and daily price.
   - Google Maps integration to show the location of available cars.

### Rental Management

6. **Booking Management**:
   - Users can view their booking history and manage their active bookings.
   - Integration with Google Calendar to manage and remind users of their bookings.

### Payment Processing

7. **Payment Integration**:
   - Users can make payments for their bookings using the Paystack payment gateway.
   - Payment details including card number, expiry date, CVV, and card holder name are securely collected.
   - Confirmation of payment status and handling of successful and failed transactions.

### Additional Features

8. **Database Management**:
   - Use of SQLAlchemy ORM for database interactions.
   - Database migrations managed with Flask-Migrate.

9. **Form Handling**:
   - Use of Flask-WTF for form creation and validation.
   - Custom validators for email, phone number, and password confirmation.

10. **API Integrations**:
    - **Google Maps API**: Display car locations on a map.
    - **Twilio Authy API**: Two-factor authentication via SMS.
    - **Paystack API**: Secure payment processing.
    - **Google Calendar API**: Manage and remind users of their bookings.

### Security

11. **Session Management**:
    - User sessions are securely managed to ensure that users remain logged in as they navigate the site.
    - Login required for accessing specific routes, ensuring only authenticated users can book and manage rentals.

### Notifications

12. **Booking Confirmation and Reminders**:
    - Email notifications for booking confirmations.
    - Reminders for upcoming bookings via Google Calendar.

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- virtualenv (optional but recommended)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/timileyin42/Wise_Wheel_App.git
    cd Wise_Wheel_App
    ```

2. **Set up a virtual environment:**

    ```bash
    python3 -m venv venv
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add the following content, replacing placeholder values with your actual API keys and secret keys:

    ```ini
    SECRET_KEY=your_secret_key
    SQLALCHEMY_DATABASE_URI=sqlite:///site.db
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    VERIFY_SERVICE_ID=your_verify_service_id
    PAYSTACK_PUBLIC_KEY=your_paystack_public_key
    PAYSTACK_SECRET_KEY=your_paystack_secret_key
    ```

5. **Run database migrations:**

    ```bash
    flask db upgrade
    ```

### Running the Application

1. **Start the Flask development server:**

    ```bash
    python run.py
    ```

2. **Access the application in your web browser:**

    Open `http://127.0.0.1:5000` in your web browser.

## Testing

To run the test cases for this project, use the following command:

```bash
pytest
```

## Usage

- **Register an Account:** Go to the registration page and create a new user account.
- **Log In:** Use your credentials to log in to the application.
- **Browse Cars:** View the available cars for rental.
- **Book a Car:** Select a car and book it for your desired dates.
- **Payment:** Complete the payment process using Paystack.
- **Two-Factor Authentication:** Verify your identity using Twilio Authy.
- **View Bookings:** Check your bookings and manage them using the integrated Google Calendar.


# AUTHORS
Akanmu Ibrahim Timileyin | akanmuibro@gmail.com 
