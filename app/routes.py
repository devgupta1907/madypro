from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import app, db
from app.utility import admin_login_required, professional_login_required, customer_login_required, search_by_name, search_by_name_and_email, chart_for_professional_services, chart_for_category_services, validate_pincode
from app.models import Category, Service, ServiceRequest, Customer, Professional, Admin



# --------------- --  Admin Routes -------- ---------------------------------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash(f"Welcome Back, {admin.name}!", "success")
            return redirect(url_for('admin_dashboard'))   
        flash("Wrong Admin Email or Password", 'danger')  
    return render_template('login.html', usertype="admin")


@app.route("/admin")
@admin_login_required
def admin_dashboard():
    professionals_in_service_graph = chart_for_professional_services()
    services_in_category_graph = chart_for_category_services()
    
    service_count = Service.query.count()
    customer_count = Customer.query.count()
    professional_count = Professional.query.filter_by(status="Active").count()
    sr_closed_count = ServiceRequest.query.filter_by(status="Closed").count()
    return render_template("admin_dashboard.html", 
                           prof_chart=professionals_in_service_graph,
                           service_chart=services_in_category_graph,
                           service_count=service_count,
                           customer_count=customer_count,
                           professional_count=professional_count,
                           sr_closed_count=sr_closed_count)


@app.route("/admin/services")
@admin_login_required
def admin_services():
    all_services = Service.query.all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template("services_admin.html", services=service_results)
    return render_template("services_admin.html", services=all_services)


@app.route("/admin/professionals")
@admin_login_required
def admin_professionals():
    all_professionals = Professional.query.all()
    professional_results = search_by_name_and_email(Professional)
    if professional_results:
        return render_template("professionals_admin.html", professionals=professional_results)
    return render_template("professionals_admin.html", professionals=all_professionals)


@app.route('/admin/customers')
@admin_login_required
def admin_customers():
    all_customers = Customer.query.all()
    customer_results = search_by_name_and_email(Customer)
    if customer_results:
        return render_template("customers_admin.html", customers=customer_results)
    return render_template("customers_admin.html", customers=all_customers)


@app.route('/admin/professionals/<int:professional_id>/activate', methods=['POST'])
@admin_login_required
def activate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "Active"
    db.session.commit()
    return redirect(url_for('admin_professionals'))


@app.route('/admin/professionals/<int:professional_id>/deactivate', methods=['POST'])
@admin_login_required
def deactivate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = "InActive"
    db.session.commit()
    return redirect(url_for('admin_professionals'))


@app.route("/admin/categories/add_category", methods=["GET", "POST"])
@admin_login_required
def add_category():
    all_categories = Category.query.all()
    if request.method == "POST":
        category_name = request.form.get("category_name")
        
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            flash(f'Error Adding Category. Category Already Exists.', 'danger')
            return redirect(url_for('add_category'))
        
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added successfully!", "success")
        return redirect(url_for('add_category'))
    return render_template("add_category.html", categories=all_categories)


@app.route("/admin/services/add_service", methods=['GET', 'POST'])
@admin_login_required
def add_service():
    all_categories = Category.query.all()
    if request.method == "POST":
        service_name = request.form.get("serviceName")
        service_price = request.form.get("servicePrice")
        service_category = request.form.get("serviceCategory")
        service_description = request.form.get("serviceDescription")
        
        existing_service = Service.query.filter_by(name=service_name).first()
        if existing_service:
            flash(f'Error Adding Service. service Already Exists.', 'danger')
            return redirect(url_for('add_service'))
            
        new_service = Service(name=service_name, 
                              price=service_price, 
                              description=service_description,
                              category_id=service_category)
        db.session.add(new_service)
        db.session.commit()
        flash("Service Added Successfully!", "success")
        return redirect(url_for('admin_services'))
    return render_template("add_service.html", categories=all_categories)


@app.route("/admin/services/update_service/<int:service_id>", methods=['GET', 'POST'])
@admin_login_required
def update_service(service_id):
    service = Service.query.filter_by(id = service_id).first()
    if request.method == "POST":
        service_name = request.form.get("serviceName")
        service_price = request.form.get("servicePrice")
        service_description = request.form.get("serviceDescription")
        
        existing_service = Service.query.filter(Service.name == service_name, 
                                                Service.id != service_id).first()
        if existing_service:
            flash(f'A Service With This Name Already Exists. Please Choose Different Name', 'danger')
            return redirect(url_for('update_service', service_id=service_id))
        
        service.name = service_name
        service.price = service_price
        service.description = service_description
        db.session.commit()
        
        flash("Service Updated Successfully!", "success")
        return redirect(url_for('admin_services'))
    return render_template("update_service.html", service=service)


@app.route("/admin/services/delete_service/<int:service_id>", methods=['POST'])
@admin_login_required
def delete_service(service_id):
    service = Service.query.filter_by(id = service_id).first()
    if request.method == "POST":
        if len(service.professionals) == 0:
            db.session.delete(service)
            db.session.commit()
            flash("Service Deleted Successfully", 'success')
            return redirect(url_for('admin_services'))
        flash("Service Cannot Be Deleted As It Has Associated Professionals", 'info')
    return redirect(url_for('admin_services'))
    
    
#  -----------------------------------------------------------------------------------   
    
@app.route("/")
def home():
    all_services = Service.query.limit(3).all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template('home.html', services=service_results)
    return render_template('home.html', services=all_services)


#  ---------------------------- Service Routes --------------------------------------

@app.route("/services")
def services():
    all_services = Service.query.all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template("services.html", services=service_results)
    return render_template("services.html", services=all_services)


@app.route("/services/<int:service_id>/professionals")
@customer_login_required
def get_professionals_of_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    if service:
        desired_professionals = Professional.query.filter_by(service_id=service.id, status="Active").all()
        if desired_professionals:
            return render_template("get_professionals_of_service.html", desired_professionals=desired_professionals, service=service)
        flash('Currently, No Professionals Are Available For This Service', 'info')
        return redirect(url_for('services'))
    return redirect(url_for('home'))


@app.route("/services/<int:service_id>/professionals/<int:professional_id>/create", methods=['POST'])
@customer_login_required
def create_service_request(service_id, professional_id):
    service = Service.query.filter_by(id=service_id).first()
    professional = Professional.query.filter_by(id=professional_id).first()
    if service and professional:
        service_request = ServiceRequest(service_id=service_id, customer_id=int(current_user.get_id()[2:]), professional_id=professional_id)
        db.session.add(service_request)
        db.session.commit()
        flash(f'Your Request Has Been Created With Professional {professional.name}.\n Let The Professional Accept Your Service Request 😀', 'success')
        return redirect(url_for('services'))
    return redirect(url_for('home'))
    

# ----------------- Category Routes -------------------------------------

@app.route('/categories')
def categories():
    categories = Category.query.all()
    category_results = search_by_name(Category)
    if category_results:
        return render_template('categories.html', categories=category_results)
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
    return render_template('professionals_dashboard.html', professional=professional, 
                           service_requests=professional.service_requests)


@app.route('/professional-dashboard/accept/<int:request_id>', methods=["POST"])
@professional_login_required
def accept_request(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id).first()
    if service_request:
        service_request.status = "Accepted"
        db.session.commit()
        return redirect(url_for('professional_dashboard'))
    flash('No Service Request Found With The Given Request ID', 'danger')
    return redirect(url_for('home'))
  
    
@app.route('/professional-dashboard/reject/<int:request_id>', methods=["POST"])
@professional_login_required
def reject_request(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id).first()
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


@app.route('/customer-dashboard/update-profile', methods=["GET", "POST"])
@customer_login_required
def update_customer():
    cust_id = int(current_user.get_id()[2:])
    customer = Customer.query.filter_by(id=cust_id).first()
    if request.method == "POST":
        new_customer_name = request.form.get("customerName")
        new_customer_pincode = int(request.form.get("customerPincode"))
        
        if validate_pincode(new_customer_pincode) is True:
            customer.name = new_customer_name
            customer.pincode = new_customer_pincode
            db.session.commit()
            flash("Details Updated Successfully", 'success')
            return redirect(url_for('customer_dashboard'))
        
        elif validate_pincode(new_customer_pincode) is False:
            flash("Invalid Pincode. Please Put Your Correct Pincode", 'danger')
        else:
            flash("Internal Issue Occurred! Please Try Again Later.", 'warning')
            
    return render_template('update_customer.html', customer=customer)


@app.route('/customer-dashboard/rate/<int:request_id>')
@customer_login_required
def rate_service(request_id):
    return render_template('rating.html', request_id=request_id)


@app.route('/customer-dashboard/close/<int:request_id>', methods=["POST"])
@customer_login_required
def close_request(request_id):
    rating = request.form.get('rating')
    
    existing_service_request = ServiceRequest.query.filter_by(id=request_id).first()
    if not existing_service_request:
        flash('Service Request Does Not Exist', 'danger')
        return redirect(url_for('customer_dashboard'))

    existing_service_request.rating = int(rating)
    existing_service_request.status = "Closed"
    db.session.commit()
    flash('Service Request Closed. Thank You For Rating Our Service Professional', 'success')
    return redirect(url_for('customer_dashboard'))
    

            

#  ------------------------ Registration Routes ----------------------------------

@app.route('/professional-register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        name = request.form.get('professionalName')
        email = request.form.get('professionalEmail')
        password = request.form.get('professionalPassword')
        work_exp = request.form.get('professionalExp')
        service_id = request.form.get('professionalService')

        existing_professional = Professional.query.filter_by(email=email).first()
        if existing_professional:
            flash('Email Already Registered. Please Use A Different Email Address.', 'danger')
            return redirect(url_for('professional_register'))

        service = Service.query.filter_by(id=service_id).first()
        
        new_professional = Professional(name=name, email=email, work_exp=work_exp, service_id=service_id)
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
        pincode = int(request.form.get('customerPincode'))
        password = request.form.get('customerPassword')
        
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email Already Registered. Please Use Different Email Address.', 'danger')
            return redirect(url_for('customer_register'))
        
        if validate_pincode(pincode) is True:
            new_customer = Customer(name=name, email=email, pincode=pincode)
            new_customer.set_password(password)
        
            db.session.add(new_customer)
            db.session.commit()
        
            flash("Your Account Has Been Created. Book Your First Service Now!", "success")
            return redirect(url_for('home'))
        
        elif validate_pincode(pincode) is False:
            flash("Invalid Pincode. Please Put Your Correct Pincode", 'danger')
        else:
            flash("Internal Issue Occurred! Please Try Again Later.", 'warning')
        return redirect(url_for('customer_register'))
        
    return render_template('customer_registration.html')


#  ------------------------ Login Routes ----------------------------------------

@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        professional = Professional.query.filter_by(email=email).first()
        if professional and check_password_hash(professional.password, password):
            login_user(professional)
            flash("You Are Now Logged In!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="professional")


@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        
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