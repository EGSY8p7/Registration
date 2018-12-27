from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
from flask_login import login_required
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'login'
app.config['MONGO_URI'] = 'mongodb://admin:qwe123@ds141654.mlab.com:41654/login'

mongo = PyMongo(app)



@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('type'))

    return 'Please log in' + render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})
    if login_user:
        if bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    flash('Invalid username/password combination')
    return redirect(url_for('index'))

@app.route('/signout')
def sign_out():
    if 'username' not in session:
        return render_template("index.html")
    session.pop('username')
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass, 'access': 'guest'})
            return redirect(url_for('index'))

        return 'That username already exists!'


    return render_template('register.html')

@app.route('/cabinet')
def type():
    user = mongo.db.users
    teacher = user.find_one({'access' : 'teacher'})
    guest = user.find_one({'access' : 'guest'})
    student = user.find_one({'access' : 'student'})

    if teacher['name'] in session['username']:
        return render_template('teacher.html')
    elif student['name'] in session['username']:
        return render_template('student.html')
    elif guest['name'] in session['username']:
        return 'you are guest'
    return

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
