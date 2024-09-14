from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = b'_5#y2LF4Q8z\sdfdgxec]/'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///madyproDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
# login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('p_'):
        return Professional.query.get(int(user_id[2:]))
    elif user_id.startswith('c_'):
        return Customer.query.get(int(user_id[2:]))
    return None

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    services = db.relationship('Service', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"
    

class Service(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    professionals = db.relationship('Professional', backref='service', lazy=True)
    
    def __repr__(self):
        return f"<Service {self.name}>"

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    status = db.Column(db.String, default="Requested")
    
    def __repr__(self):
        return f"<ServiceRequest {self.id}>"
    
    
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    def __repr__(self):
        return f"<Customer {self.email}>"
    
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be None or empty")

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    
class Professional(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True)
    status = db.Column(db.String, default="Pending")
    
    def __repr__(self):
        return f'<Professional {self.name}>'
    
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be None or empty")

    def check_password(self, password):
        return check_password_hash(self.password, password)
    


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


@app.route("/professional-login")
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
        
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            login_user(customer)
            flash("You are now logged in!", "success")
            return redirect(url_for('home'))     
    return render_template('login.html', usertype="customer")

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)




