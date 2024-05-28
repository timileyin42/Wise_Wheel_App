import pytest
from flask import url_for
from app import create_app, db
from app.models import User, Car, Rental
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            # Create the database and the database table(s)
            db.create_all()
            yield testing_client
            db.drop_all()

@pytest.fixture(scope='module')
def init_database(test_client):
    user = User(username='Alex', email='alexbuddy@gmail.com', authy_id='123456')
    user.set_password('password')
    db.session.add(user)

    car = Car(maker='Nord', model='SUV', year=2022, price_per_day=50.0, availability=True)
    db.session.add(car)

    # Commit the changes for the models
    db.session.commit()

@pytest.fixture(scope='module')
def login_default_user(test_client):
    test_client.post('/login', data=dict(
        email='alexbuddy@gmail.com',
        password='password'
    ), follow_redirects=True)

def test_home_page(test_client, init_database):
    response = test_client.get(url_for('main.home'))
    assert response.status_code == 200
    assert b'Available Cars' in response.data

def test_register(test_client):
    response = test_client.post(url_for('main.register'), data={
        'username': 'Alex',
        'email': 'alexbuddy@gmail.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'phone': '08124799371'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Verification token sent to your phone.' in response.data

def test_login(test_client, init_database):
    response = test_client.post(url_for('main.login'), data={
        'email': 'alexbuddy@example.com',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Available Cars' in response.data

def test_car_page(test_client, init_database):
    car = Car.query.first()
    response = test_client.get(url_for('main.car', car_id=car.id))
    assert response.status_code == 200
    assert b'Nord SUV' in response.data

def test_payment_page(test_client, init_database, login_default_user):
    car = Car.query.first()
    response = test_client.get(url_for('main.payment', car_id=car.id))
    assert response.status_code == 200
    assert b'Pay' in response.data

def test_create_checkout_session(test_client, init_database, login_default_user):
    car = Car.query.first()
    response = test_client.post(url_for('main.create_checkout_session', car_id=car.id))
    assert response.status_code == 200
    assert b'id' in response.data

def test_send_token(test_client, init_database, login_default_user):
    response = test_client.post(url_for('main.send_token'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Verification token sent to your phone.' in response.data

def test_verify_token(test_client, init_database, login_default_user):
    response = test_client.post(url_for('main.verify_token'), data={
        'token': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your account has been verified!' in response.data

def test_rental_booking(test_client, init_database, login_default_user):
    car = Car.query.first()
    response = test_client.post(url_for('main.book_rental', car_id=car.id), data={
        'start_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'end_date': (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Booking successful!' in response.data

def test_google_map_api(test_client):
    response = test_client.get(url_for('main.map'))
    assert response.status_code == 200
    assert b'<div id="map">' in response.data

def test_google_calendar_integration(test_client):
    response = test_client.get(url_for('main.calendar'))
    assert response.status_code == 200
    assert b'Google Calendar Integration' in response.data

