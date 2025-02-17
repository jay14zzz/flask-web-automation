from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from sqlite3 import IntegrityError

import os
from datetime import datetime
import random
import string

from flask import send_file
import pandas as pd

from flask import jsonify
from selenium_scripts.seleniumDriverCheck import selenium_driver_check
# from selenium_scripts.loginCheck import test_login_combinations
from selenium_scripts.loginCheckV2 import test_login_combinations
from selenium_scripts.dropdownCheck import dropdown_check
from selenium_scripts.dropdown2Check import dropdown2_check

# from loginCheck import test_login_combinations

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration to remove trailing slashes
app.url_map.strict_slashes = False


# Function to initialize the admin database
def initialize_admin_database():
    conn = sqlite3.connect('admin_users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS admin_users (username TEXT PRIMARY KEY, password TEXT, status INTEGER)')
    conn.commit()

    # Check if there are no records in the admin_users table
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    count = cursor.fetchone()[0]

    # If there are no records, insert the default admin users
    if count == 0:
        # Define multiple admin users
        admins = [
            ('jsadmin', 'jsadminpassword', 1),
            ('js2admin', 'js2adminpassword', 2),
            ('admin', 'adminpassword', 1)  # Add more admins as needed
        ]
        
        # Insert each admin into the table
        cursor.executemany("INSERT INTO admin_users (username, password, status) VALUES (?, ?, ?)", admins)
        conn.commit()  # Commit the insert operations

    conn.close()

# Function to view all admin users
def view_admins():
    conn = sqlite3.connect('admin_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin_users')
    admins = cursor.fetchall()
    conn.close()
    return admins

# Function to validate admin login credentials
def validate_admin_login(username, password):
    conn = sqlite3.connect('admin_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin_users WHERE username = ? AND password = ?', (username, password))
    admin_user = cursor.fetchone()
    conn.close()
    return admin_user

# Function to add a new admin user to the database
def add_admin(username, password):
    conn = sqlite3.connect('admin_users.db')
    cursor = conn.cursor()
    # cursor.execute('INSERT INTO admin_users (username, password, status) VALUES (?, ?, ?)', (username, password, 3))
    # conn.commit()
    # conn.close()
    try:
        cursor.execute('INSERT INTO admin_users (username, password, status) VALUES (?, ?, ?)', (username, password, 3))
        conn.commit()
    except IntegrityError:
        # Handle the case where the username already exists
        conn.rollback()  # Rollback the transaction
        return False     # Return False to indicate failure
    finally:
        conn.close()
    return True  # Return True to indicate success

# Function to add a new admin user to the database
def add_admin_with_status(username, password, status):
    conn = sqlite3.connect('admin_users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO admin_users (username, password, status) VALUES (?, ?, ?)', (username, password, status))
    conn.commit()
    conn.close()

# Function to delete an admin user
def delete_admin(username):
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE username = ?', (username,))
    conn.commit()
    conn.close()

# Function to initialize the database
def initialize_user_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, status INTEGER)')
    conn.commit()
    conn.close()

# Function to validate login credentials
def validate_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to add a new user to the database
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # cursor.execute('INSERT INTO users (username, password, status) VALUES (?, ?, ?)', (username, password, 0))
    # conn.commit()
    # conn.close()
    # above line commented to handle existing username

    try:
        cursor.execute('INSERT INTO users (username, password, status) VALUES (?, ?, ?)', (username, password, 0))
        conn.commit()
    except IntegrityError:
        # Handle the case where the username already exists
        conn.rollback()  # Rollback the transaction
        return False     # Return False to indicate failure
    finally:
        conn.close()
    return True  # Return True to indicate success

def view_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Function to initialize the user data database
def initialize_user_details_database():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    # cursor.execute('''CREATE TABLE IF NOT EXISTS uploads (
    #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                     username TEXT,
    #                     url TEXT,
    #                     identifier TEXT,
    #                     file_path TEXT,
    #                     upload_datetime TEXT,
    #                     unique_id TEXT,
    #                 )''')
    
    cursor.execute('CREATE TABLE IF NOT EXISTS user_uploads (id INTEGER PRIMARY KEY AUTOINCREMENT, unique_id INTEGER, username TEXT, url TEXT, identifier TEXT, file_name TEXT, file_path TEXT, file_upload_remark TEXT, uploaded_at DATETIME)')
    cursor.execute('CREATE TABLE IF NOT EXISTS login_comb (id INTEGER PRIMARY KEY AUTOINCREMENT, unique_id INTEGER, login_comb_id INTEGER, username TEXT, url TEXT, identifier TEXT, file_name TEXT, file_path TEXT, file_upload_remark TEXT, login1 TEXT, login2 TEXT, password1 TEXT, password2 TEXT, login_remark TEXT, login_comb_uploaded_at DATETIME)  ')   

    conn.commit()
    conn.close()

# Function to generate unique ID
def generate_unique_id():
    return random.randint(100000, 999999)

# Function to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' in session:
        username = session['username']
        url = request.form['url']
        identifier = request.form['identifier']
        remark = request.form['remark']
        file = request.files['file']
        if file:
            # Create directory for user if it doesn't exist
            user_dir = os.path.join('uploads', username)
            os.makedirs(user_dir, exist_ok=True)

            # Generate unique ID
            unique_id = generate_unique_id()

            # Generate a random string to append to the filename
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Append random string and unique ID to the filename
            filename, file_extension = os.path.splitext(file.filename)
            new_filename = f"{filename}_{random_string}_{unique_id}{file_extension}"
            
            if not new_filename.endswith(('.xls', '.xlsx', '.csv')):
                return f"""
                    <script type="text/javascript">
                        alert("Invalid file uploaded");
                        window.location.href = ("/upload");
                    </script>
                """

            # # Save file to user directory
            # filename = file.filename
            # file_path = os.path.join(user_dir, filename)
            # file.save(file_path)

            # Save file with the new filename
            file_path = os.path.join(user_dir, new_filename)
            file.save(file_path)
            
            
            # Store data in the user uploads database
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            upload_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''INSERT INTO user_uploads 
                            (unique_id, username, url, identifier,file_name, file_path, file_upload_remark, uploaded_at ) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (unique_id, username, url, identifier, new_filename, file_path, remark, upload_datetime ))
            conn.commit()
            conn.close()
            
            # return redirect('/verify')  # Redirect to verification page after successful upload #commented to debug
            # # return redirect('/upload')

            uid = str(unique_id)
            alert_message = "This is a popup alert test ! "  + "File uploaded and saved with UID (Unique ID): "+ uid +" use this UID in login combination and age combination form."
            redirect_url = url_for('verify')
            return f"""
                <script type="text/javascript">
                    alert("{alert_message}");
                    window.location.href = "{redirect_url}";
                </script>
            """
        
        else:
            return "No file uploaded"
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in

# Function to handle login comb form
@app.route('/upload_login', methods=['POST'])
def upload_login_comb():
    if 'username' in session:
        username = session['username']
        unique_id = request.form['unique-id']
        file_path = get_file_path(unique_id,username)
        login_remark = request.form['login-comb-remark']
        login1 = request.form['login1']
        login2 = request.form['login2']
        password1 = request.form['password1']
        password2 = request.form['password2']
        login_remark = request.form['login-comb-remark']

        # Fetch existing data using unique_id
        file_upload_data = get_user_upload_data_with_uniqueID(unique_id,username)
        if not file_upload_data:
            return jsonify({'error': 'Unique ID not found'}), 404
        url, identifier, file_name, file_path, file_upload_remark = file_upload_data

        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        login_comb_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        login_comb_id = generate_unique_id()
        cursor.execute('''INSERT INTO login_comb 
                            (unique_id, login_comb_id, username, url, identifier,file_name, file_path, file_upload_remark, login1, login2, password1, password2, login_remark, login_comb_uploaded_at ) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (unique_id, login_comb_id, username, url, identifier, file_name, file_path, file_upload_remark, login1, login2, password1, password2, login_remark, login_comb_datetime ))
        conn.commit()
        conn.close()
        uid = str(unique_id)
        lid = str(login_comb_id)
        # return redirect('/verify')
        ## pop up to display unique ID.
        alert_message = "This is a popup alert test ! "  + "Login combination saved for uid: "+ uid+ " with combination reference id = "+ lid+" use this reference id while running....."
        redirect_url = url_for('verify')
        return f"""
            <script type="text/javascript">
                alert("{alert_message}");
                window.location.href = "{redirect_url}";
            </script>
        """
    
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in

# Function to retrieve user uploads data with uniqueID to merge with login or age combination data
def get_user_upload_data_with_uniqueID(unique_id,username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, identifier, file_name, file_path, file_upload_remark FROM user_uploads WHERE username = ? AND unique_id = ? ', (username,unique_id))
    data = cursor.fetchone()
    conn.close()
    return data

# Function to retrieve user uploads
def get_user_uploads(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_uploads WHERE username = ?', (username,))
    uploads = cursor.fetchall()
    conn.close()
    #return uploads  # comented to return the value in a different data type

    # Converting the list of tuples to a list of dictionaries to display it
    uploads_dict = []
    for upload in uploads:
        upload_dict = {
            #'id': upload[0], # commented id since it is not required for the user(and also bcoz id increments for all user)
            'unique_id': upload[1],
            'username': upload[2],
            'url': upload[3],
            'identifier': upload[4],
            'file_name' : upload[5],
            #'file_path': upload[6],
            'file_upload_remark': upload[7],
            'uploaded_at': upload[8],
            
        }
        uploads_dict.append(upload_dict)
    return uploads_dict

# Function to retrieve login combination table
def get_login_comb(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM login_comb WHERE username = ?', (username,))
    login_comb = cursor.fetchall()
    conn.close()
    # Convert the list of tuples to a list of dictionaries to display it
    login_comb_dict = []
    for login in login_comb:
        login_dict = {
            #'id': login[0], # commented id since it is not required for the user(and also bcoz id increments for all user)
            'unique_id': login[1],
            'login_comb_id': login[2],
            'username': login[3],
            'url': login[4],
            'identifier': login[5],
            'file_name' : login[6],
            #'file_path': login[7],
            'file_upload_remark': login[8],
            'login1': login[9],
            'login2': login[10],
            'password1': login[11],
            'password2': login[12],
            'login combination remark': login[13],
            'login combination uploaded at': login[14],
            
        }
        login_comb_dict.append(login_dict)
    return login_comb_dict

# Function to retrieve login combination data with login_comb_id to pass the value to loginCheck.py script
def get_login_comb_data(username, login_comb_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, file_path, login1, login2, password1, password2 FROM login_comb WHERE username = ? AND login_comb_id = ? ', (username, login_comb_id))
    data = cursor.fetchone()
    conn.close()
    return data

# Function to retrieve age combination table -- TO BE DEVELOPED
# def get_age_comb(username):
#     conn = sqlite3.connect('user_data.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM age_comb WHERE username = ?', (username,))
#     age_comb = cursor.fetchall()
#     conn.close()
#     # Convert the list of tuples to a list of dictionaries to display it
#     age_comb_dict = []
#     for age in age_comb:
#         age_dict = {
#             'unique_id': age[0],
#             'age1': age[1],
#             'age2': age[2],
#             'remark': age[3],
#         }
#         age_comb_dict.append(age_dict)
#     return age_comb_dict

# Function to view all user uploads (!!!!for ADMIN or DEBUG only!!!!)
def view_all_user_uploads():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_uploads')
    uploads = cursor.fetchall()
    conn.close()
    return uploads

def get_file_path(unique_id,username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM user_uploads WHERE unique_id = ? AND username = ?',(unique_id,username))
    file_path = cursor.fetchone() # use fetchone() instead of fetchall() to retrieve only the first matching row
    conn.close()
    return file_path[0] if file_path else None  # Return the first element of the tuple or None if no match found
    # return file_path

# Function to handle viewing the file contents
def view_file(file_path):
    # Check the file extension to determine the appropriate method for reading the file
    if file_path.endswith('.csv'):
        # Read CSV file using pandas
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        # Read Excel file using pandas
        df = pd.read_excel(file_path)
    else:
        return "Unsupported file format"

    # Convert DataFrame to HTML table
    file_contents = df.to_html(index=False)
    return file_contents


def fetch_unique_ids(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT unique_id FROM user_uploads WHERE username = ?", (username,))
    unique_ids = [row[0] for row in cursor.fetchall()]
    # Close the cursor
    cursor.close()
    # Return the unique IDs
    return unique_ids

def fetch_details(username,unique_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    # Fetch details based on unique ID
    cursor.execute("SELECT url, identifier, file_name, file_path, file_upload_remark FROM user_uploads WHERE username = ? and unique_id = ?", (username,unique_id))
    details = cursor.fetchone()
    # Close the cursor
    cursor.close()
    # Return the details
    return details

def get_column_names(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError('Unsupported file format')
    
    # Get column names
    column_names = df.columns.tolist()
        
    return {'columns': column_names}

def fetch_login_comb_ids(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT login_comb_id FROM login_comb WHERE username = ?", (username,))
    login_comb_id = [row[0] for row in cursor.fetchall()]
    # Close the cursor
    cursor.close()
    # Return the unique IDs
    return login_comb_id

##################### --------- END OF Functions -------------- ################ page routes start

# Route for index (default) page
@app.route('/')
def index_default():
    return render_template('user/index.html')

# Route for index page
@app.route('/index')
def index():
    return render_template('user/index.html')

# Route for home page
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('user/home.html', username=session['username'], active='home')
    else:
        return redirect('/login')

# Route for login page (GET method)
@app.route('/login', methods=['GET'])
def show_login_form():
    return render_template('user/login.html')

# Route for signup page (GET method)
@app.route('/signup', methods=['GET'])
def show_signup_form():
    return render_template('user/signup.html')


# Route for login (POST method)
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = validate_login(username, password)
    if user:
        session['username'] = username
        return redirect('/home')
    else:
        # return 'Invalid username or password'
        # instead of returning a statement, alert msg is displayed for invalid username or password
        alert_message = "Invalid username or password"
        redirect_url = url_for('login')
        return f"""
            <script type="text/javascript">
                alert("{alert_message}");
                window.location.href = "{redirect_url}";
            </script>
        """

# Route for signup (POST method)
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    
    # add_user(username, password)
    # return redirect('/login')
    # above lines commented to handle existing username

    if add_user(username, password):
        return redirect('/login')
    else:
        # return "Username already exists. Please choose a different username."
        # instead of returning a statement, alert msg is displayed for Username already exists
        alert_message = "Username already exists. Please choose a different username"
        redirect_url = url_for('signup')
        return f"""
            <script type="text/javascript">
                alert("{alert_message}");
                window.location.href = "{redirect_url}";
            </script>
        """



# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/upload')
def upload():
    if 'username' in session:
        return render_template('user/upload.html', username=session['username'], active='upload')
    else:
        return redirect('/login')
    

# @app.route('/verify')
# def verify():
#     if 'username' in session:
#         return render_template('user/verify.html', username=session['username'], active='verify')
#     else:
#         return redirect('/login')
    
# Route for verification page
@app.route('/verify')
def verify():
    if 'username' in session:
        username = session['username']
        # Fetch user's uploads from the user_uploads table - user_data.db
        uploads = get_user_uploads(username)
        # Fetch user's login combination from login_comb table - user_data.db
        login_comb = get_login_comb(username)
        # Fetch user's lage combination from age_comb table - user_data.db
        # age_comb = get_age_comb(username)
        return render_template('user/verify.html', username=username, uploads=uploads, login_comb=login_comb, active='verify')
        return redirect('/login')  # Redirect to login page if user is not logged in

# Route to handle viewing the file contents
@app.route('/view_file', methods=['POST'])
def view_file_route():
    # file_path = request.form['file_path']
    # file_contents = view_file(file_path)
    # username=session['username']
    # view file button now fetches filw with unique instead of displaying and selection file path from client side

    unique_id = request.form['unique_id']
    username=session['username']
    file_path = get_file_path(unique_id,username)
    file_contents = view_file(file_path)
    return render_template('user/view_file.html', file_contents=file_contents,username=username)

@app.route('/test_run')
def test_run():
    if 'username' in session:
        return render_template('user/test_run.html', username=session['username'], active='test_run')
    else:
        return redirect('/login')
    

@app.route('/execute')
def execute():
    if 'username' in session:
        return render_template('user/execute.html', username=session['username'], active='execute')
    else:
        return redirect('/login')
    
# Route for dropdown verification page
@app.route('/dropdown')
def dropdown():
    if 'username' in session:
        return render_template('user/dropdown.html', username=session['username'], active='')
    else:
        return redirect('/login')
    
# Route for dropdown verification page
@app.route('/dropdown2')
def dropdown2():
    if 'username' in session:
        return render_template('user/dropdown2.html', username=session['username'], active='')
    else:
        return redirect('/login')

# Route for dropdown verification page
@app.route('/verifylogin')
def verifylogin():
    if 'username' in session:
        return render_template('user/verifylogin.html', username=session['username'], active='')
    else:
        return redirect('/login')

    
# Route for admin login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = validate_admin_login(username, password)
        if admin_user:
            session['admin_username'] = username
            return redirect('/admin/dashboard')
        else:
            return 'Invalid username or password'
    return render_template('admin/admin_login.html')

# Route for admin signup page
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # add_admin(username, password)
        # return redirect('/admin/login')

        if add_admin(username, password):
            return redirect('/admin/login')
        else:
            return "Username already exists. Please choose a different username."
        
    return render_template('admin/admin_signup.html')

# Route for admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_username' in session:
        admins = view_admins()  # Get admin users from admin database
        users = view_users()    # Get regular users from user database
        return render_template('admin/admin_dashboard.html', admins=admins, users=users)
    else:
        return redirect('/admin/login')
    

@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/404.html'), 404
    # return render_template('user/404v2.html'), 404


##################### --------- END OF page routes -------------- ################ ajax routes starts
# Endpoint to fetch unique IDs
@app.route('/fetch_unique_ids')
def fetch_unique_ids_route():

    username=session['username']
    # Fetch unique IDs using the function
    unique_ids = fetch_unique_ids(username)
    # Return the unique IDs as JSON response
    return jsonify(unique_ids)

# Endpoint to fetch details based on unique ID
@app.route('/fetch_details')
def fetch_details_route():
    unique_id = request.args.get('unique_id')
    username=session['username']

    details = fetch_details(username,unique_id)
    # Return the details as JSON response
    return jsonify({
        'url': details[0],
        'identifier': details[1],
        'file_name': details[2],
        # 'file_path': details[3],
        'file_upload_remark' : details[4]
    })

# Route to fetch column names from Excel/CSV file based on unique ID
@app.route('/fetch_column_names')
def fetch_column_names():
    # Get the unique ID from the request query parameters
    unique_id = request.args.get('unique_id')
    username=session['username']

    file_path = get_file_path(unique_id,username)
    # check file path and then call get_column_names and use jsonify within the route
    if file_path:
        try:
            column_names = get_column_names(file_path)
            return jsonify(column_names), 200
        except FileNotFoundError:
            return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File path not found for the given unique ID'}), 404
    
# Endpoint to fetch login comb IDs
@app.route('/fetch_login_comb_ids')
def fetch_login_comb_ids_route():

    username=session['username']
    # Fetch unique IDs using the function
    login_comb_ids = fetch_login_comb_ids(username)
    # Return the unique IDs as JSON response
    return jsonify(login_comb_ids)

# Route for selenium driver check
@app.route('/run_selenium')
def run_selenium():
    if 'username' in session:
        result = selenium_driver_check()
        return jsonify(result), 200 if result["status"] == "success" else 500
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in
    
# Route for dropdown check
@app.route('/run_dropdown_check')
def run_dropdown():
    if 'username' in session:
        url = request.args.get('url')
        id = request.args.get('id')
        result = dropdown_check(url,id)
        return jsonify(result), 200 if result["status"] == "success" else 500
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in
    
# Route for dropdown check
@app.route('/run_dropdown2_check')
def run_dropdown2():
    if 'username' in session:
        url = request.args.get('url')
        id1 = request.args.get('id1')
        id2 = request.args.get('id2')
        result = dropdown2_check(url,id1,id2)
        return jsonify(result), 200 if result["status"] == "success" else 500
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in


# Route to run the login check script
@app.route('/run_login_check')
def run_login_check():
    if 'username' in session:
        username=session['username']
        login_comb_id = request.args.get('login_comb_id')

        # Get login comb data with login comb ID for passing the value to run loginCheck.py script
        login_comb_data = get_login_comb_data(username, login_comb_id)

        url, file_path, login1, login2, password1, password2 = login_comb_data
        # create list for login and password column and append the data
        login_columns = []
        password_columns = []

        login_columns.append(login1)
        if login2 and login2.strip():       # Check if login2 is not empty or None
            login_columns.append(login2)
        
        password_columns.append(password1)
        if password2 and password2.strip():     # Check if password2 is not empty or None
            password_columns.append(password2)

        # Run the selenium script or any other process with the given login_comb_id
        result = test_login_combinations(url, file_path, login_columns, password_columns)  # Implement this function to run your check
        return jsonify(result), 200 if result["status"] == "success" else 500
        return result
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in
    
# Route to verify login check
@app.route('/verify_login_check', methods=['POST'])
def verify_login_check():
    if 'username' in session:
        username=session['username']
        url = request.form.get('url')
        identifier = request.form.get('identifier')
        login1 = request.form.get('login1')
        login2 = request.form.get('login2')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        dob_format = request.form.get('dob_format')
        test_case_number = request.form.get('test_case_number')

        # Process the file
        file = request.files.get('file')
        # Initialize file_path
        file_path = None
        if file:
            # Create directory for user if it doesn't exist
            user_dir = os.path.join('uploads', username)
            os.makedirs(user_dir, exist_ok=True)

            # Generate unique ID
            unique_id = generate_unique_id()

            # Generate a random string to append to the filename
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Append random string and unique ID to the filename
            filename, file_extension = os.path.splitext(file.filename)
            new_filename = f"{filename}_{random_string}_{unique_id}{file_extension}"
            
            if not new_filename.endswith(('.xls', '.xlsx', '.csv')):
                return f"""
                    <script type="text/javascript">
                        alert("Invalid file uploaded");
                        window.location.href = ("/upload");
                    </script>
                """

            # # Save file to user directory
            # filename = file.filename
            # file_path = os.path.join(user_dir, filename)
            # file.save(file_path)

            # Save file with the new filename
            file_path = os.path.join(user_dir, new_filename)
            file.save(file_path)

        else:
            # return "No file uploaded"
            return f"""
                <script type="text/javascript">
                    alert("No file uploaded");
                    window.location.href = ("/verifylogin");
                </script>
            """

        # create list for login and password column and append the data
        login_columns = []
        password_columns = []

        login_columns.append(login1)
        if login2 and login2.strip():       # Check if login2 is not empty or None
            login_columns.append(login2)
        
        password_columns.append(password1)
        if password2 and password2.strip():     # Check if password2 is not empty or None
            password_columns.append(password2)
        # print(type(file_path),file_path)
        # Run the selenium script or any other process with the given login_comb_id
        result = test_login_combinations(url, file_path, login_columns, password_columns, dob_format, test_case_number)  # Implement this function to run your check
        os.remove(file_path)
        return jsonify(result), 200 if result["status"] == "success" else 500
        return result
    else:
        return redirect('/login')  # Redirect to login page if user is not logged in

if __name__ == '__main__':

    initialize_user_database()  # normal user db
    initialize_admin_database()  # admin user db
    initialize_user_details_database() # user data db

    # Initialize the admin database (run this only once) and add admin user manually
    # Add an admin user
    # user_data('jsadmin', 'jsadminpassword', 1)
    # add_admin_with_status('jsadmin', 'jsadminpassword', 1)
    # add_admin_with_status('js2admin', 'js2adminpassword', 2)

    # Code to view all admin users
    # admins = view_admins()
    # print("Admin Users:")
    # for admin in admins:
    #     print(admin)

    # code to view/check all user uploads database
    # user_uploads = view_all_user_uploads()
    # print("User Uploads:")
    # for upload in user_uploads:
    #     print(upload)

    # file_path = get_file_path(465818,'js') # checking get_file_path fn
    # print(file_path)
    # print(get_column_names(file_path)) # pass file path and check the response 

    
    # # # Debug statements for running login script
    # # Read data from the Excel file
    # file_path = 'uploads\js\Sample_DATA (1)_yltRswlq_769134.csv'
    # url = "https://regqc.sifyitest.com/bobfojan24/oecla_may24/login.php?appid=78fc7136fcc5e0413bd46958952aee9b"
    # # Define the login and password field combinations
    # login_columns = ['RegistrationNo', 'Rollno']  # Add your actual column names for Rollno and Registration_No
    # password_columns = ['Password', 'Birthdate']  # Add your actual column names for Password and DOB


    # login_script = test_login_combinations(url, file_path, login_columns, password_columns)
    # print(login_script)


    # print(get_login_comb_data('js', 942271)) # to check get_login_comb_data function, which will then be passed to run the script


    # print(app.url_map) # Prints a detailed list of URL rules (routes) registered in the application, useful for debugging and understanding the application's routing configuration.

    app.run(debug=True)

