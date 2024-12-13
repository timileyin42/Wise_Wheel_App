document.addEventListener('DOMContentLoaded', function () {
    console.log('The page is ready.');

    import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js';
    import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from 'https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js';

    fetch('/firebase-config')
        .then(response => response.json())
        .then(firebaseConfig => {
            // Initialize Firebase
            const app = initializeApp(firebaseConfig);
            const auth = getAuth(app);
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
            sendOtpBtn.addEventListener('click', async function () {
                const phoneNumber = document.querySelector('#phoneNumber').value;
                if (!phoneNumber) {
                    alert('Please enter a valid phone number.');
                    return;
                }

                const appVerifier = window.recaptchaVerifier;

                try {
                    const confirmationResult = await signInWithPhoneNumber(auth, phoneNumber, appVerifier);
                    console.log('OTP sent successfully.');
                    window.confirmationResult = confirmationResult;
                    alert('OTP sent! Please check your phone.');

                    // Show the verify button
                    verifyOtpBtn.style.display = 'block';
                } catch (error) {
                    console.error('Error sending OTP:', error);
                    alert('Failed to send OTP. Please try again.');
                }
            });

            // Verify OTP Button Handler
            verifyOtpBtn.addEventListener('click', async function () {
                const otpCode = document.querySelector('#otpCode').value;
                if (!otpCode) {
                    alert('Please enter the OTP sent to your phone.');
                    return;
                }

                try {
                    const result = await window.confirmationResult.confirm(otpCode);
                    const user = result.user;

                    // Send the ID token to the backend
                    const idToken = await user.getIdToken();
                    const response = await fetch('/verify_token', {
                        method: 'POST',
                        body: JSON.stringify({ token: idToken }),
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const data = await response.json();
                    if (data.success) {
                        alert(data.message);
                        location.href = '/'; // Redirect to home page
                    } else {
                        alert(data.message);
                    }
                } catch (error) {
                    console.error('Error verifying OTP:', error);
                    alert('Invalid OTP. Please try again.');
                }
            });
        })
        .catch(error => {
            console.error('Error fetching Firebase config:', error);
        });
});

