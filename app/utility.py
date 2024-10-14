from flask import redirect, request, url_for, flash
from flask_login import current_user
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from functools import wraps
from app import db, login_manager
from app.models import Customer, Professional, Admin, Service, Category



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
            flash('Please Log In As A Professional To Continue', 'warning')
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
            flash('Please Log in As A Customer To Continue', 'warning')
            return redirect(url_for('customer_login'))

        if not current_user.get_id().startswith('c_'):
            flash('Access Denied! You Are Not Allowed To Access This Page', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function


def search_by_name(model):
    keyword = request.args.get('keyword')
    result = model.query.filter(model.name.ilike(f"%{keyword}%")).all()
    return result

def search_by_name_and_email(model):
    keyword = request.args.get('keyword')
    result = model.query.filter((model.name.ilike(f"%{keyword}%")) | (model.email.ilike(f"%{keyword}%"))).all()
    return result


def num_of_prof_in_each_service():
    result = {}
    services = Service.query.all()
    for service in services:
        result[service.name] = len(service.professionals)
    return result


def num_of_services_in_each_category():
    result = {}
    categories = Category.query.all()
    for category in categories:
        result[category.name] = len(category.services)
    return result


def chart_for_category_services():
    result = num_of_services_in_each_category()
    category_names = result.keys()
    service_counts = result.values()
    
    plt.figure(figsize=(8, 5))
    plt.bar(category_names, service_counts, color='skyblue')
    plt.xlabel('Category')
    plt.ylabel("Count of Services")
    plt.title('Number of Services in Each Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    image_path = os.path.join('app', 'static', 'graphs', 'services_in_category.png')
    plt.savefig(image_path)
    return 'services_in_category.png'
    

def chart_for_professional_services():
    result = num_of_prof_in_each_service()
    service_names = result.keys()
    professional_counts = result.values()
    plt.figure(figsize=(8, 5))
    plt.bar(service_names, professional_counts, color='#e6e600')
    plt.xlabel('Services')
    plt.ylabel('Number of Professionals')
    plt.title('Number of Professionals in Each Service')
    plt.xticks(rotation=45)
    
    image_path = os.path.join('app', 'static', 'graphs', 'professionals_in_service.png')
    plt.tight_layout()
    plt.savefig(image_path)
    return 'professionals_in_service.png'


def validate_pincode(pincode):
    try:
        response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}")
        json_response = response.json()
    
        if json_response[0]["Status"] == "Success":
            return True
        return False
    except Exception as e:
        return None