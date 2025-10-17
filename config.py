# config.py
class Config:
    SECRET_KEY = 'your-secret-key'  # For session management
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False