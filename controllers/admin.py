# controllers/admin.py
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.database import db
from models.subject_model import Subject
from models.chapter_model import Chapter
from models.quiz_model import Quiz
from models.question_model import Question
from models.user_model import User
from models.score_model import Score
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def ensure_static_dir():
    """Ensure the static directory exists"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    return static_dir

def save_chart(fig, filename):
    """Save a chart to the static directory"""
    static_dir = ensure_static_dir()
    filepath = os.path.join(static_dir, filename)
    fig.savefig(filepath)
    plt.close(fig)
    return filename

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    try:
        # Fetch all subjects, chapters, quizzes, scores, and users for display
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        scores = Score.query.all()
        users = User.query.all()
        
        # Prepare data for charts
        # 1. Subject-wise Top Scores (Bar Chart)
        subject_scores = {}
        for subject in subjects:
            total_score = sum(score.total_scored for score in scores if score.quiz.chapter.subject_id == subject.id)
            subject_scores[subject.name] = total_score
        
        # Generate Bar Chart for Subject-wise Top Scores
        if subject_scores:
            fig = plt.figure(figsize=(8, 6))
            plt.bar(subject_scores.keys(), subject_scores.values(), color=['#007bff', '#28a745', '#dc3545'])
            plt.xlabel('Subjects')
            plt.ylabel('Total Scores')
            plt.title('Subject-wise Top Scores')
            plt.xticks(rotation=45)
            plt.tight_layout()
            bar_chart_path = save_chart(fig, 'subject_scores_bar.png')
        else:
            bar_chart_path = None

        # 2. Subject-wise User Attempts (Pie Chart)
        subject_attempts = {}
        for subject in subjects:
            attempts = len([score for score in scores if score.quiz.chapter.subject_id == subject.id])
            subject_attempts[subject.name] = attempts if attempts > 0 else 0
        
        # Generate Pie Chart for Subject-wise User Attempts
        if any(subject_attempts.values()):  # Only generate if there are attempts
            fig = plt.figure(figsize=(8, 6))
            plt.pie(subject_attempts.values(), labels=subject_attempts.keys(), autopct='%1.1f%%', startangle=140, colors=['#007bff', '#28a745', '#dc3545', '#ffc107'])
            plt.title('Subject-wise User Attempts')
            plt.tight_layout()
            pie_chart_path = save_chart(fig, 'subject_attempts_pie.png')
        else:
            pie_chart_path = None
        
        return render_template('admin_dashboard.html', 
                             subjects=subjects, 
                             chapters=chapters, 
                             quizzes=quizzes, 
                             users=users, 
                             bar_chart_path=bar_chart_path, 
                             pie_chart_path=pie_chart_path)
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        return render_template('admin_dashboard.html', 
                             subjects=[], 
                             chapters=[], 
                             quizzes=[], 
                             users=[], 
                             bar_chart_path=None, 
                             pie_chart_path=None)

@admin_bp.route('/admin/subject/add', methods=['POST'])
def add_subject():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    name = request.form['name']
    description = request.form['description']
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/subject/edit/<int:subject_id>', methods=['POST'])
def edit_subject(subject_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form['name']
    subject.description = request.form['description']
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/subject/delete/<int:subject_id>')
def delete_subject(subject_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/chapter/add', methods=['POST'])
def add_chapter():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    name = request.form['name']
    description = request.form['description']
    subject_id = request.form['subject_id']
    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/chapter/delete/<int:chapter_id>')
def delete_chapter(chapter_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/quiz/add', methods=['POST'])
def add_quiz():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    chapter_id = request.form['chapter_id']
    date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d').date()
    time_duration = request.form['time_duration']
    remarks = request.form['remarks']
    quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks)
    db.session.add(quiz)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/quiz/edit/<int:quiz_id>', methods=['POST'])
def edit_quiz(quiz_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d').date()
    quiz.time_duration = request.form['time_duration']
    quiz.remarks = request.form['remarks']
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/quiz/delete/<int:quiz_id>')
def delete_quiz(quiz_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/question/add', methods=['POST'])
def add_question():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    quiz_id = request.form['quiz_id']
    question_statement = request.form['question_statement']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    correct_option = int(request.form['correct_option'])
    question = Question(quiz_id=quiz_id, question_statement=question_statement, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=correct_option)
    db.session.add(question)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))
@admin_bp.route('/admin/question/delete/<int:question_id>')
def delete_question(question_id):
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/search', methods=['GET'])
def search():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    try:
        query = request.args.get('query', '')
        search_type = request.args.get('type', 'all')
        
        # Fetch all data for the dashboard
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        users = User.query.all()
        
        # Filter results based on search query and type
        if query:
            if search_type in ['all', 'users']:
                users = User.query.filter(User.email.ilike(f'%{query}%') | User.full_name.ilike(f'%{query}%')).all()
            
            if search_type in ['all', 'subjects']:
                subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%') | Subject.description.ilike(f'%{query}%')).all()
            
            if search_type in ['all', 'quizzes']:
                quizzes = Quiz.query.join(Chapter).join(Subject).filter(
                    (Subject.name.ilike(f'%{query}%')) |
                    (Chapter.name.ilike(f'%{query}%')) |
                    (Quiz.remarks.ilike(f'%{query}%'))
                ).all()
            
            if search_type in ['all', 'chapters']:
                chapters = Chapter.query.join(Subject).filter(
                    (Chapter.name.ilike(f'%{query}%')) |
                    (Chapter.description.ilike(f'%{query}%')) |
                    (Subject.name.ilike(f'%{query}%'))
                ).all()
        
        # Prepare data for charts
        scores = Score.query.all()
        subject_scores = {}
        for subject in subjects:
            total_score = sum(score.total_scored for score in scores if score.quiz.chapter.subject_id == subject.id)
            subject_scores[subject.name] = total_score
        
        # Generate Bar Chart for Subject-wise Top Scores
        if subject_scores:
            fig = plt.figure(figsize=(8, 6))
            plt.bar(subject_scores.keys(), subject_scores.values(), color=['#007bff', '#28a745', '#dc3545'])
            plt.xlabel('Subjects')
            plt.ylabel('Total Scores')
            plt.title('Subject-wise Top Scores')
            plt.xticks(rotation=45)
            plt.tight_layout()
            bar_chart_path = save_chart(fig, 'subject_scores_bar.png')
        else:
            bar_chart_path = None

        # Generate Pie Chart for Subject-wise User Attempts
        subject_attempts = {}
        for subject in subjects:
            attempts = len([score for score in scores if score.quiz.chapter.subject_id == subject.id])
            subject_attempts[subject.name] = attempts if attempts > 0 else 0
        
        if any(subject_attempts.values()):
            fig = plt.figure(figsize=(8, 6))
            plt.pie(subject_attempts.values(), labels=subject_attempts.keys(), autopct='%1.1f%%', startangle=140, colors=['#007bff', '#28a745', '#dc3545', '#ffc107'])
            plt.title('Subject-wise User Attempts')
            plt.tight_layout()
            pie_chart_path = save_chart(fig, 'subject_attempts_pie.png')
        else:
            pie_chart_path = None
        
        return render_template('admin_dashboard.html', 
                             subjects=subjects, 
                             chapters=chapters, 
                             quizzes=quizzes, 
                             users=users, 
                             bar_chart_path=bar_chart_path, 
                             pie_chart_path=pie_chart_path,
                             search_query=query)
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return render_template('admin_dashboard.html', 
                             subjects=[], 
                             chapters=[], 
                             quizzes=[], 
                             users=[], 
                             bar_chart_path=None, 
                             pie_chart_path=None,
                             search_query=query)
