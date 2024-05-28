import pytest
from app import db
from app.models import User, Car, Rental
from datetime import datetime

def test_user_model(init_database):
    user = User.query.first()
    assert user.username == 'Alex'
    assert user.email == 'alexbuddy@gmail.com'
    assert user.check_password('password') == True
    assert user.image_file == 'default.jpg'
    assert user.authy_id is None


def test_set_password(init_database):
    user = User.query.first()
    user.set_password('newpassword')
    assert user.check_password('newpassword') == True


def test_car_model(init_database):
    car = car.query.first()
    assert car.maker == 'Nord'
    assert car.model == 'SUV'
    assert car.year == 2022
    assert car.price_per_day == 50.0
    assert car.availability == True


def test_rental_model(init_database):
    user = User.query.first()
    car = Car.query.first()
    rental = Rental(
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        total_amount= 100.0,
        payment_status=False,
        car_id=car.id,
        user_id=user.id
    )
    db.session.add(rental)
    db.session.commit()


    assert rental.id is not None
    assert rental.total_amount == 100.0
    assert rental.payment_status == False
    assert rental.car_id == car.id
    assert rental.user_id == user.id
    assert rental.start_date <= datetime.utcnow()
    assert rental.end_date <= datetime.utcnow()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    user = User(username='Alex', email='alexbuddy@gmail.com', password='password', phone='08124799371')
    user.set_password('password')
    db.session.add(user)


    car = Car(maker='Nord', model='SUV', year=2022, price_per_day=50.0, availability=True)
    db.session.commit()


    yield db


    db.session.remove()
    db.drop_all()
