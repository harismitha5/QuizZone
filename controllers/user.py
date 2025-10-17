# controllers/user.py
import datetime
import matplotlib.pyplot as plt
import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.database import db
from models.subject_model import Subject
from models.chapter_model import Chapter
from models.quiz_model import Quiz
from models.question_model import Question
from models.score_model import Score

def save_chart(fig, filename):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    filepath = os.path.join(static_dir, filename)
    fig.savefig(filepath)
    plt.close(fig)
    return filename

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    subjects = Subject.query.all()
    user_scores = Score.query.filter_by(user_id=session['user_id']).all()
    
    # Prepare data for performance chart
    subject_performance = {}
    for subject in subjects:
        subject_scores = [score for score in user_scores if score.quiz.chapter.subject_id == subject.id]
        if subject_scores:
            total_possible = sum(len(score.quiz.questions) for score in subject_scores)
            total_scored = sum(score.total_scored for score in subject_scores)
            percentage = (total_scored / total_possible) * 100 if total_possible > 0 else 0
            subject_performance[subject.name] = percentage
    
    # Generate performance chart
    if subject_performance:
        fig = plt.figure(figsize=(4, 4))
        plt.bar(subject_performance.keys(), subject_performance.values(), color=['#007bff', '#28a745', '#dc3545', '#ffc107'])
        plt.xlabel('Subjects')
        plt.ylabel('Average Score (%)')
        plt.title('Your Performance by Subject')
        plt.xticks(rotation=45)
        plt.ylim(0, 100)  # Set y-axis from 0 to 100 for percentage
        plt.tight_layout()
        chart_path = save_chart(fig, 'user_performance.png')
    else:
        chart_path = None
    
    return render_template('user_dashboard.html', subjects=subjects, user_scores=user_scores, chart_path=chart_path)

@user_bp.route('/user/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('auth.login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        # Calculate score
        questions = quiz.questions
        total_score = 0
        for question in questions:
            user_answer = int(request.form.get(f'question_{question.id}', 0))
            if user_answer == question.correct_option:
                total_score += 1
        # Save score
        score = Score(
            quiz_id=quiz.id,
            user_id=session['user_id'],
            time_stamp_of_attempt=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_scored=total_score
        )
        db.session.add(score)
        db.session.commit()
        return redirect(url_for('user.quiz_results', score_id=score.id))
    return render_template('quiz.html', quiz=quiz)

@user_bp.route('/user/results/<int:score_id>')
def quiz_results(score_id):
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('auth.login'))
    score = Score.query.get_or_404(score_id)
    if score.user_id != session['user_id']:
        return redirect(url_for('user.user_dashboard'))
    return render_template('results.html', score=score)