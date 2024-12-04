from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField
from wtforms import DecimalField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from wtforms.validators import Email, EqualTo, Optional
import datetime
from app.models import User
from flask_login import current_user


# Movie Form
class MovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    genre = SelectField(
        'Genre',
        choices=[
            ('Action', 'Action'),
            ('Drama', 'Drama'),
            ('Comedy', 'Comedy'),
            ('Thriller', 'Thriller'),
            ('Romance', 'Romance'),
            ('Horror', 'Horror')
        ],
        validators=[DataRequired()]
    )
    watch_date = DateField('Watch Date', validators=[DataRequired()])
    rating = DecimalField(
        'Rating',
        default=0,
        validators=[
            DataRequired(),
            NumberRange(min=0, max=5, message="Invalid rating.")
        ],
        places=1
    )
    review = TextAreaField('Review', validators=[DataRequired()])
    reflections = TextAreaField('Reflections', validators=[DataRequired()])
    recommend = BooleanField('Recommend?')
    poster_url = StringField('Poster URL')
    submit = SubmitField('Add Movie')

    # Custom validator for watch_date
    def validate_watch_date(form, field):
        if field.data > datetime.date.today():
            raise ValidationError("Watch date cannot be in the future.")


# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Signup Form
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Edit Profile Form
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(), EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('This email is already registered.')


# Delete Account Form
class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Delete Account')
