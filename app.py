# app.py (updated)
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template
from config import Config
from models.database import init_db
from controllers.auth import auth_bp
from controllers.admin import admin_bp
from controllers.user import user_bp
from controllers.api import api_bp

# Import all models to ensure they are registered with SQLAlchemy
from models.user_model import User
from models.subject_model import Subject
from models.chapter_model import Chapter
from models.quiz_model import Quiz
from models.question_model import Question
from models.score_model import Score

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(api_bp)  # Register the API blueprint

# Initialize database
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    