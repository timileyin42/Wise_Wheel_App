document.addEventListener('DOMContentLoaded', function () {
    console.log('The page is ready.');

    // Show/hide password functionality
    const togglePassword = document.querySelector('#togglePassword');
    const passwordField = document.querySelector('#password');
    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', function () {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
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

    // Firebase OTP handling (updated to Firebase Modular SDK)
    import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js';
    import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js';

    fetch('/firebase-config')
        .then(response => response.json())
        .then(firebaseConfig => {
            // Initialize Firebase
            const app = initializeApp(firebaseConfig);
            const auth = getAuth(app);
	    console.log(firebaseConfig);
            console.log('Firebase initialized successfully.');

            // Initialize Recaptcha
            window.recaptchaVerifier = new RecaptchaVerifier('recaptcha-container', {
                size: 'invisible',
                callback: function () {
                    console.log('ReCAPTCHA solved!');
                }
            }, auth);

            const sendOtpBtn = document.getElementById('sendOtpBtn');
            const verifyOtpBtn = document.getElementById('verifyOtpBtn');

            // Send OTP Button Handler
            sendOtpBtn.addEventListener('click', function () {
                const phoneNumber = prompt('Enter your phone number (with country code):');
                const appVerifier = window.recaptchaVerifier;

                signInWithPhoneNumber(auth, phoneNumber, appVerifier)
                    .then(function (confirmationResult) {
                        console.log('OTP sent to phone number.');
                        window.confirmationResult = confirmationResult;
                        alert('OTP sent! Please check your phone.');

                        // Show the verify button
                        verifyOtpBtn.style.display = 'block';
                    })
                    .catch(function (error) {
                        console.error('Error sending OTP:', error);
                        alert('Failed to send OTP. Please try again.');
                    });
            });

            // Verify OTP Button Handler
            verifyOtpBtn.addEventListener('click', function () {
                const otpCode = prompt('Enter the OTP sent to your phone:');

                window.confirmationResult.confirm(otpCode)
                    .then(function (result) {
                        const user = result.user;

                        // Send the ID token to the backend
                        user.getIdToken()
                            .then(function (idToken) {
                                fetch('/verify_token', {
                                    method: 'POST',
                                    body: JSON.stringify({ token: idToken }),
                                    headers: { 'Content-Type': 'application/json' }
                                })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.success) {
                                            alert('Phone number verified successfully!');
                                            location.href = '/'; // Redirect to home page
                                        } else {
                                            alert('Verification failed. Please try again.');
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error during token verification:', error);
                                        alert('Error verifying token. Please try again.');
                                    });
                            });
                    })
                    .catch(function (error) {
                        console.error('Error verifying OTP:', error);
                        alert('Invalid OTP. Please try again.');
                    });
            });
        })
        .catch(error => {
            console.error('Error fetching Firebase config:', error);
        });
});

