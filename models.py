from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(10), unique=True)
    referred_by = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    investments = db.relationship('Investment', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    referrals = db.relationship('Referral', foreign_keys='Referral.referrer_id', backref='referrer', lazy=True)

class InvestmentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    daily_profit = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in days
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('investment_plan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    total_profit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    plan = db.relationship('InvestmentPlan', backref='investments')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, investment, profit
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    commission_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    referred = db.relationship('User', foreign_keys=[referred_id], backref='referred_by_link')