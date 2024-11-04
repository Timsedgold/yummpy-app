from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import InputRequired, Email, Length


class SignupForm(FlaskForm):
    """Form for adding users."""
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class AddRecipeForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    image = StringField('Image Url', validators=[InputRequired()])
    vegetarian = BooleanField('Vegetarian')
    vegan = BooleanField('Vegan')
    ketogenic = BooleanField('Ketogenic')

class EditRecipeForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    image = StringField('Image Url', validators=[InputRequired()])
    vegetarian = BooleanField('Vegetarian')
    vegan = BooleanField('Vegan')
    ketogenic = BooleanField('Ketogenic')    
        

    