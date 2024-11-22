from flask_admin import Admin
from flask_babel import Babel
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')


# Create the Flask app
app = Flask(__name__)

# Configure the app using config.py
app.config.from_object('config')

# Initialize the SQLAlchemy database object with the app
app.config.from_object('config')
db = SQLAlchemy(app)

# Initialize Babel for localization support (optional, if you need it)
babel = Babel(app, locale_selector=get_locale)

# Initialize Flask-Admin
admin = Admin(app, template_mode='bootstrap4')

# Set up migration object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

# Import views and models (ensure models imports db from here)
from app import views, models  # noqa: F401, E402


# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
