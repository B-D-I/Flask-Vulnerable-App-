from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime as dt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from creds import mysql_config
from forms import *

app = Flask(__name__)

# mysql db
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_config

# secret key csrf token
app.config['SECRET_KEY'] = "password"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50))
    password_hash = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=dt.datetime.now)

    @property
    def password(self):
        raise AttributeError('password not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha512', salt_length=10)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return '<Name %r>' % self.name


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get the first (unique) username
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password!")  # <<< remove these prompts (make generic error)
        else:
            flash("User does not exist!")

    return render_template('login.html', form=form)


# logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("logged out")
    return redirect(url_for('login'))


# dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


# DELETE
@app.route('/delete/<int:id>') # <- can delete users in URL
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    except:
        flash("Error")
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)


# UPDATE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.role = request.form['role']
        name_to_update.password = request.form['password']
        try:
            db.session.commit()
            flash("User updated")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)


# ADD
@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        # get all user with same email (should return none, as unique) -> if exists, then email cannot be added
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data,
                         password=form.password_hash.data,
                         role=form.role.data, username=form.username.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        # clear the form
        form.name.data = ''
        form.email.data = ''
        form.role.data = ''
        form.username.data = ''
        form.password_hash.data = ''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)


@app.route('/user/<name>')
@login_required
def user(name):
    return render_template('user.html', user_name=name)


@app.route('/name', methods=['GET', 'POST'])
@login_required
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully")

    return render_template('name.html',
                           name=name,
                           form=form)


@app.route('/')
def index():
    # first_name = "Nathan"
    return render_template("index.html")  # first_name=first_name


if __name__ == '__main__':
    app.run()
