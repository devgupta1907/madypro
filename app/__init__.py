from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

app.secret_key = b'_5#y2LF4Q8z\sdfdgxec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///madyproDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESUME_FOLDER'] = os.path.join(app.root_path, 'static', 'resume')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)


from app import routes
