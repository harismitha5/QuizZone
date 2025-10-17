# controllers/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db
from models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
        except KeyError:
            flash('Please provide both email and password.')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        user = User(
            email=email,
            password=password,  # In a real app, hash the password
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))