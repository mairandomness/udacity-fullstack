from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def menu_json(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id)
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItem=[i.serialize for i in menu])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menu_item_json(menu_id):
    menu_item = session.query(MenuItem).filterby(id = menu_id).one()
    return jsonify(MenuItem=menu_item.serialize)


@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def create_new_item(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name = request.form['name'], restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for('restaurant_menu', restaurant_id = restaurant_id))
    else:
        return render_template('new_menu_item.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def edit_menu_item(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
       item.name = request.form['name']
       session.commit()
       flash("Saved changes!")
       return redirect(url_for('restaurant_menu', restaurant_id = restaurant_id))
    else:
       return render_template('edit_item.html', restaurant_id=restaurant_id, menu_id = menu_id, item=item)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def delete_menu_item(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
       session.delete(item)
       session.commit()
       flash("Item deleted!")
       return redirect(url_for('restaurant_menu', restaurant_id = restaurant_id))
    else:
       return render_template('delete_item.html', restaurant_id=restaurant_id, menu_id = menu_id, item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
