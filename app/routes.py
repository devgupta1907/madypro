from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import app, db, login_manager
from app.models import Category, Service, ServiceRequest, Customer, Professional

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('p_'):
        return db.session.get(Professional, int(user_id[2:]))
    elif user_id.startswith('c_'):
        return db.session.get(Customer, int(user_id[2:]))
    return None 


@app.route("/admin")
def admin_home():
    return render_template("admin.html")

@app.route("/admin/services")
def admin_services():
    all_services = Service.query.all()
    return render_template("services_admin.html", services=all_services)


@app.route("/admin/professionals")
def admin_professionals():
    all_professionals = Professional.query.all()
    return render_template("professionals_admin.html", professionals=all_professionals)

@app.route('/admin/customers')
def admin_customers():
    all_customers = Customer.query.all()
    return render_template("customers_admin.html", customers=all_customers)

@app.route('/admin/activate/<int:professional_id>', methods=['POST'])
def activate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "Active"
    db.session.commit()
    return redirect(url_for('admin_professionals'))

@app.route('/admin/deactivate/<int:professional_id>', methods=['POST'])
def deactivate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "InActive"
    db.session.commit()
    return redirect(url_for('admin_professionals'))

@app.route('/admin/delete/<int:professional_id>', methods=['POST'])
def delete_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    db.session.delete(professional)
    db.session.commit()
    return redirect(url_for('admin_professionals'))

@app.route("/admin/categories/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category_name = request.form["category_name"]
        
        new_category = Category(name=category_name)
        
        try:
            db.session.add(new_category)
            db.session.commit()
            flash("Category added successfully!", "success")
            return redirect(url_for('admin_services'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding category: {str(e)}', 'danger')
            return redirect(url_for('admin_services'))
    return render_template("add_category.html")

@app.route("/admin/services/add_service", methods=['GET', 'POST'])
def add_service():
    all_categories = Category.query.all()
    if request.method == "POST":
        service_name = request.form["serviceName"]
        service_price = request.form["servicePrice"]
        service_category = request.form["serviceCategory"]
        service_description = request.form["serviceDescription"]
        
        new_service = Service(name=service_name, 
                              price=service_price, 
                              description=service_description,
                              category_id=service_category)
        
        try:
            db.session.add(new_service)
            db.session.commit()
            flash("Service added successfully!", "success")
            return redirect(url_for('admin_services'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding service: {str(e)}', 'danger')
            return redirect(url_for('admin_services'))
            
    return render_template("add_service.html", categories=all_categories)
    



@app.route("/")
def home():
    print(current_user)
    return render_template("base.html")
    
@app.route("/services")
def services():
    all_services = Service.query.all()
    return render_template("services.html", services=all_services)


@app.route("/services/<int:service_id>/professionals")
def get_professionals_of_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    if service:
        desired_professionals = service.professionals
        if desired_professionals:
            return render_template("get_professionals_of_service.html", desired_professionals=desired_professionals)
    return redirect(url_for('home'))


@app.route("/services/<int:service_id>/professionals/<int:professional_id>/create")
def create_service_request(service_id, professional_id):
    service = Service.query.filter_by(id=service_id).first()
    professional = Professional.query.filter_by(id=professional_id).first()
    if service and professional:
        service_request = ServiceRequest(service_id=service_id, customer_id=current_user["id"], professional_id=professional_id)
        print(service_request)
        return None
    return None
    



@app.route('/professional-register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        name = request.form.get('professionalName')
        email = request.form.get('professionalEmail')
        password = request.form.get('professionalPassword')
        service_id = request.form.get('professionalService')

        existing_professional = Professional.query.filter_by(email=email).first()
        if existing_professional:
            flash('Email already registered. Please use different email address.', 'danger')
            return redirect(url_for('professional_register'))


        new_professional = Professional(name=name, email=email, service_id=service_id)
        new_professional.set_password(password)

        db.session.add(new_professional)
        db.session.commit()

        flash('Great! Your details has been passed to the admin. You may start providing your service post verfication of details.', 'success')
        return redirect(url_for('home'))

    # Fetch services to populate the dropdown
    all_services = Service.query.all()
    return render_template('professional_registration.html', services=all_services)

@app.route("/customer-register", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        name = request.form.get('customerName')
        email = request.form.get('customerEmail')
        password = request.form.get('customerPassword')
        
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email already registered. Please use different email address.', 'danger')
            return redirect(url_for('customer_register'))
        
        new_customer = Customer(name=name, email=email)
        new_customer.set_password(password)
        
        db.session.add(new_customer)
        db.session.commit()
        
        flash("Your account has been created. Book your first service now!", "success")
        return redirect(url_for('home'))
        
    return render_template('customer_registration.html')


@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    if request.method == "POST":
        email = request.form.get("typeEmail")
        password = request.form.get('typeEmail')
        
        professional = Professional.query.filter_by(email=email).first()
        if professional and check_password_hash(professional.password, password):
            login_user(professional)
            
            flash("You are now logged in!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="professional")


@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form.get("typeEmail")
        password = request.form.get('typePassword')
        
        customer = db.session.query(Customer).filter(Customer.email == email).first()
        if customer and check_password_hash(customer.password, password):
            login_user(customer)
            flash("You are now logged in!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="customer")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))