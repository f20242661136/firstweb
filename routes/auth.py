from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, bcrypt, Referral
import re
import random
import string

auth_bp = Blueprint('auth', __name__)

def generate_referral_code():
    """Generate a unique referral code"""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # Ensure uniqueness
    while User.query.filter_by(referral_code=code).first():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return code

@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    """Check if username exists"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'status': 'empty'})
    
    user = User.query.filter_by(username=username).first()
    return jsonify({'status': 'exists' if user else 'available'})

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if email exists"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'status': 'empty'})
    
    user = User.query.filter_by(email=email).first()
    return jsonify({'status': 'exists' if user else 'available'})

@auth_bp.route('/check-referrer', methods=['POST'])
def check_referrer():
    """Check if referrer exists"""
    data = request.get_json()
    referrer_code = data.get('reffer', '').strip().upper()
    
    if not referrer_code:
        return jsonify({'status': 'empty', 'message': ''})
    
    referrer = User.query.filter_by(referral_code=referrer_code).first()
    if referrer:
        return jsonify({'status': 'valid', 'message': 'Valid referrer code'})
    else:
        return jsonify({'status': 'invalid', 'message': 'Invalid referrer code'})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request
    try:
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password are required'})
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return jsonify({
                'status': 'success', 
                'message': 'Login successful', 
                'redirect': url_for('dashboard.index')
            })
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Login failed. Please try again.'})

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request
    try:
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            password = data.get('password', '')
            referrer_code = data.get('reffer', '').strip().upper()
        else:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            referrer_code = request.form.get('reffer', '').strip().upper()
        
        # Validation
        if not all([username, email, phone, password]):
            return jsonify({'status': 'error', 'message': 'All fields are required'})
        
        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'message': 'Username already exists'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'Email already exists'})
        
        if len(password) < 6:
            return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'})
        
        # Phone validation
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            return jsonify({'status': 'error', 'message': 'Invalid phone number format'})
        
        # Check referrer
        referrer = None
        if referrer_code:
            referrer = User.query.filter_by(referral_code=referrer_code).first()
            if not referrer:
                return jsonify({'status': 'error', 'message': 'Invalid referral code'})
        
        # Create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_referral_code = generate_referral_code()
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            password=hashed_password,
            referral_code=user_referral_code,
            referred_by=referrer_code if referrer else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create referral relationship if applicable
        if referrer:
            referral = Referral(referrer_id=referrer.id, referred_id=user.id)
            db.session.add(referral)
            db.session.commit()
        
        # Auto-login after registration
        login_user(user)
        
        return jsonify({
            'status': 'success', 
            'message': 'Registration successful!',
            'redirect': url_for('dashboard.index')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # For debugging
        return jsonify({'status': 'error', 'message': 'Registration failed. Please try again.'})

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))