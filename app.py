from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

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

@app.route("/aboutus")
def about():
    return render_template("about.html")

@app.route("/shopsingle")
def shopsingle():
    return render_template("shop-single.html")

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

@app.route("/shop")
def shop():
    return render_template("shop.html")

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
