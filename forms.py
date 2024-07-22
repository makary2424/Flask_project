from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

def have_digit(form, field):
    if not any([sym.isdigit() for sym in field.data]):
        raise ValidationError('Пароль должен содержать цифры')
def have_lower(form, field):
    if not any([sym.islower() for sym in field.data]):
        raise ValidationError("Пароль должен содержать маленькие буквы") 
def have_upper(form, field):
    if not any([sym.isupper() for sym in field.data]):
        raise ValidationError("Пароль должен содержать большие буквы")


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Отправить')


class LogInForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    submit = SubmitField("LogIn")