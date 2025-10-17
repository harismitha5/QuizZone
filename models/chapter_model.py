# models/chapter_model.py
from models.database import db

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('chapters', lazy=True))

    def __repr__(self):
        return f'<Chapter {self.name}>'