from flask import redirect, request, url_for, flash
from flask_login import current_user
from functools import wraps
from app import db, login_manager
from app.models import Customer, Professional, Admin



@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('p_'):
        return db.session.get(Professional, int(user_id[2:]))
    elif user_id.startswith('c_'):
        return db.session.get(Customer, int(user_id[2:]))
    elif user_id.startswith('a_'):
        return db.session.get(Admin, int(user_id[2:]))
    return None 



def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please Log In With Admin Credentials', 'warning')
            return redirect(url_for('admin_login'))

        if not current_user.get_id().startswith('a_'):
            flash('Access Denied! You Are Not Allowed To Access This Page', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function



def professional_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please Log As A Professional To Continue', 'warning')
            return redirect(url_for('professional_login'))

        if not current_user.get_id().startswith('p_'):
            flash('Access Denied! You Are Not Allowed To Access This Page', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function



def customer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please Log As A Customer To Continue', 'warning')
            return redirect(url_for('customer_login'))

        if not current_user.get_id().startswith('c_'):
            flash('Access Denied! You Are Not Allowed To Access This Page', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_search_results(model):
    keyword = request.args.get('keyword')
    result = model.query.filter(model.name.ilike(f"%{keyword}%")).all()
    return result

def search_by_name_and_email(model):
    keyword = request.args.get('keyword')
    result = model.query.filter((model.name.ilike(f"%{keyword}%")) | (model.email.ilike(f"%{keyword}%"))).all()
    return result