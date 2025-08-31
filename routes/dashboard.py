from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, User, Investment, Transaction, Referral
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Get user investments
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    
    # Calculate stats
    total_investment = sum(inv.amount for inv in investments if inv.status == 'active')
    total_profit = sum(inv.total_profit for inv in investments)
    
    # Get recent transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.created_at.desc()).limit(5).all()
    
    # Get referral stats
    referral_count = Referral.query.filter_by(referrer_id=current_user.id).count()
    referral_earnings = db.session.query(db.func.sum(Referral.commission_earned)).filter(
        Referral.referrer_id == current_user.id).scalar() or 0
    
    return render_template('dashboard.html', 
                         investments=investments,
                         total_investment=total_investment,
                         total_profit=total_profit,
                         transactions=transactions,
                         referral_count=referral_count,
                         referral_earnings=referral_earnings,
                         user = current_user,
                         total_deposit = total_investment)

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def get_stats():
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    referrals = Referral.query.filter_by(referrer_id=current_user.id).all()
    
    total_deposit = sum(t.amount for t in transactions if t.transaction_type == 'deposit' and t.status == 'completed')
    total_withdrawal = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal' and t.status == 'completed')
    total_investment = sum(inv.amount for inv in investments)
    referral_earnings = sum(ref.commission_earned for ref in referrals)
    
    return jsonify({
        'balance': current_user.balance,
        'total_deposit': total_deposit,
        'total_withdrawal': total_withdrawal,
        'total_investment': total_investment,
        'referral_earnings': referral_earnings
    })