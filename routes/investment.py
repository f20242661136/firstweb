from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Investment, InvestmentPlan, Transaction
from datetime import datetime, timedelta

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/investmentplan')
@login_required
def investment_plan():
    plans = InvestmentPlan.query.filter_by(is_active=True).all()
    return render_template('investment.html', plans=plans)

@investment_bp.route('/api/invest', methods=['POST'])
@login_required
def invest():
    plan_id = request.form.get('plan_id')
    amount = float(request.form.get('amount'))
    
    plan = InvestmentPlan.query.get(plan_id)
    if not plan:
        return jsonify({'status': 'error', 'message': 'Invalid investment plan'})
    
    if amount < plan.price:
        return jsonify({'status': 'error', 'message': f'Minimum investment for this plan is {plan.price}'})
    
    if current_user.balance < amount:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'})
    
    # Deduct amount from user balance
    current_user.balance -= amount
    
    # Create investment
    end_date = datetime.utcnow() + timedelta(days=plan.duration)
    investment = Investment(
        user_id=current_user.id,
        plan_id=plan.id,
        amount=amount,
        end_date=end_date
    )
    
    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        transaction_type='investment',
        status='completed',
        description=f'Investment in {plan.name}'
    )
    
    db.session.add(investment)
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Investment successful', 'redirect': url_for('dashboard.index')})

@investment_bp.route('/api/calculate_profit', methods=['POST'])
@login_required
def calculate_profit():
    plan_id = request.form.get('plan_id')
    amount = float(request.form.get('amount'))
    
    plan = InvestmentPlan.query.get(plan_id)
    if not plan:
        return jsonify({'status': 'error', 'message': 'Invalid investment plan'})
    
    daily_profit = (amount * plan.daily_profit) / plan.price
    total_profit = daily_profit * plan.duration
    
    return jsonify({
        'status': 'success',
        'daily_profit': round(daily_profit, 2),
        'total_profit': round(total_profit, 2),
        'duration': plan.duration
    })