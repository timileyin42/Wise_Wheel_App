document.addEventListener('DOMContentLoaded', function() {
    console.log('The page is ready');

    function showAlert(message) {
        alert(message);
    }

    showAlert("Welcome");

    // Show/hide password functionality
    const togglePassword = document.querySelector('#togglePassword');
    const passwordField = document.querySelector('#password');
    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', function (e) {
            // Toggle the type attribute
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            // Toggle the eye slash icon
            this.classList.toggle('fa-eye-slash');
        });
    }

    // Real-time search filter for cars
    const carSearch = document.querySelector('#carSearch');
    const carList = document.querySelectorAll('.car-item');
    if (carSearch && carList.length > 0) {
        carSearch.addEventListener('input', function () {
            const filter = carSearch.value.toLowerCase();
            carList.forEach(function (car) {
                const carName = car.querySelector('.car-name').textContent.toLowerCase();
                if (carName.includes(filter)) {
                    car.style.display = '';
                } else {
                    car.style.display = 'none';
                }
            });
        });
    }
});

