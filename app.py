from flask import Flask, render_template, redirect, url_for, flash, logging, request
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
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
                #Passed
            else:
                error = 'Invalid password'
                return render_template('login.html', error = error)
        else:
            error = 'Username not found'
            return render_template('login.html',error = error)

        #where do I close the db connection
        #cur.close()


    return render_template('login.html')

@APP.route('/products')
def products():
    return render_template('products.html', productslist = maindata.getProducts('broccoli'))

if __name__ == '__main__':
    APP.run()