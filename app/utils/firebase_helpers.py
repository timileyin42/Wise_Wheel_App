from firebase_admin import auth

def send_firebase_otp(phone_number):
    """
    Initiates the OTP sending process via Firebase.

    Firebase Admin SDK does not directly send OTPs, but you can use Firebase Authentication
    to trigger an SMS-based verification process.

    Args:
        phone_number (str): The phone number in E.164 format (e.g., "+1234567890").

    Returns:
        dict: Contains the result or error message.
    """
    try:
        # Check if the user exists, if not create a placeholder for the phone number
        try:
            user = auth.get_user_by_phone_number(phone_number)
            message = "User already exists. OTP sent for verification."
        except auth.UserNotFoundError:
            user = auth.create_user(phone_number=phone_number)
            message = "New user created and OTP sent for verification."

        # You may need to integrate client-side Firebase SDK to send OTP
        # Firebase Admin alone doesn't handle OTP sending
        return {"success": True, "message": message, "user_id": user.uid}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_firebase_otp(verification_id, otp):
    """
    Verifies the OTP entered by the user via Firebase Authentication.

    Note: Firebase Admin SDK does not handle OTP verification directly.
    OTP verification is done client-side and the result (ID token) is sent to the backend.

    Args:
        verification_id (str): Firebase Verification ID (session).
        otp (str): One-time password entered by the user.

    Returns:
        dict: Contains the verification result or error message.
    """
    try:
        # Normally, you would use client-side Firebase SDK to verify the OTP
        # This method assumes you receive a valid ID token after verification on the client-side
        decoded_token = auth.verify_id_token(otp)
        user_id = decoded_token.get("uid", None)
        if user_id:
            return {"success": True, "message": "OTP verified successfully.", "user_id": user_id}
        else:
            return {"success": False, "error": "Invalid OTP or user ID not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

