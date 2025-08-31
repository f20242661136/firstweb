from flask import Blueprint, render_template
from models import InvestmentPlan

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    plans = InvestmentPlan.query.filter_by(is_active=True).limit(3).all()
    return render_template('index.html', plans=plans)

@main_bp.route('/about')
def about():
    return render_template('about.html')