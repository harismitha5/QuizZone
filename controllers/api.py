from flask import Blueprint, jsonify, request
from models.database import db
from models.user_model import User
from models.subject_model import Subject
from models.chapter_model import Chapter
from models.quiz_model import Quiz
from models.question_model import Question
from models.score_model import Score
from functools import wraps
import jwt
import datetime
from config import Config

api_bp = Blueprint('api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication endpoints
@api_bp.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    user = User.query.filter_by(email=auth.get('email')).first()
    if not user or user.password != auth.get('password'):  # In production, use proper password hashing
        return jsonify({'message': 'Could not verify'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'is_admin': user.is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, Config.SECRET_KEY)
    
    return jsonify({'token': token})

# Subject endpoints
@api_bp.route('/api/subjects', methods=['GET'])
@token_required
def get_subjects(current_user):
    subjects = Subject.query.all()
    return jsonify([{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    } for subject in subjects])

@api_bp.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
@token_required
def get_subject_chapters(current_user, subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description
    } for chapter in chapters])

# Quiz endpoints
@api_bp.route('/api/quizzes', methods=['GET'])
@token_required
def get_quizzes(current_user):
    quizzes = Quiz.query.all()
    return jsonify([{
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.isoformat(),
        'time_duration': str(quiz.time_duration),
        'remarks': quiz.remarks
    } for quiz in quizzes])

@api_bp.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
@token_required
def get_quiz(current_user, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.isoformat(),
        'time_duration': str(quiz.time_duration),
        'remarks': quiz.remarks,
        'questions': [{
            'id': q.id,
            'question_statement': q.question_statement,
            'options': [q.option1, q.option2, q.option3, q.option4]
        } for q in quiz.questions]
    })

# User score endpoints
@api_bp.route('/api/users/me/scores', methods=['GET'])
@token_required
def get_user_scores(current_user):
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': score.id,
        'quiz_id': score.quiz_id,
        'total_scored': score.total_scored,
        'time_stamp': score.time_stamp_of_attempt.isoformat()
    } for score in scores])

# Admin only endpoints
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user.is_admin:
                return jsonify({'message': 'Admin privileges required'}), 403
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@api_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users(current_user):
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'qualification': user.qualification,
        'is_admin': user.is_admin
    } for user in users])

@api_bp.route('/api/admin/scores', methods=['GET'])
@admin_required
def get_all_scores(current_user):
    scores = Score.query.all()
    return jsonify([{
        'id': score.id,
        'user_id': score.user_id,
        'quiz_id': score.quiz_id,
        'total_scored': score.total_scored,
        'time_stamp': score.time_stamp_of_attempt.isoformat()
    } for score in scores]) 