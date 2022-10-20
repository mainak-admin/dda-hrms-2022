#from crypt import methods
#from urllib import request
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re 
import yaml

app = Flask(__name__,static_folder='./static',static_url_path='/static')

#Set secret key for the session
app.secret_key = "super secret key"


#Configure my sql db details
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Instantiation of MySQL Object
mysql = MySQL(app)

#End Point -
@app.route('/')
def index():
    return render_template('index.html')

#End Point - Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    #
    msg = "Something Wrong"  
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST': 
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur = mysql.connection.cursor()  
        cur.execute("select * from accounts where username = %s AND password = %s", (username, password,))
        # Fetch one record and return result
        account = cur.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account[1]
            # Redirect to home page
            #return 'Login Suceess'
            return redirect(url_for('home'))
        else:
            # If Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!. Try again'
            # Show the login form with Error message (if any)
    return render_template('index.html', msg = msg)


#End Point - Home Page
@app.route('/home')
def home():
    return render_template('home.html', username = session['username'])


#End Point - Update the Course table in MySQL Database
@app.route('/update_course', methods=['GET','POST'])
def update_course():
    if request.method == 'POST':
    # Fetch form data
        updateCourseDetails = request.form
        course_id = updateCourseDetails['course_id']
        credit_hours = updateCourseDetails['credit_hours']
        course_name = updateCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO course (course_id, credit_hours, course_name) VALUES (%s, %s, %s)",(course_id, credit_hours, course_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    return render_template('update_course.html')
  
#End Point - Select the Course table from  MySQL Database
#End Point - To display all the Course Details
@app.route('/course_list')
def course_list():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from course")
    if resultValue > 0:
        courseSelectDetails = cur.fetchall()
        return render_template('course_list.html',courseSelectDetails=courseSelectDetails)

#This will ensure that any changes made updated immediately on the web browser
if __name__ == '__main__':
  app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')