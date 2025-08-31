from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, bcrypt, User, InvestmentPlan
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.investment import investment_bp
from routes.main import main_bp
from config import Config

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
       return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(main_bp)
    
    # Database setup
    with app.app_context():
        db.create_all()
        
        # Add default investment plans if they don’t exist
        plans = [
            {'name': 'VIP 1', 'price': 174, 'daily_profit': 55, 'duration': 60},
            {'name': 'VIP 2', 'price': 471, 'daily_profit': 132, 'duration': 60},
            {'name': 'VIP 3', 'price': 948, 'daily_profit': 260, 'duration': 60}
        ]
        
        for plan_data in plans:
            if not InvestmentPlan.query.filter_by(name=plan_data['name']).first():
                plan = InvestmentPlan(
                    name=plan_data['name'],
                    price=plan_data['price'],
                    daily_profit=plan_data['daily_profit'],
                    duration=plan_data['duration']
                )
                db.session.add(plan)
        
        db.session.commit()
    
    return app
# In your routes.py or app.py

from flask import jsonify, request
from flask_login import login_required, current_user
from models import User, Referral, db

@app.route('/api/user/stats')
@login_required
def user_stats():
    """Get user statistics for the referral page"""
    # Get referral count
    referral_count = Referral.query.filter_by(referrer_id=current_user.id).count()
    
    # Calculate team investment (you'll need to implement this based on your model)
    team_investment = calculate_team_investment(current_user.id)
    
    return jsonify({
        'referral_count': referral_count,
        'team_investment': team_investment,
        'referral_code': current_user.referral_code,
        'username': current_user.username
    })

@app.route('/api/user/referrals')
@login_required
def user_referrals():
    """Get user's referral tree"""
    referrals = get_referral_tree(current_user.id)
    return jsonify(referrals)

def get_referral_tree(user_id, level=1, max_levels=5):
    """Recursively build referral tree"""
    if level > max_levels:
        return None
    
    referrals = Referral.query.filter_by(referrer_id=user_id).all()
    
    tree = []
    for ref in referrals:
        referred_user = User.query.get(ref.referred_id)
        if referred_user:
            user_data = {
                'id': referred_user.id,
                'username': referred_user.username,
                'plan': referred_user.plan.name if referred_user.plan else 'N/A',
                'level': level,
                'children': get_referral_tree(referred_user.id, level + 1, max_levels)
            }
            tree.append(user_data)
    
    return tree

def calculate_team_investment(user_id):
    """Calculate total investment by user's team"""
    # This will depend on your investment model structure
    # Example implementation:
    team_investment = 0
    referrals = Referral.query.filter_by(referrer_id=user_id).all()
    
    for ref in referrals:
        referred_user = User.query.get(ref.referred_id)
        if referred_user:
            # Assuming you have an investment relationship
            for investment in referred_user.investments:
                if investment.status == 'active':
                    team_investment += investment.amount
    
    return team_investment
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
