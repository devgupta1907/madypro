from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

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
    rating = db.Column(db.Integer, CheckConstraint(sqltext='rating >= 1 AND rating <= 5'), nullable=True)

    
    def __repr__(self):
        return f"<ServiceRequest {self.id}>"
    
    
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True)
    
    def get_id(self):
        return f"c_{self.id}"
    
    def __repr__(self):
        return f"<Customer {self.email}>"
    
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be None or empty")
    
    
class Professional(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    work_exp = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True)
    status = db.Column(db.String, default="Pending")
    
    
    def get_id(self):
        return f"p_{self.id}"
    
    def __repr__(self):
        return f'<Professional {self.name}>'
    
    @property
    def rating(self):
        total_services = 0
        total_ratings = 0
        for request in self.service_requests:
            if request.rating is not None: 
                total_ratings += request.rating
            total_services += 1
            
        if total_services > 0: return total_ratings / total_services
        return None
    
    
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be None or empty")
    
    
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def get_id(self):
        return f"a_{self.id}"
    
    def __repr__(self):
        return f'<Admin {self.name}>'
    
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be None or empty")