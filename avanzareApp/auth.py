from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Menu
from werkzeug.security import generate_password_hash, check_password_hash
from .import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)
# GET request retrieves information
# POST is updating or creating something
# sending info to the server is a POST request
# UPDATE, DELETE, ETC

# @auth.route('hello')
#@auth.route()


@auth.route('/start_page', methods=['GET'])
def start_page():
    user = User.query.filter(User.email=='headChef@gmail.com').first()
    # if db is deleted then we have to manually create the first user
    if not user:
        new_user = User(email="headChef@gmail.com", first_name="Rance", password=generate_password_hash("pasta123", method="sha256"))
        db.session.add(new_user)
        db.session.commit()
        items = Menu.query.filter_by(user_id=new_user.id).order_by(Menu.name).all()
        return render_template("start_page.html", items=items, user=current_user)
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("start_page.html", items=items, user=current_user)

'''
@auth.route('/edit_menu', methods=['GET', 'POST'])
def edit_menu():

    return render_template("edit_menu.html", user=current_user)'''


# type url 127.0.0.1:5000/login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # .first() returns first result but should only be one
        user = User.query.filter_by(email=email).first()
        # dont forget to check_password here for pasta123
        if email == "headChef@gmail.com" and password == "pasta123":
            login_user(user, remember=True)
            return redirect(url_for('views.add_menu_item'))

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category="success")
                # makes it so user doesn't have to login everytime
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category="error")
        else:
            flash('Email does not exist.', category="error")

    return render_template("login.html", user=current_user)

# type url 127.0.0.1:5000/logout
@auth.route('/logout')
# can't access this route unless user is logged in
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.start_page'))

#sign-up is a POST request because you're adding an account
# type url 127.0.0.1:5000/sign-up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('This email already exists.', category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category="error")
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category="error")
        elif password1 != password2:
            flash('Passwords don\'t match.', category="error")
        elif len(password1) < 7:
            flash('Password must be greater than 7 characters', category="error")
        else:
            # add the user
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            #login_user(user, remember=True)
            flash('Account created!!! You can login now!!', category="success")
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", user=current_user)