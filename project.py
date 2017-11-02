from flask import Flask, request, jsonify, redirect, render_template, flash, url_for, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from login_decorator import login_required
import os
import random
import string
import datetime
import json
import httplib2
import requests


# Flask instance created
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Creating a session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# ADD LOGIN/AUTHENTICATION/USERS STUFF HERE
@app.route('/login')
def viewLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Add google authentication


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


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

# Disconnect from website


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result.status
    if result.status == 200:
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('viewCatalog'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Flask Routing

@app.route('/')
@app.route('/catalog')
def viewCatalog():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('catalog.html', categories=categories, items=items)

@app.route('/catalog/<int:category_id>/items')
def viewCategory(category_id):
    categories = session.query(Category)
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    count = session.query(Item).filter_by(category_id=category_id).count()
    return render_template('items.html', category=category, categories=categories, items=items, count=count)

@app.route('/catalog/<int:category_id>/<int:item_id>')
def viewItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id)
    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('detailed-public-item.html', category=category, item=item)
    else:
        return render_template('detailed-user-item.html', category=category, item=item, creator=creator)



@app.route('/catalog/<int:category_id>/new', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'GET': # Show the add form
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('new-item.html', category=category)
    else: # Add the Item
        newItem = Item(
            name = request.form['name'],
            description = request.form['description'],
            category = session.query(Category).filter_by(id=category_id).one(),
            picture = request.form['picture'],
            user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item has been added successfully')
        return redirect(url_for('items',category_id=category_id))


@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def updateItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    updatedItem = session.query(Item).filter_by(id=item_id).one()
    creator = session.query(User).filter_by(id=updatedItem.user_id).one()
    # check if user is the creator of the item
    if updatedItem.user_id != login_session['user_id']:
        flash("You must be the creator of an Item to edit it. This item belongs to %s" % creator.name)
        return redirect(url_for('catalog'))
    if request.method == 'GET':
        return render_template('edit-item.html', category=category, updatedItem=updatedItem)
    else:

        newName = request.form['name']
        newDesc = request.form['description']
        newPic = request.form['picture']
        newCat = request.form['category']
        if newName:
            updatedItem.name = newName
        if newDesc:
            updatedItem.description = newDesc
        if newPic:
            updatedItem.picture = newPic
        if newCat:
            updatedItem.item_catalog = newCat
        session.add(updatedItem)
        session.commit()
        flash('Item has been updated successfully')
        return redirect(url_for('viewItem', category_id=category_id, item_id=item_id))

@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def deleteItem(category_id, item_id):
    deleteItem = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(id = category_id).one()
    owner = session.query(User).filter_by(id = deleteItem.user_id)

    if login_session['user'] != owner.id:
        flash('You must be the owner to delete this item. This item belongs to %s.' % owner.name)
        return redirect(url_for('catalog'))

    if request.method == 'GET':
        return render_template('deleteitem.html', item=deleteItem, category=category)
    else:
        session.delete(deleteItem)
        session.commit()
        flash('Item has been deleted successfully')
        return redirect(url_for('viewCategory', category_id=category_id))

# JSON ENDPOINTs

@app.route('/catalog/JSON')
def catalogJSON():
    json_catalog = session.query(Category).all()
    return jsonify(json_catalog = [c.serialize for c in json_catalog])

@app.route('/catalog/<int:category_id>/items/JSON')
def itemsJSON():
    json_items = session.query(Item).filter_by(category_id = category_id).all()
    return jsonify(json_items = [i.serialize for i in json_items])



if __name__ == '__main__':
    app.secret_key = 'mxmkl6-iBsDY8uWl8YwZQJNM'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
