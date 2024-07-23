from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  create_engine
from flask_bcrypt import Bcrypt
import sqlite3

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
    
def email_enable(form, email):
    user = User.query.filter_by(email=email.data).first()
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


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdfdsafsa341243kj;lajrfjpip install -U Flask-SQLAlchemy' 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
bcrypt = Bcrypt(app)
db.init_app(app)
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column



engine = create_engine('sqlite:////path/to/sqlite3.db')


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("home.html")
@app.route("/about")
def about():
    services = [
        {
            'name' : 'Установка операционной системы',
            'price' : '1 500 р'
        },
        {
            'name' : 'Разработка сайта',
            'price' : '20 000 р'
        },
        {
            'name' : 'Создание игры на pygame',
            'price' : '1500 р'
        }
    ]
    return render_template("about.html", services=services)
@app.route("/page1")
def page1():
    points = [
        {
            'point' : 'Адрес 1',
            'metro' : 'Ветка 1 станция 1'
        },
        {
            'point' : 'Адрес 2',
            'metro' : 'Ветка 2 станция 2'
        }
    ]
    return render_template("Page1.html", points=points)
@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Пользователь добавлен в базу', 'success')
        return redirect(url_for('login'))
        
    return render_template("register.html", form=form)
@app.route("/sign_in", methods=["POST", "GET"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                return f'Вы вошли как {form.email.data}'
            else:
                flash('Неверный пароль')
        else:
            flash('Пользователь с таки email не найден')
        
    return render_template("login.html", form=form)
    
    





app.run(debug=True)
