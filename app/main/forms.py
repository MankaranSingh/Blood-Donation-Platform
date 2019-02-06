from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField , PasswordField, SubmitField, ValidationError, TextAreaField,IntegerField,SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email,NumberRange
from .. import db
from ..models.users import User
import pandas as pd

patiala = pd.read_csv('patiala.txt', names = ['areas'])

EqualTo('confirm', message='Passwords must match')

class SearchForm(FlaskForm):
    blood_group = SelectField('Search by Blood Group: ', choices=[('All','All'),('A+','A+' ), ('A-', 'A-'), ('B+', 'B+'),('B-', 'B-'),('O+', 'O+'), ('O+', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')],validators = [DataRequired()])
    Submit = SubmitField('Search')

class SignUp(FlaskForm):

    username = StringField('Username: ' , validators= [Length(3,50), DataRequired()])
    email = StringField('Email: ', validators= [Email()])
    phone_number = IntegerField('Phone Number: ', validators = [DataRequired()])
    blood_group = SelectField('Blood Group: ', choices=[('A+','A+' ), ('A-', 'A-'), ('B+', 'B+'),('B-', 'B-'),('O+', 'O+'), ('O+', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')],validators = [DataRequired()])
    Area = SelectField('Area: ', choices = [(str(area), str(area)) for area in patiala.areas ],validators = [DataRequired()])
    password = PasswordField('Password: ' ,validators= [Length(3,50), DataRequired()])
    phone_number = IntegerField('Phone Number: ', validators = [DataRequired()])
    age = IntegerField('Age: ', validators = [DataRequired(),NumberRange(min=18, max=60, message='You must be in the range of 18 - 60 years to donate blood according to International Standards.')])
    confirm_password = PasswordField('Confirm Password: ' ,validators= [Length(3,50), DataRequired(), EqualTo('password', message='Passwords must match')])
    Submit = SubmitField('Sign Up !')

    def validate_username(self, username):

        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username Already Taken')
    def validate_email(self, email):

        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Email Already in Use')

class Login(FlaskForm):

    email = StringField('Email: ', validators = [Email()])
    password = PasswordField('Password: ' ,validators= [Length(3,50), DataRequired()])
    remember = BooleanField('Remember Me')
    Submit = SubmitField('Login')

class Admin_editor(FlaskForm):
    
    username = StringField('Username: ' , validators= [Length(3,50), DataRequired()])
    email = StringField('Email: ', validators= [Email(),DataRequired()])
    role = StringField('Role: ', validators= [DataRequired()])
    Submit = SubmitField('Edit User')

class Profile_Edit(FlaskForm):
    
    username = StringField('Username' , validators= [Length(3,50), DataRequired()])
    email = StringField('Email', validators= [Email(),DataRequired()])
    about_me = TextAreaField('About Me')
    location = StringField('Location')
    Submit = SubmitField('Edit User')

class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Post')

    

  
    

    
    
    
    
