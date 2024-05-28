from app.models import User, Car

def test_user_model(init_database):
    user = User.query.first()
    assert user.username == 'alex'
    assert user.check_password('password') == True

def test_car_model(init_database):
    car = Car.query.first()
    assert car.maker == 'Nord'
    assert car.model == 'SUV'
    assert car.year == 2022
    assert car.price_per_day == 100
    assert car.availability == True
