from multiprocessing import connection
from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime as dt
import yaml

app = Flask(__name__,static_folder='./static',static_url_path='/static')

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e'

#Configure my sql db details
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('auth/login.html')

# http://localhost:5000/hrmslogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/hrmslogin', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html',title="Login")

# http://localhost:5000/pythinlogin/register 
# This will be the registration page, we need to use both GET and POST requests
@app.route('/hrmslogin/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'id' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM accounts WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        elif not username or not password or not email or not id:
            flash("ID already exists","danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            #cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username,email, password))
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s, %s)', (id, username, password, email))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html',title="Register")


#End Point - Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('/'))
    #return render_template('auth/login.html',title="Login")

# http://localhost:5000/pythinlogin/home 
# This will be the home page, only accessible for loggedin users

@app.route('/hrmslogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home/home.html', username=session['username'],title="Home")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))    


@app.route('/hrmslogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('auth/profile.html', username=session['username'],title="Profile")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#End Point - To display all the Course Details
@app.route('/course_list')
def course_list():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from course")
    if resultValue > 0:
        courseSelectDetails = cur.fetchall()
        return render_template('course_list.html',courseSelectDetails=courseSelectDetails)


#End Point - Update the Course table in MySQL Database
@app.route('/insert_course', methods=['GET','POST'])
def insert_course():
    if request.method == 'POST':
    # Fetch form data
        insertCourseDetails = request.form
        course_id = insertCourseDetails['course_id']
        credit_hours = insertCourseDetails['credit_hours']
        course_name = insertCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO course (course_id, credit_hours, course_name) VALUES (%s, %s, %s)",(course_id, credit_hours, course_name))
        mysql.connection.commit()
        cur.close()
        msg = "Successfully Added a new Course"
        return redirect('/course_list')
        
    else:
        return render_template('insert_course.html')

#End Point - Delete the Course table in MySQL Database
@app.route('/delete_course', methods=['GET','POST'])
def delete_course():
    if request.method == 'POST':
    # Fetch form data
        deleteCourseDetails = request.form
        course_id = deleteCourseDetails['course_id']
        credit_hours = deleteCourseDetails['credit_hours']
        course_name = deleteCourseDetails['course_name']        
        cur = mysql.connection.cursor()      
        cur.execute("DELETE FROM course WHERE course_id = %s AND credit_hours = %s AND course_name = %s", (course_id,credit_hours,course_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    else:
        return render_template('delete_course.html')

#End Point - Update a Course table in MySQL Database
@app.route('/update_course',methods=['GET','POST'])
def update_course():
    if request.method == 'POST':
    # Fetch form data
        updateCourseDetails = request.form
        course_id = updateCourseDetails['course_id']
        credit_hours = updateCourseDetails['credit_hours']
        course_name = updateCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        updateResult = cur.execute("UPDATE course SET credit_hours = %s, course_name = %s WHERE course_id = %s", (credit_hours, course_name, course_id))
        if updateResult > 0:
            updateCourseDetails = cur.fetchall()
            #return render_template('update_details.html',updateCourseDetails=updateCourseDetails )
            print(updateCourseDetails)
            flash("Data Updated Sucessfully")
        mysql.connection.commit()
        cur.close()
        #return redirect('/course_list')
        return redirect(url_for('course_list'))
    else:
        return render_template('update_course.html')

#End Point for Training Programs Module
@app.route('/training_programs')
def training_programs():
    #return render_template('home.html', username = session['username'])
    return render_template('training_programs.html') 

#End Point - To display all the Completed trainings
@app.route('/completed_trainings')
def completed_trainings():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from training_table")
    if resultValue > 0:
        trainingSelectDetails = cur.fetchall()
        return render_template('completed_trainings.html',trainingSelectDetails=trainingSelectDetails)

#End Point - Add a new course details in MySQL Database of course table
@app.route('/insert_training', methods=['GET','POST'])
def insert_training():
    if request.method == 'POST':
    # Fetch form data
        insertTrainingDetails = request.form
        training_id = insertTrainingDetails['training_id']
        emp_id = insertTrainingDetails['emp_id']
        platform = insertTrainingDetails['platform']
        doc = dt.datetime.strptime(request.form['doc'], '%Y-%m-%d')
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO training_table (training_id, emp_id, platform, date_of_completion) VALUES (%s, %s, %s, %s)",(training_id, emp_id, platform, doc))
        mysql.connection.commit()
        cur.close()
        return redirect('/completed_trainings')
    else:
        return render_template('insert_training.html')

#End Point - Delete aCourse record from course table in MySQL Database
@app.route('/delete_training', methods=['GET','POST'])
def delete_training():
    if request.method == 'POST':
    # Fetch form data
        deleteTrainingDetails = request.form
        training_id = deleteTrainingDetails['training_id']
        emp_id = deleteTrainingDetails['emp_id']
        cur = mysql.connection.cursor()      
        cur.execute("DELETE FROM training_table WHERE training_id = %s AND emp_id = %s", (training_id, emp_id))
        mysql.connection.commit()
        cur.close()
        return redirect('/completed_trainings')
    else:
        return render_template('delete_training.html')

#End Point - Update a training record in MySQL Database for training table
@app.route('/update_training',methods=['GET','POST'])
def update_training():
    if request.method == 'POST':
        training_id = request.form['training_id']
        emp_id = request.form['emp_id']
        platform = request.form['platform']
        doc = request.form['date_of_completion']
        doc = dt.datetime.strptime(request.form['date_of_completion'],'%Y-%m-%d')
        #date_of_completion = updateTrainingDetails[datetime.strptime(request.form['date_of_completion'], '%Y-%m-%d')]
        #doc = dt.datetime.strptime(request.form['doc'], '%Y-%m-%d')
        cur = mysql.connection.cursor()      
        #cur.execute("UPDATE training_table SET emp_id = %s, platform = %s, date_of_completion = %s WHERE training_id = %s", (emp_id, platform, doc, training_id))
        cur.execute("UPDATE training_table SET emp_id = %s, platform = %s, date_of_completion = %s WHERE training_id = %s", (emp_id, platform, doc, training_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('/completed_trainings'))
    else:
        return render_template('update_training.html')

# End Point - To get a list of Course Completed from a particular training Program from MySQL Database - Join Operation
# 
@app.route('/employee_trainings', methods=['GET','POST'])
def employee_trainings():
    if request.method == 'POST':
    # Fetch form data
        #employeeTrainingDetails = request.form
        #training_id = employeeTrainingDetails['training_id']
        training_id = request.form['training_id']
        cur = mysql.connection.cursor() 
        try:     
            cur.execute("SELECT c.COURSE_ID,c.CREDIT_HOURS, c.COURSE_NAME  from course c JOIN course_training ct ON c.COURSE_ID = ct.COURSE_ID AND ct.TRAINING_ID = %s", (training_id))
            print("COURSE_ID CREDIT_HOURS COURSE_NAME")
            for row in cur:
                print("%s %s %s"%(row[0],row[1],row[2]))
        except:        
        #mysql.connection.commit()
            cur.connection.rollback()
            flash("Operation Completed")
        cur.close()
        return redirect('/completed_trainings')
    else:
        return render_template('employee_trainings.html')

if __name__ =='__main__':
	app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')