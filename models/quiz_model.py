# models/quiz_model.py
from models.database import db
from datetime import date

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True))
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    remarks = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Quiz {self.id}>'