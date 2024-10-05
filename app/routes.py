from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import app, db, login_manager
from app.utility import admin_login_required, professional_login_required, customer_login_required
from app.models import Category, Service, ServiceRequest, Customer, Professional, Admin



# --------------- --  Admin Routes -------- ---------------------------------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("typeEmail")
        password = request.form.get('typePassword')
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash("You are now logged in!", "success")
            return redirect(url_for('admin_home'))   
        flash("Wrong Admin Email or Password", 'danger')  
    return render_template('login.html', usertype="admin")


@app.route("/admin")
@admin_login_required
def admin_home():
    return render_template("admin.html")


@app.route("/admin/services")
@admin_login_required
def admin_services():
    all_services = Service.query.all()
    return render_template("services_admin.html", services=all_services)


@app.route("/admin/professionals")
@admin_login_required
def admin_professionals():
    all_professionals = Professional.query.all()
    return render_template("professionals_admin.html", professionals=all_professionals)


@app.route('/admin/customers')
@admin_login_required
def admin_customers():
    all_customers = Customer.query.all()
    return render_template("customers_admin.html", customers=all_customers)


@app.route('/admin/activate/<int:professional_id>', methods=['POST'])
@admin_login_required
def activate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "Active"
    db.session.commit()
    return redirect(url_for('admin_professionals'))


@app.route('/admin/deactivate/<int:professional_id>', methods=['POST'])
@admin_login_required
def deactivate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "InActive"
    db.session.commit()
    return redirect(url_for('admin_professionals'))


@app.route('/admin/delete/<int:professional_id>', methods=['POST'])
@admin_login_required
def delete_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    db.session.delete(professional)
    db.session.commit()
    return redirect(url_for('admin_professionals'))


@app.route("/admin/categories/add_category", methods=["GET", "POST"])
@admin_login_required
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
            flash(f'Error Adding Category. Category Might Already Exists.', 'danger')
            return redirect(url_for('admin_services'))
    return render_template("add_category.html")


@app.route("/admin/services/add_service", methods=['GET', 'POST'])
@admin_login_required
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
            flash("Service Added Successfully!", "success")
            return redirect(url_for('admin_services'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error Adding Service. Service Might Already Exists.', 'danger')
            return redirect(url_for('admin_services'))
            
    return render_template("add_service.html", categories=all_categories)


#  -----------------------------------------------------------------------------------   


@app.route("/")
def home():
    keyword = request.args.get('keyword')
    if keyword:
        all_services = Service.query.filter(Service.name.ilike(f"%{keyword}%")).all()
    else:
        # Show the first 3 services if no search keyword is provided
        all_services = Service.query.limit(3).all()

    return render_template('home.html', services=all_services)
    # all_services = Service.query.all()
    # return render_template("home.html", services=all_services)


#  ---------------------------- Service Routes --------------------------------------

@app.route("/services")
def services():
    all_services = Service.query.all()
    return render_template("services.html", services=all_services)


@app.route("/services/<int:service_id>/professionals")
def get_professionals_of_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    if service:
        desired_professionals = Professional.query.filter_by(service_id=service.id, status="Active").all()
        if desired_professionals:
            return render_template("get_professionals_of_service.html", desired_professionals=desired_professionals, service=service)
        flash('Currently, No Professionals Are Available For This Service', 'info')
        return redirect(url_for('services'))
    return redirect(url_for('home'))


@app.route("/services/<int:service_id>/professionals/<int:professional_id>/create")
@login_required
def create_service_request(service_id, professional_id):
    if current_user.get_id().startswith('c_'):
        service = Service.query.filter_by(id=service_id).first()
        professional = Professional.query.filter_by(id=professional_id).first()
        if service and professional:
            service_request = ServiceRequest(service_id=service_id, customer_id=int(current_user.get_id()[2:]), professional_id=professional_id)
            db.session.add(service_request)
            db.session.commit()
            flash(f'Your Request Has Been Created With Professional {professional.name}.\n Let The Professional Accept Your Service Request 😀', 'success')
            return redirect(url_for('services'))
        return redirect(url_for('home'))
    flash('Please Login As A Customer To Book A Service', 'danger')
    return redirect(url_for('home'))
    

# ----------------- Category Route -------------------------------------

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories) 


@app.route('/categories/<int:category_id>/services')
def get_services_of_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category:
        available_services = category.services
        if available_services:
            return render_template('services.html', services=available_services, category=category.name)
        flash("Currently, No Service Is Available Under This Category", 'info')
        return redirect(url_for('categories'))
    return redirect(url_for('home'))
    

# ------------------------ Professional Routes --------------------------------


@app.route('/professional-dashboard')
@professional_login_required
def professional_dashboard():
    prof_id = int(current_user.get_id()[2:])
    professional = Professional.query.filter_by(id=prof_id).first()
    return render_template('professionals_dashboard.html', professional = professional, 
                           service_requests = professional.service_requests)


@app.route('/professional-dashboard/accept/<int:request_id>', methods=["POST"])
@professional_login_required
def accept_request(request_id):
    service_request = ServiceRequest.query.filter_by(id = request_id).first()
    if service_request:
        service_request.status = "Accepted"
        db.session.commit()
        return redirect(url_for('professional_dashboard'))
    flash('No Service Request Found With The Given Request ID', 'danger')
    return redirect(url_for('home'))
  
    
@app.route('/professional-dashboard/reject/<int:request_id>', methods=["POST"])
@professional_login_required
def reject_request(request_id):
    service_request = ServiceRequest.query.filter_by(id = request_id).first()
    if service_request:
        service_request.status = "Rejected"
        db.session.commit()
        return redirect(url_for('professional_dashboard'))
    flash('No Service Request Found With The Given Request ID', 'danger')
    return redirect(url_for('home')) 


# ------------------------ Customer Routes -----------------------------------

@app.route('/customer-dashboard')
@customer_login_required
def customer_dashboard():
    cust_id = int(current_user.get_id()[2:])
    customer = Customer.query.filter_by(id=cust_id).first()
    return render_template('customer_dashboard.html', customer=customer, service_requests=customer.service_requests)


@app.route('/customer-dashbaord/rate/<int:request_id>')
@customer_login_required
def rate_service(request_id):
    return render_template('rating.html', request_id=request_id)

@app.route('/customer-dashboard/close/<int:request_id>', methods=["GET", "POST"])
@customer_login_required
def close_request(request_id):
    if request.method == "POST":
        rating = request.form.get('rating')
        
        existing_service_request = ServiceRequest.query.filter_by(id=request_id).first()
        if not existing_service_request:
            flash('Service Request Does Not Exist', 'danger')
            return redirect(url_for('customer_dashboard'))

        existing_service_request.rating = int(rating)
        existing_service_request.status = "Closed"
        db.session.commit()
        return redirect(url_for('customer_dashboard'))
    

        
            

#  ------------------------ Registration Routes ----------------------------------

@app.route('/professional-register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        name = request.form.get('professionalName')
        email = request.form.get('professionalEmail')
        password = request.form.get('professionalPassword')
        service_id = request.form.get('professionalService')
        service_fee = request.form.get('professionalFee')

        existing_professional = Professional.query.filter_by(email=email).first()
        if existing_professional:
            flash('Email Already Registered. Please Use A Different Email Address.', 'danger')
            return redirect(url_for('professional_register'))

        service = Service.query.filter_by(id=service_id).first()
        if int(service_fee) < int(service.price):
            flash("Service Fee Must Be Greater Than Or Equals To Base Price", "danger")
            return redirect(url_for("professional_register"))
        
        new_professional = Professional(name=name, email=email, service_id=service_id, service_fee=service_fee)
        new_professional.set_password(password)

        db.session.add(new_professional)
        db.session.commit()

        flash('Great! Your Details Has Been Passed To The Admin. You May Start Providing Your Service Post Verfication Of Details.', 'success')
        return redirect(url_for('home'))

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
            flash('Email Already Registered. Please Use Different Email Address.', 'danger')
            return redirect(url_for('customer_register'))
        
        new_customer = Customer(name=name, email=email)
        new_customer.set_password(password)
        
        db.session.add(new_customer)
        db.session.commit()
        
        flash("Your Account Has Been Created. Book Your First Service Now!", "success")
        return redirect(url_for('home'))
        
    return render_template('customer_registration.html')


#  ------------------------ Login Routes ----------------------------------------

@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    if request.method == "POST":
        email = request.form.get("typeEmail")
        password = request.form.get('typePassword')
        professional = Professional.query.filter_by(email=email).first()
        if professional and check_password_hash(professional.password, password):
            login_user(professional)
            flash("You Are Now Logged In!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="professional")


@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form.get("typeEmail")
        password = request.form.get('typePassword')
        
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            login_user(customer)
            flash("You Are Now Logged In!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="customer")


#  ------------------ LogOut Route --------------------------------------

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged Out.', 'info')
    return redirect(url_for('home'))