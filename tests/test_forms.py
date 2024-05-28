from app.forms import RegistrationForm, LoginForm

def test_registration_form():
    form = RegistrationForm(data={
        'username': 'Alex',
        'email': 'alexbuddy@gmail.com',
        'phone': '08124799371
