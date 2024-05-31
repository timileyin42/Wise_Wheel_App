from app.forms import RegistrationForm, LoginForm, RentalForm, PaymentForm

def test_registration_form():
    form = RegistrationForm(data={
        'username': 'Alex',
        'email': 'alexbuddy@gmail.com',
        'phone': '08124799371',
        'password': 'securepassword',
        'confirm_password': 'securepassword'
    })

    form.validate()

    assert form.username.data == 'Alex'
    assert form.email.data == 'alexbuddy@gmail.com'
    assert form.phone.data == '08124799371'
    assert form.password.data == 'securepassword'
    assert form.confirm_password.data == 'securepassword

    assert form.validate_on_submit()
