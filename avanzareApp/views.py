from flask import Blueprint, render_template, request, flash, abort, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Menu, User, Order, Menu_order, News
from . import db
import json
import os

# for image uploading
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'images/')
if not os.path.isdir(target):
    os.mkdir(target)
views = Blueprint('views', __name__)


# this function just returns the a specific image based on the name from the directory
@views.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('images', filename)


# get to edit menu page
@views.route('/edit-menu', methods=['GET'])
def edit_menu():
    # fetch all menu items
    items = Menu.query.all()
    # if user is not logged in and trying to access the page
    if current_user.is_anonymous:
        abort(404, description="Resource not found")
    # make sure page only loads for head chef
    if current_user.email == 'headChef@gmail.com':
        return render_template("edit_menu.html", items=items, user=current_user)
    else:
        flash('Sorry not allowed.', category="error")
        return redirect(url_for('views.user_home'))


# this is the function for the head chef to add any item they want to the menu. There are some requirements like menu
# items cannot have the same name, price must be digits/float, and limited chars for name/description.
@views.route('/add-to-menu', methods=['POST'])
def add_to_menu():
    # get input values from the chef
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    menu_type = request.form.get('menu_type')
    gluten_free = request.form.get('gluten_free')
    vegan = request.form.get('vegan')
    tmp_file = request.files.get('file')
    filename = name + '.jpg'
    # if filename empty then do nothing because user doesn't want to change the item image
    if tmp_file.filename != '':
        destination = "/".join([target, filename])
        tmp_file.save(destination)
    else:
        flash('Item image not submitted.', category="error")
        return redirect(url_for('views.edit_menu'))
    # check if there is any item in Menu that already has the name that was entered by chef
    menu_item = Menu.query.filter_by(name=name).first()
    # if menu_item exists then that means the item name is taken already
    if menu_item:
        flash('This dish name already exists.', category="error")
    # test to make sure price is acceptable
    try:
        # if price can't be converted to float then that means there are chars being used that are not digits
        # might be a better way to implement this
        float(price)
        # convert str type price to format it in $0.00 format
        price = "{:,.2f}".format(float(price))
    # (Exception,) stop 'too broad' exception msg
    except (Exception,):
        # refresh page and send error message
        flash('Only enter digits for price.', category="error")
        return redirect(url_for('views.edit_menu'))
    # test to check against any special chars
    special_chars = '`~@#^*()-_=+|[]{};:<>\\/'
    for char in special_chars:
        # check if char is in name/description
        if char in name + description:
            message = 'Some special chars are not permitted such as: ' + char
            flash(message, category="error")
            return redirect(url_for('views.edit_menu'))
    # if all is good then create the item and refresh page
    item = Menu(name=name, price=price, description=description, menu_type=menu_type, gluten_free=gluten_free,
                vegan=vegan, item_image=filename, user_id=current_user.id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('views.edit_menu'))


# this function directs the user to their home page, and it also passes their active orders. The past orders can be
# active or clear, so I just filter posts by status not active to get past orders. For efficiency, it might be better
# to change this to one loop that displays the order accordingly
@views.route('/user-home', methods=['GET', 'POST'])
@login_required
def user_home():
    active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
    # user can view all restaurant's news in user home. This could be changed to show limited random news like in
    # the featured section of the start page, but I'm assuming that there wouldn't be that much news
    # coming from a small family restaurant
    news = db.session.query(News).order_by(News.id.desc()).all()
    db.session.commit()
    return render_template("user_home.html", news=news, active_orders=active_orders, user=current_user)


# this function directs user to the order page
@views.route('/order', methods=['GET', 'POST'])
@login_required
def test_order():
    # fetch all menu items
    items = Menu.query.all()
    return render_template("order.html", items=items, user=current_user)


# Render views order page for chef to see active orders. Active order are orders that are still being prepared
# inactive orders are orders that were completed. In this page inactive orders can be cleared. The idea behind that
# feature is that if it is a new day then you might not want to see inactive orders from the day before
# It could be useful to add feature for chef to see all orders and filter by specific user or date etc. This is going on
# the to do list
@views.route('/view-orders', methods=['POST', 'GET'])
def view_orders():
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# function to deactivate active orders
# it just fetches the order by id and sets the order is_active variable to Inactive and refreshes page
@views.route('/deactivate-order/<int:id>', methods=['POST', 'GET'])
def deactivate_orders(id):
    order = Order.query.filter(Order.id == id).first()
    order.is_active = "Inactive"
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    db.session.commit()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# this sets all inactive orders to clear, so they don't appear in view orders and takes up space
@views.route('/clear-inactive-orders', methods=['POST', 'GET'])
def clear_inactive_orders():
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    for item in inactive_orders:
        item.is_active = "clear"
    db.session.commit()
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# a function to create news post and refreshes create news page
@views.route('/create-news', methods=['GET', 'POST'])
@login_required
def create_news():
    # just gets form info and creates a post
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('text')
        news_type = request.form.get('news_type')
        news_post = News(title=title, text=text, news_type=news_type)
        db.session.add(news_post)
        db.session.commit()
        flash('News post created!', category="success")
    news = db.session.query(News).order_by(News.id.desc()).all()
    return render_template("create_news.html", news=news, user=current_user)


# deletes news post using java and jsonify
@views.route('/delete-news-post', methods=['POST', 'GET'])
def delete_news_post():
    news_post = json.loads(request.data)
    news_postId = news_post['news_postId']
    news_post = News.query.get(news_postId)

    if news_post:
        db.session.delete(news_post)
        db.session.commit()
        flash('NEWS POST DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})


# this function completes and submits the user's order
@views.route('/complete-order', methods=['POST', 'GET'])
def complete_order():
    # get data from json
    items_list = json.loads(request.data)
    items_list = items_list['values']
    # create new order to save data in
    new_order = Order()
    # set order id to the current user making the order
    new_order.user_id = current_user.id
    # add the rest of the order info
    new_order.is_active = 'Active'
    new_order.total = items_list[1]['total']
    new_order.taxes = items_list[2]['taxes']
    new_order.comment = items_list[3]['comment']
    new_order.name = current_user.first_name
    # save order
    db.session.add(new_order)
    db.session.commit()
    # get the list of items in format name*quantity*price*item_id#name*quantity*price*item_id#....
    items = items_list[0]['listOfItem'].split('#')
    # the # separates each item
    for item in items:
        # the * separates the item's info
        tmp_item = item.split('*')
        for quantity in range(int(tmp_item[1])):
            # create a menu object to get the rest of the item's info
            menu_item = Menu.query.filter_by(id=tmp_item[2]).first()
            tmp_item_object = Menu_order()  # change Menu_order to MenuOrder
            # save objects details
            tmp_item_object.name = tmp_item[0]
            tmp_item_object.price = menu_item.price
            tmp_item_object.item_id = menu_item.id
            # create relationship to order
            tmp_item_object.order_id = new_order.id
            db.session.add(tmp_item_object)
            db.session.commit()
    # direct back to js to get sent to user home page
    return jsonify({})


# this function takes the order's details and passes it to the order page for the user order the same things again
@views.route('/orderAgain/<string_list>/<total>/<taxes>', methods=['POST', 'GET'])
def order_again(string_list, total, taxes):
    items = Menu.query.all()
    # string list has the info of the past order
    # separate total and taxes with '^' char because that is how js splits the string
    new_order = [string_list + '^' + total + '^' + taxes]
    return render_template("order.html", items=items, new_order=new_order, user=current_user)


# this is function is to delete an item from the menu. It just finds the item by id and then deletes it. It also deletes
# the image associated with that item from the images directory
@views.route('/delete-menu-item/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    item = Menu.query.filter_by(id=item_id).first()
    filename = item.name + '.jpg'
    os.unlink(os.path.join(target, filename))
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', category="success")
    return redirect(url_for('views.edit_menu'))


# this function is to edit any item from the menu
# it gets an id from the button when the form is submitted it has an action for this decorator. Then whatever values
# were inside the input fields are pulled and overwritten.
@views.route('/edit-menu-item/<int:item_id>', methods=['POST'])
def edit_menu_item(item_id):
    # find the item by its id
    item = Menu.query.filter_by(id=item_id).first()
    # get all the user input values
    item.name = request.form.get('name')
    # we have to rename the image associated with this item if the name changes
    # we change the name of the image before saving to 'images' folder because some images have really long names
    # and naming image after the food it is associated with makes it easier to find in the images folder
    os.renames(target + item.item_image, target + item.name + '.jpg')
    item.price = request.form.get('price')
    item.description = request.form.get('description')
    item.gluten_free = request.form.get('gluten_free')
    item.vegan = request.form.get('vegan')
    item.menu_type = request.form.get('menu_type')
    tmp_file = request.files.get('file')
    item.item_image = item.name + '.jpg'
    # if filename empty then do nothing because user doesn't want to change the item image
    if tmp_file.filename != '':
        os.unlink(os.path.join(target, item.item_image))
        # else change the image
        filename = item.name + '.jpg'
        destination = "/".join([target, filename])
        tmp_file.save(destination)
        # save the image name to item.item_image to call it later when it is needed to be displayed
        item.item_image = filename
    db.session.commit()
    # return to edit menu html
    flash('Item edited!', category="success")
    return redirect(url_for('views.edit_menu'))
