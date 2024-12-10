from firebase_admin import auth

def send_firebase_otp(phone_number):
    """
    Simulates the initiation of the OTP sending process via Firebase.

    Firebase Admin SDK does not directly send OTPs. The client-side Firebase SDK handles
    OTP sending and reCAPTCHA. This function ensures the user exists in Firebase.

    Args:
        phone_number (str): The phone number in E.164 format (e.g., "+1234567890").

    Returns:
        dict: Contains the result or error message.
    """
    try:
        # Check if the user exists; create if not
        try:
            user = auth.get_user_by_phone_number(phone_number)
            message = "User already exists. OTP sending is handled client-side."
        except auth.UserNotFoundError:
            user = auth.create_user(phone_number=phone_number)
            message = "New user created. OTP sending is handled client-side."

        # Note: OTP sending is handled by the Firebase client-side SDK
        return {"success": True, "message": message, "user_id": user.uid}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_firebase_token(id_token):
    """
    Verifies the Firebase ID token received from the client after OTP verification.

    Firebase Admin SDK verifies the token to authenticate the user.

    Args:
        id_token (str): The Firebase ID token received from the frontend.

    Returns:
        dict: Contains the verification result or error message.
    """
    try:
        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token.get("uid", None)

        if user_id:
            return {
                "success": True,
                "message": "Token verified successfully.",
                "user_id": user_id,
            }
        else:
            return {
                "success": False,
                "error": "Invalid token or user ID not found.",
            }
    except Exception as e:
        return {"success": False, "error": f"Token verification failed: {str(e)}"}

