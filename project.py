from flask import Flask, request, jsonify, redirect, render_template, flash, url_for, session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Puppy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
import os
import random
import string
import datetime
import json
import httplib2
import requests


engine = create_engine('sqlite:///puppies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Flask instance created
app = Flask(__name__)

# Connect to database
engine = create_engine('postgresql://item_catalog.db')
Base.metadata.bind = engine

# Creating a session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# ADD LOGIN/AUTHENTICATION/USERS STUFF HERE
@app.route('/login')
def veiwLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    
    return render_template('login.html', STATE=state)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))





# Flask Routing

@app.route('/')
@app.route('/catalog')
def viewCatalog():
    categories = session.query(Category)
    items = session.query(Item)
    return render_template('catalog.html', categories=categories, items=items)

@app.route('/catalog/<int:category_id>/items')
def viewCategory(category_id):
    categories = session.query(Category)
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('items.html', category=category, categories=categories, items=items)

@app.route('/catalog/<int:category_id>/<int:item_id>')
def viewItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id)
    item = session.query(Item).filter_by(id=item_id)
    creator = session.query(User).filter_by(id=user_id).one()
    if creator.id != login_session['user_id'] or 'username' not in login_session:    
        return render_template('detailed-public-item.html', category=category, item=item)
    else():
        return render_template('detailed-user-item.html', category=category, item=item)



@app.route('/catalog/<int:category_id>/new', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    if request.method == 'GET': # Show the add form
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('new-item.html', categories=categories)
    else: # Add the Item
        newItem = Item(
            name = request.form['name'],
            description = request.form['description'],
            category = session.query(Category).filter_by(name=request.form['Category'])
            # TODO: Add user_id --> user_id = request.form['user']
        )
        session.add(newItem)
        session.commit()
        flash('Item has been added successfully')
        return redirect(url_for('items',category_id=category_id)




if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
