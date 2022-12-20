from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Menu, News
from werkzeug.security import generate_password_hash, check_password_hash
from .import db
from flask_login import login_user, login_required, logout_user, current_user
import random

auth = Blueprint('auth', __name__)
# GET request retrieves information
# POST is updating or creating something
# sending info to the server is a POST request
# UPDATE, DELETE, ETC
# when db is deleted you have to sign up maybe change login so if no accounts exist the nothing

# star page is where people can see the menu without making an account
@auth.route('/', methods=['GET'])
def start_page():
    # get all menu items
    items = Menu.query.all()
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    # if db is deleted then we have to manually create the first user
    # first user is the headChef
    # this only occurs if start page is the first page selected so if login page was directed first then this user
    # doesn't exist until selected. I have it set that start page should be the first page, but sometimes if db is reset
    # it won't be the first page I think because of the keep user logged in function
    if not user:
        new_user = User(email="headChef@gmail.com", first_name="Rance", password=generate_password_hash("pasta123", method="sha256"))
        db.session.add(new_user)
        db.session.commit()
        return render_template("start_page.html", items=items, user=current_user)
    # if there are any news created by the chef then retrieve them to show in featured section
    news = db.session.query(News).order_by(News.id.desc()).all()
    # I only want to show a couple of featured news posts so this loop randomly chooses five to pass to start page
    # counts to five and breaks loop when 5 are selected
    # everytime the start page is selected, random news posts are shown
    count = 0
    for post in news:
        post = random.choice(news)
        post.featured = "TRUE"
        count += 1
        if count == 5:
            break
    # get all the news that were randomly selected. We do not commit here so that different news shows up everytime
    news = News.query.filter_by(featured="TRUE").order_by(News.featured).all()
    return render_template("start_page.html", news=news, items=items, user=current_user)

# type url 127.0.0.1:5000/login
# login to make an order and view past orders
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # fetch all emnu items
    items = Menu.query.all()
    # if db reset this user might not exist, so this is here to create user just in case
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    if not user:
        new_user = User(email="headChef@gmail.com", first_name="Rance",
                        password=generate_password_hash("pasta123", method="sha256"))
        db.session.add(new_user)
        db.session.commit()
        return render_template("start_page.html", items=items, user=current_user)
    # this function renders login.html if method == get and logs in user if method == post
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # .first() returns first result but should only be one
        user = User.query.filter_by(email=email).first()
        # dont forget to check_password here for pasta123
        # if chef is logging in then they get redirected to add menu item. could be changed to view orders or user home.
        # the chef usually would just make whatever he wants to eat, so he wouldn't really need to make an order
        if email == "headChef@gmail.com" and password == "pasta123":
            msg = 'Hello Chef ' + user.first_name + "!"
            flash(msg, category="success")
            login_user(user, remember=True)
            return redirect(url_for('views.edit_menu'))

        # checks to see if the user exists by checking if the password entered matches the db password
        # it is also hashed in the db
        # if password does not match db password then user can't log in to that account
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category="success")
                # makes it so user doesn't have to login everytime
                login_user(user, remember=True)
                return redirect(url_for('views.user_home'))
            else:
                flash('Incorrect password, try again.', category="error")
        else:
            flash('Email does not exist.', category="error")
    return render_template("login.html", user=current_user)


# type url 127.0.0.1:5000/logout
@auth.route('/logout')
# can't access this route unless user is logged in
# just logs out user and redirects to start page
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.start_page'))


# sign-up is a POST request because you're adding an account
# type url 127.0.0.1:5000/sign-up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # renders sign up page if get method and creates user row if a post method
    if request.method == 'POST':
        email = request.form.get('email')
        # all special chars minus @ and . because it is needed to make an email
        # loop make sures no special characters are in and if it is then refreshes page
        special_chars = '`~!#$%^&*()-_=+|[]{};:<>,\"\\/'
        for char in special_chars:
            if char in email:
                flash('No special chars allowed in email (except \' ).', category="error")
                return redirect(url_for('auth.sign_up'))
        first_name = request.form.get('firstName')
        # this time checks for @ char too
        special_chars = '@`~!#$%^&*()-_=+|[]{};:<>,.\"\\/'
        for char in special_chars:
            if char in first_name:
                flash('No special chars allowed in First name (except \' ).', category="error")
                return redirect(url_for('auth.sign_up'))
        # might need more password restrictions
        # I will consider making better password restriction in the future
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # fetch user to see if the email is already in use
        # can't have two users with same email
        # these are some slight restrictions for the users email/password
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
            # if user passes restrictions then their account is created
            # redirects to login page for user to login/ could be changed to redirect to user homepage
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            # login_user(user, remember=True)
            flash('Account created!!! You can login now!!', category="success")
            return redirect(url_for('auth.login'))
    return render_template("sign_up.html", user=current_user)