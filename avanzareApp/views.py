from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Menu, User
from . import db
import json

views = Blueprint('views', __name__)

#decorator
@views.route('/add-menu-item', methods=['GET', 'POST'])
@login_required
def add_menu_item():

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        menu_type = request.form.get('menu_type')


        menu_item = Menu.query.filter_by(name=name).first()

        if menu_item:
            flash('This dish name already exists.', category="error")

        #elif len(description) > 10000:
            #flash('Description must be less than 10,000 characters.', category="error")
        else:
            # add the user
            new_menu_item = Menu(name=name, price=price, description=description, menu_type=menu_type, user_id=current_user.id)
            db.session.add(new_menu_item)
            db.session.commit()
            #login_user(user, remember=True)
            flash('New item added to menu!!!', category="success")
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template("edit_menu.html", items=items, user=current_user)
        # this is needed just in case to show items just in case add item gets error
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()

    return render_template("edit_menu.html", items=items, user=current_user)

#decorator
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added.', category="success")
    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete-item', methods=['POST', 'GET'])
def delete_item():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Menu.query.get(itemId)

    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})

@views.route('/edit_redirect/<int:id>', methods=['GET', 'POST'])
def edit_redirect(id):
    item = Menu.query.filter(Menu.id == id).first()
    if request.method == 'POST':
        print("first: ", item.name, item.price, item.description, item.menu_type, item.id)
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        menu_type = request.form.get('menu_type')
        print("form vars:", name, price, description, menu_type)
        item.name = name
        item.price = price
        item.description = description
        item.menu_type = menu_type
        print(item.name, item.price, item.description, item.menu_type, item.id)
        flash('Item has been edited!!!', category="success")
        db.session.commit()
        return redirect(url_for('views.add_menu_item'))
    return render_template('edit_menu_item.html', item=item)


'''''
@views.route('/update_menu/<int:id>', methods=['GET','POST'])
def update_menu_item(id):
    item = Menu.query.filter(Menu.id == id).first()
    print("first: ", item.name, item.price, item.description, item.menu_type, item.id)
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    menu_type = request.form.get('menu_type')
    print("form vars:", name, price, description, menu_type)
    item.name = name
    item.price = price
    item.description = description
    item.menu_type = menu_type
    print(item.name, item.price, item.description, item.menu_type, item.id)

    print(item.name, item.price, item.description, item.menu_type, item.id)
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("edit_menu.html", items=items, user=current_user)


'''''


