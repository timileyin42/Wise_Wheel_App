from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Replace 'username_or_email' with the actual identifier of the user
    user = User.query.filter_by(email="tompsonphilip446@gmail.com").first()

    if user:
        db.session.delete(user)
        db.session.commit()
        print("User deleted successfully.")
    else:
        print("User not found.")

