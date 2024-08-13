from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  create_engine
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import os
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
os.getcwd()


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

class TopicForm(FlaskForm):
    name = StringField('Категория', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField("Отправить")

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), email_enable])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    confirm = PasswordField('confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Отправить')


class LogInForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6), have_digit, have_lower, have_upper])
    submit = SubmitField("LogIn")



class TaskEditForm(FlaskForm):
    question = StringField("question", validators=[DataRequired()])
    photo = FileField("photo")
    answer = StringField("answer", validators=[DataRequired()])
    topic = StringField("topic")
    submit = SubmitField("submit")





class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/images/uploads"
app.config['SECRET_KEY'] = 'asdfdsafsa341243kj;lajrfjpip install -U Flask-SQLAlchemy' 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
bcrypt = Bcrypt(app)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class TaskForm(FlaskForm):
    question = StringField("question", validators=[DataRequired()])
    photo = FileField("photo")
    answer = StringField("answer", validators=[DataRequired()])
    topic = SelectField("topics")
    submit = SubmitField("submit")

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



engine = create_engine('sqlite:////path/to/sqlite3.db')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    question = db.Column(db.String(999), nullable=False)
    photo = db.Column(db.String(999))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    answer = db.Column(db.String(199), nullable=False)

class Topic(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    questions = db.relationship('Question', backref='topic', lazy=True)


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

@app.route("/tasks", defaults={'topic_id':None})
@app.route("/tasks/<topic_id>")
def tasks(topic_id):
    if topic_id != None:
        tasks=Question.query.filter_by(topic_id=topic_id)
    else:
        tasks =Question.query.all()
    return render_template("tasks.html", tasks=tasks)
    
@app.route('/task/create', methods=["POST", "GET"])
def create_task():
    form_in_main = TaskForm()

    topics = Topic.query.all()
    options = []
    for topic in topics:
        options.append((topic.id, topic.name))
    form_in_main.topic.choices = options
    
    if form_in_main.validate_on_submit():
        basedir = os.path.abspath(os.path.dirname(__file__))
        file = request.files['photo']
        filename = file.filename
        new_question = Question(question=form_in_main.question.data, photo=filename, answer=form_in_main.answer.data, topic_id=form_in_main.topic.data)
        file.save(os.path.join(basedir, "static", "images", filename))               
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('create_task.html', form_in_template=form_in_main, topics=topics)

@app.route('/task/delete/<task_id>')
def delete_task(task_id):
    flash(f'Вы удалили вопрос с id {task_id}')
    question = Question.query.get(int(task_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('tasks'))

   
@app.route('/task/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    form_in_main = TaskEditForm()
    this_task = Question.query.get(int(task_id))
    if form_in_main.validate_on_submit():       
        this_task.question = form_in_main.question.data
        basedir = os.path.abspath(os.path.dirname(__file__))
        file = request.files['photo']
        filename = file.filename
        this_task.answer = form_in_main.answer.data
        if filename:
            file.save(os.path.join(basedir, "static", "images", filename))
            this_task.photo = filename
        db.session.commit()
        return redirect(url_for('tasks'))
    form_in_main.question.data = this_task.question
    form_in_main.answer.data = this_task.answer
    return render_template('edit_task.html', form_in_template=form_in_main)


@app.route('/check_answer', methods=['GET', 'POST'])
def check_answer():
    # guess = request.form['answer']
    # return guess
    if request.method == "POST":
        task_id = request.form['task_id']
        cor_answer = Question.query.get(int(task_id)).answer
        quess = request.form['answer']
        return str(cor_answer.lower()==quess.lower())

@app.route('/topic/create', methods=['POST', 'GET'])
def create_topic():
    topic_form = TopicForm()
    if topic_form.validate_on_submit():
        new_topic = Topic(name=topic_form.name.data)
        db.session.add(new_topic)
        db.session.commit()
        topic_form.name.data = None
    topics = Topic.query.all()
    return render_template('create_topic.html', topics=topics, form=topic_form)


app.run(debug = True)