# models/database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Create all tables
        # Create Admin account if it doesn't exist
        from models.user_model import User
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                password='admin123',  # In a real app, hash the password
                full_name='Admin User',
                qualification='N/A',
                dob='2000-01-01',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()