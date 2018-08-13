#!/usr/bin/env python2.7
import json
import random
import string
import httplib2
import requests
from database_setup import Base, Item, Category, User

from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask import session as login_session

from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# helper functions for user


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# create route for login and generate anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v2/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # store desired data in the session
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # if user doesn't exist, make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '<h1> Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src=" '
    output += login_session['picture']
    output += (' " style= "width: 300px; height:300px; border-radius: 150px;'
               '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> ')
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# DISCONNECT
@app.route("/gdisconnect")
def gdisconnect():
    # only disconnect if user is connected
    access_token = login_session.get('access_token')
    if access_token is None:
        flash('Current user not connected')
        return redirect('/')

    login_session.clear()
    flash('Successfully disconnected.')
    return redirect('/')


# JSON APIs to view catalog Information
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


# JSON for items
@app.route('/catalog/<category_id>/<item_id>.json')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    return jsonify(item.serialize)


# Home
@app.route('/catalog')
@app.route('/')
def home():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latest = session.query(Item).order_by(Item.id.desc()).limit(8).all()
    return render_template('home.html', categories=categories,
                           latest_items=latest)


# Longer paths with the item names and categories for
# Search engine optimization, but simplicity can also be nice
@app.route('/catalog/<category_id>/<item_id>')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    # if user is not the creator, show public version
    if ('username' not in login_session or
            login_session['user_id'] != item.user_id):
        return render_template('public_showitem.html', item=item)
    else:
        return render_template('showitem.html', item=item)


@app.route('/catalog/newitem', methods=['GET', 'POST'])
def addItem():
    # if user is not connected, redirect to login
    access_token = login_session.get('access_token')
    if access_token is None:
        return redirect('/login')
    else:
        if request.method == 'POST':
            category = session.query(Category).filter_by(
                name=request.form['category']).one_or_none()
            item = Item(title=request.form['title'],
                        description=request.form['description'],
                        user_id=login_session['user_id'])
            category.items.append(item)
            session.commit()
            flash('New item %s successfully created' % item.title)
            return redirect('/')
        else:
            categories = session.query(Category).all()
            return render_template('newitem.html', categories=categories)


@app.route('/catalog/<category_id>/<item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    # if user is not creator, redirect to home and flash
    if ('username' not in login_session or
            login_session['user_id'] != item.user_id):
        flash("You are not authorized to edit this item.")
        return redirect('/')
    else:
        if request.method == 'POST':
            if request.form['title'] != item.title:
                item.title = request.form['title']
            if request.form['description'] != item.description:
                item.description = request.form['description']
            if request.form['category'] != item.category.name:
                category = session.query(Category).filter_by(
                    name=request.form['category']).one_or_none()
                item.category = category
            session.commit()
            flash('%s succesfully edited' % item.title)
            return redirect('/')
        else:
            categories = session.query(Category).all()
            return render_template('edititem.html', item=item,
                                   categories=categories)


@app.route('/catalog/<category_id>/<item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    # if user is not creator, redirect to home and flash
    if ('username' not in login_session or
            login_session['user_id'] != item.user_id):
        flash("You are not authorized to delete this item.")
        return redirect('/')
    else:
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            flash('%s succesfully deleted' % item.title)
            return redirect('/')
        else:
            return render_template('deleteitem.html', item=item)


@app.route('/catalog/newcategory', methods=['GET', 'POST'])
def addCategory():
    # if user is not connected, redirect to login
    access_token = login_session.get('access_token')
    if access_token is None:
        return redirect('/login')
    else:
        if request.method == 'POST':
            category = Category(name=request.form['name'],
                                user_id=login_session['user_id'])
            session.add(category)
            flash('New category %s, successfully created' % category.name)
            session.commit()
            return redirect('/')
        else:
            return render_template('newcategory.html')


@app.route('/catalog/<category_id>/items')
def showCategory(category_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    # if user is not the creator, show public version
    if ('username' not in login_session or
            login_session['user_id'] != category.user_id):
        return render_template('public_showcategory.html',
                               main_category=category, categories=categories)
    else:
        return render_template('showcategory.html', main_category=category,
                               categories=categories)


@app.route('/catalog/<category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    # if user is not creator, redirect to home and flash
    if ('username' not in login_session or
            login_session['user_id'] != category.user_id):
        flash("You are not authorized to edit this category.")
        return redirect('/')
    else:
        if request.method == 'POST':
            category.name = request.form['name']
            flash('Category successfullly edited %s' % category.name)
            session.commit()
            return redirect(url_for('showCategory',
                                    category_id=category.id))
        else:
            return render_template('editcategory.html', category=category)


@app.route('/catalog/<category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    # if user is not creator, redirect to home and flash
    if ('username' not in login_session or
            login_session['user_id'] != category.user_id):
        flash("You are not authorized to delete this category.")
        return redirect('/')
    else:

        if request.method == 'POST':
            session.delete(category)
            flash('%s successfully deleted' % category.name)
            session.commit()
            return redirect('/')
        else:
            return render_template('deletecategory.html', category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
