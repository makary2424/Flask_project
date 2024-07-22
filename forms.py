from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main import User

def have_digit(form, field):
    if not any([sym.isdigit() for sym in field.data]):
        raise ValidationError('Пароль должен содержать цифры')
def have_lower(form, field):
    if not any([sym.islower() for sym in field.data]):
        raise ValidationError("Пароль должен содержать маленькие буквы") 
def have_upper(form, field):
    if not any([sym.isupper() for sym in field.data]):
        raise ValidationError("Пароль должен содержать большие буквы")
    
def email_enable(form, email):
    user = User.query.filter_by(email=email.data)
    if user:
        raise ValidationError('Данный email адрес уже занят!')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), email_enable])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Отправить')


class LogInForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    submit = SubmitField("LogIn")