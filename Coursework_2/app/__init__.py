from flask_admin import Admin
from flask_babel import Babel
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os


def get_locale():
    """
    Determine the locale to be used.
    If the user has specified 'lang' in the query params, use it and store it in the session.
    Otherwise, use the value stored in the session, defaulting to 'en'.
    """
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')


# Create the Flask app
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config')

# Initialize the SQLAlchemy database object with the app
db = SQLAlchemy(app)

# Initialize Babel for localization support
babel = Babel(app, locale_selector=get_locale)

# Initialize Flask-Admin
admin = Admin(app, template_mode='bootstrap4')

# Set up database migration
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

# Ensure the app binds to $PORT for deployment platforms like Koyeb or Heroku
if "PORT" in os.environ:
    app.config["PORT"] = int(os.environ.get("PORT"))
else:
    app.config["PORT"] = 8000  # Default to port 5000 for local development

# Import views and models (ensure models import `db` from this file)
from app import views, models  # noqa: F401, E402


# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID for Flask-Login.
    """
    return models.User.query.get(int(user_id))


# Ensure the app runs properly in deployment environments
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"])
