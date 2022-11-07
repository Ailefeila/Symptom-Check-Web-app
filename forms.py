from random import choices
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    firstname = StringField('Firstname', validators=[Optional()])
    lastname = StringField('Lsastname', validators=[Optional()])


class LoginForm(FlaskForm):
    """Login form."""
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])


class MemberAddForm(FlaskForm):
    """Form for adding members."""

    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('female', 'Female'), ('male', 'Male')])
    age = StringField('Age', validators=[DataRequired()])



class EvidenceForm(FlaskForm):
    """Form for adding the initial evidence"""
    symptom = StringField('What is your most obvioust symptom?', validators=[DataRequired()])

class ChoiceForm(FlaskForm):
    choice = SelectField("Answer", validators=[DataRequired()])



class DeleteForm(FlaskForm):
    """Delete form"""