# models/score_model.py
from models.database import db

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))
    user = db.relationship('User', backref=db.backref('scores', lazy=True))
    time_stamp_of_attempt = db.Column(db.String(19), nullable=False)  # Format: YYYY-MM-DD HH:MM:SS
    total_scored = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Score {self.id}>'