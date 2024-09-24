from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = b'_5#y2LF4Q8z\sdfdgxec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///madyproDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# db.init_app(app)
# migrate.init_app(app, db)
# login_manager.init_app(app)

from app import routes
