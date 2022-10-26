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


        menu_item = Menu.query.filter_by(name=name).first()

        if menu_item:
            flash('This dish name already exists.', category="error")

        #elif len(description) > 10000:
            #flash('Description must be less than 10,000 characters.', category="error")
        else:
            # add the user
            new_menu_item = Menu(name=name, price=price, description=description, user_id=current_user.id)
            db.session.add(new_menu_item)
            db.session.commit()
            #login_user(user, remember=True)
            flash('New item added to menu!!!', category="success")
            return render_template("edit_menu.html", user=current_user)

    return render_template("edit_menu.html", user=current_user)

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
    print(item)
    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})




