from app import create_app, db
from app.models import User, Car, Rental

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Car': Car, 'Rental': Rental}

if __name__ == '__main__':
    # Bind to all network interfaces
    app.run(host='0.0.0.0', port=8000, debug=True)

