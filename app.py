from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import stripe

publishable_key = 'pk_test_51N0L1ICDqTHHVoreuFuzby1LMly59U7GQNPfM2kaNvLDkDyWsKGvJldVNlcXFOhJ7kwrnaVaaXoea4Hhluy3pa9000XXVuHYgJ'

stripe.api_key = 'sk_test_51N0L1ICDqTHHVorep6O29dlON7lhF5EdyMU8ZukpN5Odbudr2WArnORDT2wum2dEFPrc1vfJ7NszWKDVDGuXjYqA00qys6wplI'

app = Flask(__name__)
app.secret_key = "screen"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'alx'

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/payment", methods =['POST'])
def payment():
    amount = request.form.get('price')
    description = request.form.get('description')
    customer = stripe.Customer.create(
            email= request.form['stripeEmail'],
            source= request.form['stripeToken'],
)
    charge = stripe.Charge.create(
            customer = customer.id,
            description = description,
            amount = amount, currency='usd',
            )
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route("/aboutus")
def about():
    return render_template("about.html")

@app.route("/shopsingle")
def shopsingle():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT id, name, model, barcode, price, description FROM market')
    marketing = cur.fetchall()

    cur.execute('SELECT id, name, model, barcode, price, description FROM marketdisplay')
    marketingdisplay = cur.fetchall()
    return render_template("shop-single.html", marketing = marketing, marketingdisplay = marketingdisplay )

@app.route("/shopsingle1")
def shopsingle1():
    return render_template("shop-single1.html")

@app.route("/contact", methods =[ 'POST','GET'])
def contact():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'subject' in request.form and 'message' in request.form:
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO contact VALUES (NULL, %s, %s, %s, %s)', (name, email, subject, message))
        mysql.connection.commit()
        message = 'You have successfully sent !'
        return render_template("contact.html", message = message)
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('contact.html', message = message)

@app.route("/shop", methods =[ 'POST','GET'])
def shop():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT id, name, model, barcode, price, description FROM market')
    marketing = cur.fetchall()

    cur.execute('SELECT id, name, model, barcode, price, description FROM marketdisplay')
    marketingdisplay = cur.fetchall()
    return render_template("shop.html", marketing = marketing, marketingdisplay = marketingdisplay )

@app.route("/user")
def user():
    return render_template("user.html")

@app.route('/market', methods =[ 'POST','GET'])
def market():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'model' in request.form and 'barcode' in request.form and 'price' in request.form and 'description' in request.form:
        name = request.form['name']
        model = request.form['model']
        barcode = request.form['barcode']
        price = request.form['price']
        description = request.form['description']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM market WHERE barcode = %s', (barcode, ))
        market = cursor.fetchone()
        if market:
            message = 'Account already exists !'
        else:
            cursor.execute('INSERT INTO market VALUES (NULL, %s, %s, %s, %s, %s)', (name, model, barcode, price, description))
            mysql.connection.commit()

            cursor.execute('INSERT INTO marketdisplay VALUES (NULL, %s, %s, %s, %s, %s)', (name, model, barcode, price, description))
            mysql.connection.commit()

            message = 'You have successfully queue an item !'
            return render_template("user.html", message = message)
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('market.html', message = message)


@app.route("/login", methods =["GET", "POST"])
def login():
    message = ""
    if request.method == "POST" and "email" in request.form and "password" in request.form:
        email = request.form["email"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE email = % s AND password = % s", (email, password, ))
        user = cursor.fetchone()
        if user:
            session["loggedin"] = True
            session["userid"] = user["userid"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            message = "Logged in successfully !"
            return render_template("user.html", message = message)
        else:
            message = "Please enter correct email / password !"
    return render_template("login.html", message = message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'repassword' in request.form:
        name = request.form['name']
        password = request.form['password']
        repassword = request.form['repassword']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not name or not password or not email:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s)', (name, email, password, repassword))
            mysql.connection.commit()
            message = 'You have successfully registered !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message = message)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
