from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  create_engine
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import LoginManager


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

class TaskForm(FlaskForm):
    question = StringField("question", validators=[DataRequired()])
    answer = StringField("answer", validators=[DataRequired()])
    submit = SubmitField("submit")


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdfdsafsa341243kj;lajrfjpip install -U Flask-SQLAlchemy' 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
bcrypt = Bcrypt(app)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column



engine = create_engine('sqlite:////path/to/sqlite3.db')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    question = db.Column(db.String(999), nullable=False)
    answer = db.Column(db.String(199), nullable=False)


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
@login_required
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
                login_user(user)
                next = request.args.get('next')
                flash(f'Вы вошли как {current_user.email}')
                return redirect(next or url_for('home'))
            else:
                flash('Неверный пароль')
        else:
            flash('Пользователь с таким email не найден')
        
    return render_template("login.html", form=form)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/log_out")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/tasks")
def tasks():
    tasks=Question.query.all()
    return render_template("tasks.html", tasks=tasks)
    
@app.route('/task/create', methods=["POST", "GET"])
def create_task():
    form_in_main = TaskForm()
    if form_in_main.validate_on_submit():
        new_question = Question(question=form_in_main.question.data,answer=form_in_main.answer.data)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('create_task.html', form_in_template=form_in_main)


@app.route('/check_answer', methods=['GET', 'POST'])
def check_answer():
    # task_id = request.form['task_id']
    # guess = request.form['answer']
    # task = Question.query.get(task_id)
    # return guess.lower() == task.answer.lower()
    return 5




app.run(debug=True)
