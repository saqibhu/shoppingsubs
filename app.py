from flask import Flask, render_template, redirect, url_for, flash, logging, request, session
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

import psycopg2
import maindata

APP = Flask(__name__)
APP.secret_key = 'test'

#config postgresql
engine = create_engine('postgresql://saqib:welcome.1@localhost/shoppingsubs')

try:
    conn = psycopg2.connect("dbname='shoppingsubs' user='saqib' host='localhost' password='welcome.1'")
except:
    print "I am unable to connect to the database"

#switch on debug
APP.debug = True

@APP.route('/')
def index():
    return render_template('index.html')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

@APP.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #sql bit
        connection = engine.connect()
        connection.execute('insert into users (name, email, username, password) values (%s, %s, %s, %s)', (name, email, username, password))
        connection.close()

        flash('You are now registered', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form = form)

@APP.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select * from users where username = '%s'""" % username)
        result = cur.fetchone()

        if result > 0:
            password = result['password']

            #Compare password
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('products'))
            else:
                error = 'Invalid password'
                return render_template('login.html', error = error)

            #Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error = error)

        #where do I close the db connection
        #cur.close()


    return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorize, please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@APP.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@APP.route('/products', methods=['GET', 'POST'])
@is_logged_in
def products():
    if request.method == 'POST':
        return render_template('products.html', productslist = maindata.getProducts(request.form['inputProduct']))
    else:
        return render_template('products.html')

@APP.route('/subscribe', methods=['GET','POST'])
@is_logged_in
def subscribe():
    if request.method == 'POST':
        print 'Woohoo - Request is ' + request.form['name'] + ' ' +  request.form['price'] + ' with an id of ' + request.form['id']
    
    #Add subscription to database

    return redirect(url_for('products'))

if __name__ == '__main__':
    APP.run()