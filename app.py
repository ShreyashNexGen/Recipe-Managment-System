from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import logging
import datetime
from datetime import datetime
from datetime import timedelta
from flask_socketio import SocketIO, emit
from opcua import Client, ua
from flask import send_from_directory
import threading
from threading import Thread
import time
import requests
import json
import sqlite3
import platform
import subprocess
import wmi  # For Windows systems (install with `pip install WMI`)
from bson import json_util
from pymongo import MongoClient
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
# OPC UA connection options

import os
DB_PATH = 'a2z_database.db'
# DB_PATH = 'Main_database.db'
# Fetch the ENDPOINT_URL dynamically
def fetch_endpoint_url():
    """Fetch plcIp and plcPort from the database and construct ENDPOINT_URL."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Fetch plcIp and plcPort from the database
            cursor.execute("SELECT plcIp, plcPort FROM Plc_Table LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                plc_ip, plc_port = result
                endpoint_url = f"opc.tcp://{plc_ip}:{plc_port}"
                return endpoint_url
            else:
                return "No PLC data available in the database."
    except sqlite3.Error as e:
        return f"Database error: {e}"
ENDPOINT_URL = fetch_endpoint_url()

# Get the base directory of the executable or script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Paths to each database
database1_path = os.path.join(base_dir, 'suvi_database.db')
database2_path = os.path.join(base_dir, 'a2z_database.db')
database3_path = os.path.join(base_dir, 'RMS.db')
# Example: Configure SQLAlchemy or SQLite connections
app.config['DATABASE_1_URI'] = f'sqlite:///{database1_path}'
app.config['DATABASE_2_URI'] = f'sqlite:///{database2_path}'
app.config['DATABASE_3_URI'] = f'sqlite:///{database3_path}'
# SQLite database setup
# Secret key for session encryption
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout


# DB_PATH1 = 'suvi_database.db'
# MONGO_URI = "mongodb://localhost:27017"  # MongoDB URI
# MONGO_DB_NAME = "suvi_flask_db"          # MongoDB Database Name
# MONGO_COLLECTION_NAME = "suvi_flask"       # MongoDB Collection Name      # MongoDB Collection Name
# pos_values = []
# submenu_values =[]
# Function to browser
def init_db():
    """Initialize the SQLite database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Create Tag_Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Tag_Table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tagId TEXT UNIQUE NOT NULL,
                    tagName TEXT UNIQUE NOT NULL,
                    tagAddress TEXT NOT NULL,
                    plcId TEXT NOT NULL
                )
            ''')
            conn.commit()

            # Create Live_Tags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Live_Tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tagId TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tagId) REFERENCES Tag_Table(tagId)
                )
            ''')
            conn.commit()

            # Create Live_Log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Live_Log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tagName TEXT NOT NULL,     
                    tagId TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

            # Create connection_status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connection_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    internet_status TEXT NOT NULL,
                    plc_status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

            # Create internet_status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS internet_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    startTime TEXT NOT NULL,
                    endTime TEXT NOT NULL,
                    time_Duration TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            conn.commit()

            # Create plc_status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plc_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    startTime TEXT NOT NULL,
                    endTime TEXT NOT NULL,
                    time_Duration TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            conn.commit()

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

            # Create user_activity table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    login_time DATETIME,
                    logout_time DATETIME,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            ''')
            conn.commit()

    except sqlite3.Error as e:
        print(f"Error initializing the database: {e}")

# Call the function to initialize the database

init_db()
def setup_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Create Raw_Materials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Raw_Materials (
                    material_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    typeCode TEXT NOT NULL,
                    lotNo TEXT NOT NULL,
                    materialType TEXT NOT NULL UNIQUE,
                    make TEXT NOT NULL,
                    user TEXT NOT NULL,
                    barcode TEXT NOT NULL
                )
            """)
            
            # Create Recipe_Details1 table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipe_Details1 (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Pos1 TEXT,
                    Pos2 TEXT,
                    Pos3 TEXT,
                    Pos4 TEXT,
                    Pos5 TEXT,
                    Pos6 TEXT,
                    Pos7 TEXT,
                    Pos8 TEXT,
                    Pos9 TEXT,
                    Alu_coil_width TEXT,
                    Alu_roller_type INTEGER,
                    Spacer REAL,
                    Recipe_ID INTEGER,
                    FOREIGN KEY (Recipe_ID) REFERENCES Recipe (Recipe_ID)
                )
            """)
            
            # Create Recipe table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipe (
                    Recipe_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Filter_Size TEXT,
                    Filter_Code TEXT,
                    Art_No INTEGER,
                    Recipe_Name TEXT
                )
            """)
            
            # Create Recipe_Log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipe_Log (
                    Batch_No INTEGER PRIMARY KEY AUTOINCREMENT,
                    Batch_Code TEXT NOT NULL,
                    Timestamp TEXT NOT NULL,
                    Recipe_ID INTEGER NOT NULL,
                    motor_speed TEXT,
                    motor_stroke TEXT,
                    other_speed_force TEXT,
                    alu_coil_width TEXT,
                    Quantity INTEGER,
                    Batch_Running_Status TEXT NOT NULL,
                    Batch_Completion_Status TEXT NOT NULL,
                    FOREIGN KEY (Recipe_ID) REFERENCES Recipe (Recipe_ID)
                )
            """)
            
            # Create Sub_Menu table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Sub_Menu (
                    Recipe_ID INTEGER PRIMARY KEY,
                    motor_speed TEXT,
                    motor_stroke TEXT,
                    other_speed_force TEXT,
                    alu_coil_width TEXT,
                    FOREIGN KEY (Recipe_ID) REFERENCES Recipe (Recipe_ID)
                )
            """)

            # Commit changes
            conn.commit()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Plc_Table (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            plcId INTEGER DEFAULT 1,
            plcName VARCHAR(50) DEFAULT 'Plc1',
            plcIp VARCHAR(50) DEFAULT '192.168.1.1',
            plcPort INTEGER DEFAULT 4840,
            intervalTime INTEGER DEFAULT 20,
            serial_Key VARCHAR(50) DEFAULT '12345')""")
            conn.commit()
            
            
# Insert the first entry if the table is empty
            cursor.execute("SELECT COUNT(*) FROM Plc_Table")
            if cursor.fetchone()[0] == 0:  # Check if the table is empty
                cursor.execute("""
             INSERT INTO Plc_Table (plcId, plcName, plcIp, plcPort, intervalTime, serial_Key)
           VALUES (1, 'Plc1', '192.168.1.1', 4840, 20, '11223344')
        """)
                conn.commit()
            
            print("Database setup completed successfully.")

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS BatchTracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number_of_batches_created INTEGER NOT NULL
            )
        ''')
        # Check if there's an entry in the table; if not, insert an initial value
        cursor.execute('SELECT COUNT(*) FROM BatchTracker')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO BatchTracker (number_of_batches_created) VALUES (0)')
            conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error setting up the database: {e}")

# Call the setup function
setup_database()

# Hardcoded user data for simplicity 
USER_DATA = {
    'username': 'admin',
    'password_hash': generate_password_hash('password123')  # Secure hashed password
}
@app.route('/status', methods=['GET'])
def get_status():
    try:
        # Connect to the database
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Fetch PLC IP and Interval Time
            cursor.execute("SELECT plcIp, intervalTime FROM Plc_Table LIMIT 1")
            plc_data = cursor.fetchone()
            plc_ip = plc_data[0] if plc_data else "Not Available"
            interval_time = plc_data[1] if plc_data else "Not Set"

            # Fetch Tag Count
            cursor.execute("SELECT COUNT(*) FROM Tag_Table")  # Replace Tags_Table with actual table
            tags_count = cursor.fetchone()[0]

            # # Fetch Log Count
            # cursor.execute("SELECT COUNT(*) FROM Recipe_Log")  # Replace Logs_Table with actual table
            # logs_count = cursor.fetchone()[0]
            # # Fetch the value of number_of_batches_created from BatchTracker

            cursor.execute('SELECT number_of_batches_created FROM BatchTracker')
            result = cursor.fetchone()
            if result is None:
               logs_count = 0
            else:
               logs_count = result[0]
            # Get Serial Key
            serial_key = platform.node()  # Fetches the computer's hostname as serial key
             # Update serial key in Plc_Table
            cursor.execute("UPDATE Plc_Table SET serial_Key = ? WHERE plcId = 1", (serial_key,))
            conn.commit()  # Commit the transaction

        # Internet and PLC connection statuses
        internet_connected = check_internet_connection()  # Custom function to check internet
        plc_connected = check_plc_connection(plc_ip)  # Custom function to check PLC connection

        # Return the statuses
        return jsonify({
            "Plc_IP": plc_ip,
            "Internet_Connected": internet_connected,
            "Plc_Connected": plc_connected,
            "No_Of_Tags_Created": tags_count,
            "No_Of_Logs_Created": logs_count,
            "Interval_Time_Of_Log_Entry": interval_time,
            "Serial_Key": serial_key
        })
    except Exception as e:
        return jsonify({"error": str(e)})

def check_internet_connection():
    """Check if the server has internet connectivity."""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return "Connected"
    except Exception:
        return "Not Connected"

def check_plc_connection(plc_ip):
    """Check if the PLC is reachable."""
    try:
        import os
        response = os.system(f"ping -n 1 {plc_ip}")  # Replace `-c` with `-n` for Windows
        return "Connected" if response == 0 else "Not Connected"
    except Exception:
        return "Unknown"

def get_last_status(table_name):
    """Retrieve the last status from the specified table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT status FROM {table_name} ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
def get_last_combined_status():
    """Retrieve the last combined status (internet and PLC) from the connection_status table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT internet_status, plc_status FROM connection_status
        ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)
def calculate_duration(start_time, end_time):
    """Calculate the duration between two timestamps."""
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    duration = end - start
    return str(duration)

def log_status():
    """Log statuses for Internet and PLC into tables."""
    # Initialize previous statuses and start times
    last_internet_status = check_internet_connection()
    last_plc_status = check_plc_connection("192.168.1.1")  # Replace with your PLC IP
    internet_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plc_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    while True:
        # Get current statuses
        internet_status = check_internet_connection()
        plc_status = check_plc_connection("192.168.1.1")  # Replace with your PLC IP
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get the last logged combined status
        last_combined_status = get_last_combined_status()

        # Log to connection_status table only if status has changed
        if (internet_status, plc_status) != last_combined_status:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO connection_status (timestamp, internet_status, plc_status)
                VALUES (?, ?, ?)
            """, (current_time, internet_status, plc_status))
            conn.commit()
            conn.close()

        # Handle internet status changes
        if internet_status != last_internet_status:
            last_record_status = get_last_status("internet_status")
            if last_record_status != internet_status:
                duration = calculate_duration(internet_start_time, current_time)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO internet_status (startTime, endTime, time_Duration, status)
                    VALUES (?, ?, ?, ?)
                """, (internet_start_time, current_time, duration, internet_status))
                conn.commit()
                conn.close()

            # Update start time and last status
            internet_start_time = current_time
            last_internet_status = internet_status

        # Handle PLC status changes
        if plc_status != last_plc_status:
            last_record_status = get_last_status("plc_status")
            if last_record_status != plc_status:
                duration = calculate_duration(plc_start_time, current_time)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO plc_status (startTime, endTime, time_Duration, status)
                    VALUES (?, ?, ?, ?)
                """, (plc_start_time, current_time, duration, plc_status))
                conn.commit()
                conn.close()

            # Update start time and last status
            plc_start_time = current_time
            last_plc_status = plc_status

        # Wait for 1 second before the next check
        time.sleep(1)
# log_status(internet_status, plc_status)



@app.route('/status1', methods=['GET'])
def get_status_summary():
    """Fetch summary for pie charts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN internet_status = 'Connected' THEN 1 ELSE 0 END) AS internet_uptime,
            SUM(CASE WHEN internet_status = 'Not Connected' THEN 1 ELSE 0 END) AS internet_downtime,
            SUM(CASE WHEN plc_status = 'Connected' THEN 1 ELSE 0 END) AS plc_connected,
            SUM(CASE WHEN plc_status = 'Not Connected' THEN 1 ELSE 0 END) AS plc_disconnected
        FROM connection_status
    """)
    result = cursor.fetchone()
    conn.close()

    return jsonify({
        "internet": {"uptime": result[0], "downtime": result[1]},
        "plc": {"connected": result[2], "disconnected": result[3]}
    })


def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        flash(f"Database connection error: {e}", "danger")
        return None

@app.route('/')
def index():
    if 'username' not in session:  # User must be logged in
        return redirect(url_for('login'))

    # Pagination
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('login'))

    recipes = conn.execute(
        'SELECT * FROM Recipe LIMIT ? OFFSET ?', (per_page, offset)
    ).fetchall()

    # Fetch unique Pos_Values
    # pos_values = [row[0] for row in conn.execute("SELECT DISTINCT Pos_Values FROM Pos_Options").fetchall()]

    # Calculate total pages
    total_count = conn.execute('SELECT COUNT(*) FROM Recipe').fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page

    conn.close()

    return render_template(
        'dashboard.html',
    )

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']  # Allow public routes and static files
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        if not request.endpoint or request.endpoint.startswith('static'):  # Allow static files
            return
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/recipe')
def recipe_list():
    if 'username' not in session:  # Check if the user is logged in
        return redirect(url_for('login'))
    # Logic for listing recipes
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    recipes = conn.execute(
        'SELECT * FROM Recipe LIMIT ? OFFSET ?', (per_page, offset)
    ).fetchall()
    pos_values = [row[0] for row in conn.execute("SELECT materialType FROM Raw_Materials").fetchall()]
    total_count = conn.execute('SELECT COUNT(*) FROM Recipe').fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page
    conn.close()

    return render_template(
        'recipe.html',
        recipes=recipes,
        pos_values=pos_values,
        page=page,
        total_pages=total_pages
    )
@app.route('/api/recipe_log', methods=['GET'])
def get_recipe_log():
    conn = get_db_connection()
    recipe_log = conn.execute('SELECT * FROM Recipe_Log').fetchall()
    conn.close()

    # Convert to list of dictionaries
    recipe_log_list = [dict(row) for row in recipe_log]
    return jsonify(recipe_log_list)
def update_batch_status():
    while True:
        conn = get_db_connection()
        recipe_logs = conn.execute('SELECT * FROM Recipe_Log WHERE Batch_Completion_Status = "Pending" OR Batch_Completion_Status ="Partially Completed"').fetchall()
        
        client = Client(ENDPOINT_URL)
        client.session_timeout = 30000  # Adjust timeout as needed
        try:
            client.connect()
            for log in recipe_logs:
                batch_code = log['Batch_Code']
                quantity_field_path = 'ns=3;s="OpenRecipe"."actBatchQty"'  # Replace with PLC field path
                machine_state_field_path = 'ns=3;s="OpenRecipe"."machineState"'  # Replace with PLC field path

                current_quantity = client.get_node(quantity_field_path).get_value()
                machine_state = client.get_node(machine_state_field_path).get_value()

               # Calculate completion percentage
                completion_percentage = (current_quantity / log['Quantity']) * 100

                # Determine running status
                running_status = "Pending" if machine_state == 0 else "Running"

                # Determine completion status
                if completion_percentage < 60:
                    completion_status = "Pending"
                elif 60 <= completion_percentage < 100:
                    completion_status = "Partially Completed"
                elif completion_percentage >= 100:
                    completion_status = "Completed"
                    running_status = "Completed"  # Both statuses set to completed
                    node = client.get_node(machine_state_field_path)
                    variant = ua.DataValue(ua.Variant(0,ua.VariantType.Int32))
                    node.set_value(variant)
                conn.execute(
                    '''
                    UPDATE Recipe_Log
                    SET Batch_Running_Status = ?, Batch_Completion_Status = ?
                    WHERE Batch_Code = ?
                    ''',
                    (running_status, completion_status, batch_code)
                )
                conn.commit()
                 # Update machineState PLC field to 0
        except Exception as e:
            print(f"Error updating batch status: {e}")
        finally:
            client.disconnect()
            conn.close()

@app.route('/role', methods=['GET', 'POST'])
def role():
    if not session.get('username') == 'Admin':  # Replace 'Admin' with your admin identifier
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('a2z_database.db')
    cursor = conn.cursor()

    # Fetch unique usernames
    cursor.execute("SELECT DISTINCT username FROM users")
    users = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        # Retrieve selected username and roles from the form
        selected_user = request.form.get('username')
        roles = request.form.getlist('roles')

        # Save roles to the database
        roles_str = ','.join(roles)
        print(roles_str)
        cursor.execute(
            "UPDATE users SET roles = ? WHERE username = ?",
            (roles_str, selected_user)
        )
        conn.commit()
        flash(f'Roles updated for {selected_user}', 'success')

    conn.close()
    return render_template('roles.html', users=users)
@app.route('/get_roles', methods=['POST'])
def get_roles():
    username = request.json.get('username')  # Get the username from the AJAX request
    conn = sqlite3.connect('a2z_database.db')
    cursor = conn.cursor()

    # Fetch roles for the selected user
    cursor.execute("SELECT roles FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    roles = result[0].split(',') if result and result[0] else []
    return jsonify({'roles': roles}) 
@app.route('/event_log', methods=['GET'])
def event_log():
    if not session.get('username') == 'Admin':  # Replace 'Admin' with your admin identifier
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('a2z_database.db')
    cursor = conn.cursor()

    # Fetch user summary data for activity logs, ensuring correct logout handling
    cursor.execute("""
        SELECT 
            username,
            MAX(login_time) AS last_login_time,
            (SELECT logout_time FROM user_activity 
             WHERE username = ua.username 
             AND logout_time IS NOT NULL 
             ORDER BY logout_time DESC LIMIT 1) AS last_logout_time
        FROM user_activity ua
        GROUP BY username
    """)
    
    user_summary = []
    for row in cursor.fetchall():
        username, last_login_time, last_logout_time = row
        last_login_date = last_login_time.split()[0] if last_login_time else "N/A"
        last_login_time = last_login_time.split()[1] if last_login_time else "N/A"
        last_logout_date = last_logout_time.split()[0] if last_logout_time else "N/A"
        last_logout_time = last_logout_time.split()[1] if last_logout_time else "N/A"

        user_summary.append({
            'username': username,
            'last_login_date': last_login_date,
            'last_login_time': last_login_time,
            'last_logout_date': last_logout_date,
            'last_logout_time': last_logout_time if last_logout_time else "Currently Logged In"
        })

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    selected_username = request.args.get('username')
    selected_user_details = []
    total_pages = None

    if selected_username:
        cursor.execute("""
            SELECT 
                DATE(login_time, 'localtime') AS login_date,
                TIME(login_time, 'localtime') AS login_time,
                CASE 
                    WHEN logout_time IS NULL THEN NULL 
                    ELSE DATE(logout_time, 'localtime') 
                END AS logout_date,
                CASE 
                    WHEN logout_time IS NULL THEN NULL 
                    ELSE TIME(logout_time, 'localtime') 
                END AS logout_time
            FROM user_activity
            WHERE username = ?
            ORDER BY login_time DESC
            LIMIT ? OFFSET ?
        """, (selected_username, per_page, offset))
        
        selected_user_details = [
            {
                'login_date': row[0],
                'login_time': row[1],
                'logout_date': row[2] or "Currently Logged In",
                'logout_time': row[3] or "Currently Logged In",
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("SELECT COUNT(*) FROM user_activity WHERE username = ?", (selected_username,))
        total_logs = cursor.fetchone()[0]
        total_pages = (total_logs + per_page - 1) // per_page

    conn.close()

    return render_template(
        'event_log.html',
        user_summary=user_summary,
        selected_username=selected_username,
        selected_user_details=selected_user_details,
        page=page,
        total_pages=total_pages
    )

@app.route('/reset-password', methods=['POST'])
def reset_password():
    
    user_id = request.form['user_id']
    new_password = request.form['new_password']

    # Hash the new password (important for security)
    hashed_password = generate_password_hash(new_password)

    # Update the password in the database
    conn = sqlite3.connect('a2z_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

    flash('Password has been reset successfully!', 'success')
    return redirect(url_for('users'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):  # Checking hashed password
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            
            # Record login time
            cursor.execute("INSERT INTO user_activity (username, login_time) VALUES (?, datetime('now'))", (username,))
            conn.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
        conn.close()
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        try:
            # Connect to the database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Check if the username or email already exists
            cursor.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                flash('Username or email already taken!', 'danger')
                conn.close()
                return redirect(url_for('register'))

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
            conn.close()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))  # Redirect to the login page

        except sqlite3.Error as e:
            flash(f"Database error: {e}", 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')
@app.route('/users')
def users():
    if not session.get('username') == 'Admin':  # Replace 'Admin' with your admin identifier
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, is_admin FROM users")
    users = cursor.fetchall()
    print("This is users",users)
    conn.close()
    
    return render_template('users.html', users=users)
@app.route('/validate-admin-password', methods=['POST'])
def validate_admin_password():
    data = request.json
    admin_password = "admin123"  # Predefined admin password

    if data.get('password') == admin_password:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']

        # Update the logout time for the latest login session
        conn = sqlite3.connect('a2z_database.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_activity 
            SET logout_time = DATETIME('now', 'localtime') 
            WHERE username = ? 
            AND logout_time IS NULL
        """, (username,))
        conn.commit()
        conn.close()

        # Remove user from session
        session.pop('username', None)

        flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/tag-overview')
def tag_overview():
    if 'username' not in session:  # Check if the user is logged in
        flash("Login first to access the Tag Overview.")
        return redirect(url_for('login'))  # Redirect to login if not logged in
    # Get the page and limit parameters from the query string
    current_page = int(request.args.get('page', 1))  # Default to page 1 if not provided
    limit = int(request.args.get('limit', 10))  # Default limit is 10 if not provided
    
    # Database connection
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Calculate offset for pagination
    offset = (current_page - 1) * limit

    # Fetch paginated data
    cursor.execute('SELECT * FROM Tag_Table LIMIT ? OFFSET ?', (limit, offset))
    tags = cursor.fetchall()

    # Fetch the total number of rows for pagination calculation
    cursor.execute('SELECT COUNT(*) FROM Tag_Table')
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows + limit - 1) // limit  # Calculate total pages

    conn.close()

    # Render the template with tags and pagination details
    return render_template(
        'tag_overview.html',
        tags=tags,
        page=current_page,
        total_pages=total_pages,
        limit=limit,
        active_menu='tags',
        active_submenu='tag-overview'
    )
@app.route('/update-tag/<string:tagId>', methods=['PUT'])
def update_tag(tagId):
    try:
        # Parse JSON data from the request
        data = request.get_json()
        tagName = data.get('tagName')
        tagAddress = data.get('tagAddress')
        plcId = data.get('plcId')

        if not tagName or not tagAddress or not plcId:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Connect to the database and update the tag
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the tag exists
        cursor.execute("SELECT * FROM Tag_Table WHERE tagId = ?", (tagId,))
        tag = cursor.fetchone()
        if not tag:
            conn.close()
            return jsonify({"success": False, "error": "Tag not found"}), 404

        # Update the tag details in the database
        cursor.execute("""
            UPDATE Tag_Table
            SET tagName = ?, tagAddress = ?, plcId = ?
            WHERE tagId = ?
        """, (tagName, tagAddress, plcId, tagId))
        
        conn.commit()
        
        conn.close()
        fetch_and_update_live_value(tagAddress)
        # Respond with success message
        return jsonify({"success": True, "message": "Tag updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/delete-tag/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    try:
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Connect to the specific database
        conn = sqlite3.connect(DB_PATH)  # Make sure we're connecting to the right database
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Execute deletion query
        cursor.execute('DELETE FROM Tag_Table WHERE tagId = ?', (tag_id,))
        cursor.execute('DELETE FROM Live_Tags WHERE tagId=?',(tag_id,))
        conn.commit()

        # Check if the deletion actually occurred
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Tag not found"}), 404

        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Error while deleting tag: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
    finally:
        conn.close()



# @app.route('/live-tag')
# def live_tag():
#     # Get the current page from the query string (default to 1)
#     current_page = int(request.args.get('page', 1))

#     # Connect to the database
#     # 'suvi_database.db'
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row  # Rows are returned as dictionaries
#     cursor = conn.cursor()

#     # Pagination setup: 10 items per page
#     items_per_page = 10
#     offset = (current_page - 1) * items_per_page

#     # Fetch data for the current page
#     cursor.execute('SELECT * FROM Live_Tags LIMIT ? OFFSET ?', (items_per_page, offset))
#     live_tags = cursor.fetchall()

#     # Calculate total pages
#     cursor.execute('SELECT COUNT(*) FROM Live_Tags')
#     total_rows = cursor.fetchone()[0]
#     total_pages = (total_rows + items_per_page - 1) // items_per_page

#     conn.close()

#     return render_template(
#         'live_tag.html',
#         live_tags=live_tags,       # Pass the retrieved live tag data
#         page=current_page,         # Pass the current page number
#         total_pages=total_pages,   # Pass total number of pages
#         active_menu='tags',        # Keep the Tags dropdown open
#         active_submenu='live-tag'  # Highlight the Live Tags submenu
#     )
@app.route('/live-tag')
def live_tag():
    if 'username' not in session:  # Check if the user is logged in
        return redirect(url_for('login'))
    # Get the current page from the query string (default to 1)
    current_page = int(request.args.get('page', 1))

    # Connect to the database
    # 'suvi_database.db'
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Rows are returned as dictionaries
    cursor = conn.cursor()

    # Pagination setup: 10 items per page
    items_per_page = 10
    offset = (current_page - 1) * items_per_page

    # Fetch data for the current page
    cursor.execute('''
    SELECT Live_Tags.Id, Tag_Table.tagName, Live_Tags.value, Live_Tags.timestamp
    FROM Live_Tags
    JOIN Tag_Table ON Live_Tags.tagId = Tag_Table.tagId
    LIMIT ? OFFSET ?  ''', (items_per_page, offset))
    live_tags = cursor.fetchall()

    # Calculate total pages
    cursor.execute('SELECT COUNT(*) FROM Live_Tags')
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows + items_per_page - 1) // items_per_page

    conn.close()

    return render_template(
        'live_tag.html',
        live_tags=live_tags,       # Pass the retrieved live tag data
        page=current_page,         # Pass the current page number
        total_pages=total_pages,   # Pass total number of pages
        active_menu='tags',        # Keep the Tags dropdown open
        active_submenu='live-tag'  # Highlight the Live Tags submenu
    )
@app.route('/plc')
def plc():
    if not session.get('username') == 'Admin':  # Replace 'Admin' with your admin identifier
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    # Fetch the data (example for live_tags, adjust to your actual query)
    cursor.execute('SELECT * FROM Plc_Table')  # Adjust query as per your DB schema
    plc_tags = cursor.fetchall()
    cursor.execute('SELECT * FROM Machine_Table')  # Adjust query as per your DB schema
    machine_tags = cursor.fetchall()

    conn.close()

    # Render the template with the live_tags data
    return render_template('plc.html', plc_tags=plc_tags, machine_tags=machine_tags)
    


# @app.route('/raw-material', methods=['GET', 'POST'])
# def raw_material():
#     # Handle POST request for adding a new material
#     if request.method == 'POST':
#         try:
#             material_id = request.form['material_Id']
#             type_code = request.form['typeCode']
#             lot_no = request.form['lotNo']
#             material_type = request.form['materialType']
#             make = request.form.get('make', '')  # Optional
#             user = request.form.get('user', '')  # Optional
#             barcode = request.form.get('barcode', '')  # Optional

#             # Connect to the database
#             conn = sqlite3.connect('a2z_database.db')
#             cursor = conn.cursor()

#             # Insert into the database
#             cursor.execute("""
#                 INSERT INTO Raw_Materials (material_Id, typeCode, lotNo, make, user, materialType, barcode) 
#                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
#                 (material_id, type_code, lot_no, make, user, material_type, barcode))
#             conn.commit()
#             conn.close()

#             # Return a proper success response
#             return jsonify({"success": True, "message": "Material added successfully!"})

#         except Exception as e:
#             # Print the error for debugging
#             print(f"Error: {e}")
#             return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})

#     # Handle GET request to display the raw materials
#     current_page = int(request.args.get('page', 1))  # Default to page 1 if not provided
#     limit = int(request.args.get('limit', 10))  # Get limit from URL parameter (default 10)
#     conn = sqlite3.connect('a2z_database.db')
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     # Pagination setup
#     offset = (current_page - 1) * limit

#     # Fetch data for the current page based on the limit
#     cursor.execute('SELECT * FROM Raw_Materials LIMIT ? OFFSET ?', (limit, offset))
#     raw_materials = cursor.fetchall()

#     # Calculate total pages
#     cursor.execute('SELECT COUNT(*) FROM Raw_Materials')
#     total_rows = cursor.fetchone()[0]
#     total_pages = (total_rows + limit - 1) // limit  # Calculate total pages based on limit

#     conn.close()

#     # Render the template with the raw material data
#     return render_template(
#         'raw_material.html',
#         raw_materials=raw_materials,
#         page=current_page,
#         total_pages=total_pages,
#         limit=limit  # Pass the selected limit to the template
#     )




# Ensure database is set up



# material_id_counter = 1000
@app.route('/raw-material', methods=['GET', 'POST'])
def raw_material():
    if 'username' not in session:
        return redirect(url_for('login'))
    global material_id_counter
    if request.method == 'POST':
        try:
            # Extract required fields
            type_code = request.form['typeCode']
            lot_no = request.form['lotNo']
            material_type = request.form['materialType']

            # Auto-generate fields
            # material_id = material_id_counter
            # material_id_counter += 1  # Increment for the next entry
            make = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = "admin"
            barcode = f"-{type_code}-{lot_no}"  # Example auto-generated barcode

            # Connect to the database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Insert data into the table
            cursor.execute("""
                INSERT INTO Raw_Materials (typeCode, lotNo, materialType, make, user, barcode) 
                VALUES (?, ?, ?, ?, ?,?)""",
                (type_code, lot_no, material_type, make, user, barcode))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "Material added successfully!"})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})

    # Handle GET request for pagination
    try:
        current_page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (current_page - 1) * limit

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch data for the current page
        cursor.execute('SELECT * FROM Raw_Materials LIMIT ? OFFSET ?', (limit, offset))
        raw_materials = cursor.fetchall()

        # Calculate total pages
        cursor.execute('SELECT COUNT(*) FROM Raw_Materials')
        total_rows = cursor.fetchone()[0]
        total_pages = (total_rows + limit - 1) // limit

        conn.close()

        # Render the template with the paginated data
        return render_template(
            'raw_material.html',
            raw_materials=raw_materials,
            page=current_page,
            total_pages=total_pages,
            limit=limit
        )
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})


@app.route('/delete-raw-material/<int:raw_material_id>', methods=['DELETE'])
def delete_raw_material(raw_material_id):
    try:
        print(f"Attempting to delete raw material with ID: {raw_material_id}")

        # Check if user is logged in
        if 'username' not in session:
            print("Unauthorized access attempt.")
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the material exists
        cursor.execute('SELECT * FROM Raw_Materials WHERE material_Id = ?', (raw_material_id,))
        row = cursor.fetchone()

        if row is None:
            print(f"Material with ID {raw_material_id} not found.")
            return jsonify({"success": False, "error": "Raw material not found"}), 404

        # Delete the raw material from the database
        cursor.execute('DELETE FROM Raw_Materials WHERE material_Id = ?', (raw_material_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"Failed to delete material with ID {raw_material_id}.")
            return jsonify({"success": False, "error": "Failed to delete material"}), 500

        print(f"Successfully deleted material with ID {raw_material_id}.")
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error during deletion: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if conn:
            conn.close()

@app.route('/update-raw-material/<int:material_Id>', methods=['POST'])
def update_raw_material(material_Id):
    try:
        # Parse JSON data from the request
        data = request.json
        typeCode = data.get("typeCode")
        lotNo = data.get("lotNo")
        make = data.get("make")
        user = data.get("user")
        materialType = data.get("materialType")
        barcode = data.get("barcode")

        # Validate required fields
        missing_fields = [field for field in ["typeCode", "lotNo", "make", "user", "materialType", "barcode"] if not data.get(field)]
        if missing_fields:
            return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Connect to the database and update the record
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Check if the material_Id exists
            cursor.execute("SELECT COUNT(*) FROM Raw_Materials WHERE material_Id = ?", (material_Id,))
            if cursor.fetchone()[0] == 0:
                return jsonify({"success": False, "error": "Material with the given ID does not exist."}), 404

            # Update the record
            cursor.execute('''
                UPDATE Raw_Materials
                SET typeCode = ?, lotNo = ?, make = ?, user = ?, materialType = ?, barcode = ?
                WHERE material_Id = ?
            ''', (typeCode, lotNo, make, user, materialType, barcode, material_Id))
            conn.commit()

        # Check if the update was successful
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "No changes were made to the raw material."}), 400

        return jsonify({"success": True, "message": "Raw material updated successfully."})

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Raw_Materials.materialType" in str(e):
            return jsonify({"success": False, "error": "Material Type must be unique."}), 409
        return jsonify({"success": False, "error": f"Database integrity error: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/delete-recipe/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    try:
        # Debugging: Check if session contains username
        if 'username' not in session:
            print("Session does not contain 'username'. Current session:", session)
            return jsonify({"success": False, "error": "Unauthorized access"}), 401
        
        # Database connection and deletion logic
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Recipe WHERE Recipe_ID = ?', (recipe_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Recipe not found"}), 404

        return jsonify({"success": True, "message": "Recipe deleted successfully"})
    
    except Exception as e:
        print(f"Error while deleting recipe: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
    finally:
        conn.close()

@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('login'))

    recipe_details = conn.execute('SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    conn.close()
    try:
        pos_values = extract_pos_values(recipe_details)
        submenu_values = extract_submenu_vaues(sub_menu)
        barcode_value = "S3"  # Replace this with actual logic to fetch the barcode value
        # print (dict(recipe_details));
        print("Values from subtable: ",submenu_values)
        # update_plc_with_pos_values(pos_values)
        # update_plc_with_values(pos_values,submenu_values)
        flash(f"POS values written to PLC successfully for Recipe ID {recipe_id}.", "success")
    except Exception as e:
        flash(f"Error writing POS values: {e}", "danger")

    if not recipe_details:
        flash("Recipe not found!", "danger")
        return redirect(url_for('index'))
      
    
    return render_template('recipe_details.html', recipe_details=recipe_details, sub_menu=sub_menu,pos_values=pos_values[:-1] ,barcode_value=barcode_value)

def extract_pos_values(recipe_details):
    # Extract the required POS values from the recipe_details
    pos_values = [
        recipe_details['pos1'],  
        recipe_details['pos2'],
        recipe_details['pos3'],
        recipe_details['pos4'],
        recipe_details['pos5'],
        recipe_details['pos6'],
        recipe_details['pos7'],
        recipe_details['pos8'],
        recipe_details['pos9'],
        recipe_details['recipe_id'],
        # Add other POS fields as needed
        #         Add other POS fields as needed
    ]
   
    return pos_values

def extract_submenu_vaues(sub_menu):
    submenu_values = [
        sub_menu['motor_speed'],
        sub_menu['motor_stroke'],
        sub_menu['other_Speed_force'],
        sub_menu['alu_coil_width'],
    ]
    return submenu_values
@app.route('/compare-pos', methods=['POST'])
def compare_pos():
    data = request.json  # Receive data from frontend
    pos_value = data.get('posValue')
    barcode_value = data.get('barcodeValue')

    if pos_value is None or barcode_value is None:
        return jsonify({"error": "Invalid data"}), 400

    # Comparison logic
    match = pos_value == barcode_value

    return jsonify({"match": match})


@app.route('/update_recipe', methods=['POST'])
def update_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))

    recipe_id = request.form.get('recipe_id')
    recipe_name = request.form.get('recipe_name')
    filter_size = request.form.get('filter_size')
    filter_code = request.form.get('filter_code')
    art_no = request.form.get('art_no')
    pos_values = [request.form.get(f'pos{i}') for i in range(1, 10)]
    alu_coil_width = request.form.get('Alu_coil_width')
    motor_speed = request.form.get('Motor_speed')

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('recipe_list'))

    try:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE Recipe 
               SET Recipe_Name = ?, Filter_Size = ?, Filter_Code = ?, Art_No = ?
               WHERE Recipe_ID = ?''',
            (recipe_name, filter_size, filter_code, art_no, recipe_id)
        )
        cursor.execute(
            '''UPDATE Recipe_Details1 
               SET Pos1 = ?, Pos2 = ?, Pos3 = ?, Pos4 = ?, Pos5 = ?, 
                   Pos6 = ?, Pos7 = ?, Pos8 = ?, Pos9 = ?, Alu_coil_width = ?
               WHERE Recipe_ID = ?''',
            (*pos_values, alu_coil_width, recipe_id)
        )
        cursor.execute(
            '''UPDATE Sub_Menu 
               SET motor_speed = ?
               WHERE Recipe_ID = ?''',
            (motor_speed, recipe_id)
        )

        conn.commit()
        flash("Recipe updated successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('recipe_list'))

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))

    recipe_id = request.form.get('recipe_id')
    recipe_name = request.form.get('recipe_name')
    filter_size = request.form.get('filter_size')
    filter_code = request.form.get('filter_code')
    art_no = request.form.get('art_no')
    pos_values = [request.form.get(f'pos{i}') for i in range(1, 10)]
    alu_coil_width = request.form.get('Alu_coil_width')
    alu_roller_type = request.form.get('Alu_roller_type')
    spacer = request.form.get('Spacer')
    motor_speed = request.form.get('Motor_speed')
    motor_stroke = request.form.get('Motor_stroke')
    motor_force =  request.form.get('Motor_force')
    
    # print("Pos values from form: ",pos_values);
    # update_plc_with_pos_values(pos_values)
    if not (recipe_id and filter_size and filter_code and art_no and recipe_name):
        flash("All required fields must be filled!", "danger")
        return redirect(url_for('recipe_list'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('recipe_list'))

    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO Recipe (Recipe_ID,Recipe_Name,Filter_Size, Filter_Code, Art_No) 
            VALUES (?, ?, ?, ?,?)''',
            (recipe_id,recipe_name,filter_size, filter_code, art_no)
        )
        cursor.execute(
            '''INSERT INTO Recipe_Details1 
            (Id, Pos1, Pos2, Pos3, Pos4, Pos5, Pos6, Pos7, Pos8, Pos9, Alu_coil_width, Alu_roller_type, Spacer, Recipe_ID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (recipe_id, *pos_values, alu_coil_width, alu_roller_type, spacer, recipe_id)
        )
        cursor.execute(
            '''INSERT INTO Sub_Menu
            (Recipe_ID, motor_speed,motor_stroke,other_speed_force,alu_coil_width) 
            VALUES (?, ?, ?, ?, ?)''',
            (recipe_id,motor_speed,motor_stroke,motor_force,alu_coil_width)
        )

        conn.commit()
        flash("Recipe added successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('recipe_list'))
# Function to update PLC via OPC UA based on POS values


# def update_plc_with_pos_values(pos_values):
#     """
#     Update PLC with POS values and Recipe ID (assumed as the last element in pos_values).
#     """
#     client = Client(ENDPOINT_URL)
#     client.session_timeout = 30000  # Adjust timeout as needed
    
#     try:
#         client.connect()
#         # Ensure pos_values is a list with at least 10 elements (9 POS values + 1 Recipe ID)
#         # if not isinstance(pos_values, list) or len(pos_values) < 10:
#         #     raise ValueError("pos_values must be a list with at least 10 elements (including Recipe ID).")

#         # Extract Recipe ID (last element)
#         recipe_id = pos_values[-1]
#         pos_values = pos_values[:-1]  # Remove Recipe ID from the list, keeping only POS values

#         # Write POS values (1 to 9) to PLC nodes
#         for i in range(1, 10):
#             pos_value = pos_values[i - 1]  # Access by index (0-based for lists)
#             node_id = f'ns=3;s="OpenRecipe"."selectedRoll{i}"'
            

#             try:
#                 # Get the node object
#                 node = client.get_node(node_id)
              

#                 # Determine the value to set
#                 if pos_value:  # Check if the value is present (not None or empty)
#                     node.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                   
#                 else:
#                     node.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                   

#             except Exception as node_error:
#                 print(f"Error processing Node ID {node_id}: {node_error}")

#         # Write the Recipe ID to a specific OPC UA node
#         try:
#             recipe_node_id = 'ns=3;s="OpenRecipe"."recipeId"'  # Replace with actual node ID for Recipe ID
#             recipe_node = client.get_node(recipe_node_id)
           

#             recipe_node.set_value(ua.DataValue(ua.Variant(recipe_id, ua.VariantType.Int32)))
           

#         except Exception as recipe_error:
#             print(f"Error writing Recipe ID to Node ID {recipe_node_id}: {recipe_error}")

    
       
#         client.disconnect()
      
#     except Exception as e:
#         print(f"Error updating PLC: {e}")
def update_plc_with_values(pos_values, submenu_values):
    """
    Update PLC with POS values, Recipe ID (assumed as the last element in pos_values), 
    and submenu values.
    """
    from opcua import Client, ua

    client = Client(ENDPOINT_URL)
    client.session_timeout = 30000  # Adjust timeout as needed

    try:
        client.connect()

        # Ensure pos_values is a list with at least 10 elements (9 POS values + 1 Recipe ID)
        if not isinstance(pos_values, list) or len(pos_values) < 10:
            raise ValueError("pos_values must be a list with at least 10 elements (including Recipe ID).")

        # Extract Recipe ID (last element)
        recipe_id = pos_values[-1]
        pos_values = pos_values[:-1]  # Remove Recipe ID from the list, keeping only POS values

        # Write POS values (1 to 9) to PLC nodes
        for i in range(1, 10):
            pos_value = pos_values[i - 1]  # Access by index (0-based for lists)
            node_id = f'ns=3;s="OpenRecipe"."selectedRoll{i}"'

            try:
                # Get the node object
                node = client.get_node(node_id)
                # Determine the value to set
                node.set_value(ua.DataValue(ua.Variant(bool(pos_value), ua.VariantType.Boolean)))
            except Exception as node_error:
                print(f"Error processing Node ID {node_id}: {node_error}")

        # Write the Recipe ID to a specific OPC UA node
        try:
            recipe_node_id = 'ns=3;s="OpenRecipe"."recipeId"'  # Replace with actual node ID for Recipe ID
            recipe_node = client.get_node(recipe_node_id)
            recipe_node.set_value(ua.DataValue(ua.Variant(recipe_id, ua.VariantType.Int32)))
        except Exception as recipe_error:
            print(f"Error writing Recipe ID to Node ID {recipe_node_id}: {recipe_error}")
        submenu_fields = ["servoMotorForce", "servoMotorSpeed", "servoMotorStroke", "coilWidth"]
        # Write submenu values to specific nodes
        try:
         submenu_values = [float(value) for value in submenu_values] 
        except ValueError as conversion_error:
         raise ValueError(f"Error converting submenu values to float: {conversion_error}")

        for field_name, submenu_value in zip(submenu_fields, submenu_values):
            submenu_node_id = f'ns=3;s="OpenRecipe"."{field_name}"'  # Replace with actual node ID pattern
            try:
                # Get the node object
                node = client.get_node(submenu_node_id)
                node.set_value(ua.DataValue(ua.Variant(submenu_value, ua.VariantType.Float)))
            except Exception as submenu_error:
                print(f"Error processing Submenu Node ID {submenu_node_id}: {submenu_error}")

        print("POS values, Recipe ID, and Submenu values written successfully to PLC.")
    except Exception as e:
        print(f"Error updating PLC: {e}")
    finally:
        client.disconnect()

@app.route('/start_recipe/<int:recipe_id>', methods=['POST'])
def start_recipe(recipe_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    recipe_details = conn.execute('SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    pos_values = extract_pos_values(recipe_details)
    submenu_values = extract_submenu_vaues(sub_menu)
    update_plc_with_values(pos_values, submenu_values)
    if not recipe_details or not sub_menu:
        flash("Recipe details not found!", "danger")
        return redirect(url_for('recipe_details', recipe_id=recipe_id))

    # Get Quantity from Request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    quantity = data.get('quantity')
    if not quantity:
        return jsonify({"error": "Quantity is required"}), 400

    # Generate Batch Code and Timestamp
    batch_code = f"BATCH-{recipe_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert into Recipe_Log Table
    try:
        conn.execute(
            '''
            INSERT INTO Recipe_Log 
            (Batch_Code, Timestamp, Recipe_ID, motor_speed, motor_stroke, 
            other_speed_force, alu_coil_width, Quantity, Batch_Running_Status, Batch_Completion_Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                batch_code,
                timestamp,
                recipe_id,
                sub_menu['motor_speed'],
                sub_menu['motor_stroke'],
                sub_menu['other_speed_force'],
                sub_menu['alu_coil_width'],
                quantity,
                'Running',
                'Pending'
            )
        )
        conn.commit()
        flash(f"Recipe batch started successfully with Batch Code: {batch_code}", "success")
    except Exception as e:
        flash(f"Error logging recipe batch: {e}", "danger")
    finally:
        conn.close()

    return jsonify({"message": "Recipe batch started successfully"})

# shreyash's new changes 
@app.route('/addTag', methods=['POST'])
def add_tag():
    data = request.json
    tag_id = data.get("tagId")
    tag_name = data.get("tagName")
    tag_address = data.get("tagAddress")
    plc_id = data.get("plcId")

    if not tag_id or not tag_name or not tag_address or not plc_id:
        return jsonify({"success": False, "error": "Missing fields in the request."})

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Tag_Table (tagId, tagName, tagAddress, plcId)
                VALUES (?, ?, ?, ?)
            ''', (tag_id, tag_name, tag_address, plc_id))
            conn.commit()
            # After adding the tag to the Tag_Table, fetch and update the live value for that tag
        # update_live_tags_for_new_entry(tag_address)
        fetch_and_update_live_value(tag_address)
        return jsonify({"success": True, "message": "Tag added successfully."})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "TagId already exists."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
def fetch_and_update_live_value(tag_address):
    """Fetch live value for a tag and update the Live_Tags table."""
    client = Client(ENDPOINT_URL)
    client.session_timeout = 30000  # Adjust timeout as needed
    try:
        client.connect()

        # Fetch the value from the OPC UA server for the given tagAddress
        node = client.get_node(tag_address)
        value = node.get_value()
  # Convert the value into a JSON string if it's not a single number
        if isinstance(value, (list, dict)):  # If the value is an array or object
            value = json.dumps(value)  # Convert to JSON string
        else:
            value = str(value)  # Convert single number or other value to string
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Fetch the tagId from the Tag_Table for this tagAddress
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT Tagid FROM Tag_Table WHERE tagAddress = ?''', (tag_address,))
            tag_id = cursor.fetchone()

            if tag_id:
                tag_id = tag_id[0]  # Extract tag_id from the tuple

                # Check if this tagId already has an entry in the Live_Tags table
                cursor.execute('''SELECT id FROM Live_Tags WHERE tagId = ? ORDER BY timestamp DESC LIMIT 1''', (tag_id,))
                existing_entry = cursor.fetchone()

                if existing_entry:
                    # Update the value in Live_Tags table if an entry exists
                    cursor.execute('''UPDATE Live_Tags SET value = ?, timestamp = ? WHERE id = ?''',
                                   (value, timestamp, existing_entry[0]))
                else:
                    # Insert the new value into Live_Tags table
                    cursor.execute('''INSERT INTO Live_Tags (value, tagId, timestamp) VALUES (?, ?, ?)''',
                                   (value, tag_id, timestamp))

                conn.commit()

        # Emit live data to the frontend via SocketIO
        # socketio.emit('liveData', {"success": True, "tagAddress": tag_address, "value": value})

    except Exception as e:
        # socketio.emit('liveData', {"success": False, "error": str(e)})
        print(f"Error fetching and updating live value: {e}")

    finally:
        client.disconnect()

def fetch_live_tag_data():
    """
    Fetch live tags and their corresponding tag addresses from the database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT lt.id, lt.tagId, tt.tagAddress 
            FROM Live_Tags lt 
            LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
        ''')
        return cursor.fetchall()

def read_opcua_values(tag_data):
    """
    Connect to OPC UA server and read values for the given tag addresses.
    """
    client = Client(ENDPOINT_URL)
    client.session_timeout = 30000  # Adjust timeout as needed
    updates = []

    try:
        # print("Connecting to OPC UA server...")
        client.connect()
        # print("Connected to OPC UA server!")

        # Start the overall timing for the entire operation
        overall_start_time = time.time()

        for live_tag_id, tag_id, tag_address in tag_data:
            if not tag_address:
                print(f"No tagAddress found for tagId {tag_id}. Skipping update.")
                continue

            # Start timing for individual tag fetching
            tag_start_time = time.time()

            try:
                # Fetch the live value from OPC UA server
                node = client.get_node(tag_address)
                value = node.get_value()
                
                # Calculate individual tag fetching time
                tag_end_time = time.time()
                tag_elapsed_time = (tag_end_time - tag_start_time) * 1000  # in milliseconds
                # print(f"Fetched value {value} for tagId {tag_id}. Time taken: {tag_elapsed_time:.2f} ms.")

                # Store the result
                updates.append((value, live_tag_id))
            except Exception as e:
                print(f"Error fetching live value for tagId {tag_id}: {e}")

        # Calculate overall session duration
        overall_end_time = time.time()
        overall_elapsed_time = (overall_end_time - overall_start_time) * 1000  # in milliseconds
        # print(f"Disconnected from OPC UA server. Overall session duration: {overall_elapsed_time:.2f} ms.")

    finally:
        client.disconnect()

    return updates



def update_database(updates):
    """
    Update the Live_Tags table with the new live values.
    Convert lists or dictionaries in 'value' to JSON strings.
    """
    updates_serialized = []  # To store serialized updates for Live_Tags
     # Generate a single consistent timestamp
    consistent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    for value, record_id in updates:
        if isinstance(value, (list, dict)):
            value = json.dumps(value)  # Convert list/dict to JSON string
        else:
            value = str(value)  # Convert other types to string
        
        # Prepare for Live_Tags update
        updates_serialized.append((value,consistent_timestamp, record_id))

    # Database operations
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # 1. Update the Live_Tags table
        cursor.executemany('''
            UPDATE Live_Tags
            SET value = ?, timestamp = ?
            WHERE id = ?
        ''', updates_serialized)

        conn.commit()
     
# API_URL = "https://api.ngsmart.in:5000/suvi/api/v1/machine-data"  # Change this to your Flask API URL
# API_URL = "https://api.ngsmart.in:5000/suvi/api/v1/machine-data"
API_URL =   "http://localhost:4000/suvi/api/v1/machine-data"
BATCH_SIZE = 10

def is_json(value):
    """
    Check if a value is a valid JSON.
    """
    try:
        json.loads(value)
        return True
    except ValueError:
        return False
def process_value(tag_name, value):
    """
    Process the value field:
    - If it's an array, convert each element into a separate field like field1, field2, etc.
    - If it's not an array, return as-is.
    """
    if isinstance(value, list):
        return {f"{tag_name}{i+1}": v for i, v in enumerate(value)}
    else:
        return {tag_name: value}
def timestamp_to_epoch(timestamp):
    """
    Convert timestamp from 'YYYY-MM-DD HH:MM:SS' (string) to epoch seconds,
    or use the timestamp directly if it's already in epoch form (integer).
    """
    try:
        # If timestamp is an integer (epoch time)
        if isinstance(timestamp, int):
            return timestamp
        
        # If timestamp is a string in 'YYYY-MM-DD HH:MM:SS' format
        elif isinstance(timestamp, str):
            datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            return int(datetime_obj.timestamp())
        
        # Handle unexpected timestamp types
        else:
            print(f"Unexpected timestamp type: {type(timestamp)}")
            return None
    except ValueError as e:
        print(f"Error converting timestamp: {e}")
        return None
def get_current_batch_count():
    """
    Fetch the current total number of batches from the database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT number_of_batches_created FROM BatchTracker WHERE id = 1')
        result = cursor.fetchone()
        return result[0] if result else 0
def update_batch_count(new_batches):
    """
    Add the count of new batches to the existing total and update the database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Get the current batch count
        current_count = get_current_batch_count()
        print(f"Current batch count: {current_count}")

        # Calculate the new total
        updated_count = current_count + new_batches

        # Update the table with the new count
        cursor.execute('UPDATE BatchTracker SET number_of_batches_created = ? WHERE id = 1', (updated_count,))
        conn.commit()

        print(f"Updated batch count: {updated_count}")
        return updated_count
# def clean_live_log_last_batch(conn, record_ids):
#     """
#     Clean up successfully uploaded records from SQLite.
#     """
#     try:
#         cursor = conn.cursor()
#         cursor.execute(f'''
#             DELETE FROM Live_Log
#             WHERE id IN ({','.join(['?'] * len(record_ids))})
#         ''', record_ids)
#         conn.commit()
#         print("Successfully cleaned up uploaded records from SQLite.")
#     except Exception as e:
#         print(f"Error: {e}")
def clean_live_log_last_batch(conn, record_ids, chunk_size=500):
    """
    Clean up successfully uploaded records from SQLite in chunks to avoid 'too many SQL variables' error.
    """
    try:
        cursor = conn.cursor()
        # Process deletions in chunks
        for i in range(0, len(record_ids), chunk_size):
            chunk = record_ids[i:i + chunk_size]
            placeholders = ','.join(['?'] * len(chunk))
            cursor.execute(f'''
                DELETE FROM Live_Log
                WHERE id IN ({placeholders})
            ''', chunk)
            conn.commit()
        print("Successfully cleaned up uploaded records from SQLite.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
def fetch_plc_info():
    """Fetch plcId and serialKey from Plc_Table."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Fetch plcId and serialKey for the first PLC (you can modify this if needed)
            cursor.execute("SELECT plcId, serial_Key FROM Plc_Table LIMIT 1")
            plc_info = cursor.fetchone()

            if plc_info:
                plc_id, serial_key = plc_info
                return plc_id, serial_key
            else:
                return None, None  # Return None if no data found

    except Exception as e:
        print(f"Error fetching PLC info: {e}")
        return None, None
def upload_live_log_to_mongodb():
    """
    Fetch records from SQLite, format them, send them to Flask API, and clean up SQLite.
    """
    try:
        # Fetch plcId and serialKey from Plc_Table
        plc_id, serial_key = fetch_plc_info()
        if plc_id is None or serial_key is None:
            print("Error: plcId or serialKey not found in Plc_Table.")
            return

        # Connect to SQLite
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Fetch all records grouped by timestamp
            cursor.execute('''
                SELECT id, tagName, value, timestamp
                FROM Live_Log
                ORDER BY timestamp ASC, id ASC
            ''')
            records = cursor.fetchall()

            if not records:
                print("No records to upload.")
                return

            # Group records by timestamp
            grouped_data = {}
            record_ids = []

            for record in records:
                record_id, tag_name, value, timestamp = record

                # Convert timestamp to epoch format
                epoch_timestamp = timestamp_to_epoch(timestamp)
                if epoch_timestamp is None:
                    continue  # Skip if timestamp conversion failed

                # Parse value if it's JSON
                parsed_value = json.loads(value) if is_json(value) else value

                # Process value to split arrays into separate fields
                processed_data = process_value(tag_name, parsed_value)

                if epoch_timestamp not in grouped_data:
                    grouped_data[epoch_timestamp] = []
                grouped_data[epoch_timestamp].append(processed_data)

                # Collect record IDs for cleanup
                record_ids.append(record_id)

            # Prepare the batch format
            batches = []
            for epoch_timestamp, tags in grouped_data.items():
                # Combine all tags for the same timestamp into one dictionary
                combined_tags = {}
                for tag in tags:
                    combined_tags.update(tag)

                batch = {
                    "plcId": plc_id,
                    "serialNo": serial_key,
                    "values": [{"dbId": 3,"dbNo":1001,"dbName":"dbCloud", "data": [{"temp":1,"timeStamp": epoch_timestamp * 1000, **combined_tags}]}]
                }
                batches.append(batch)
            successful_batches = 0

            # Send data in batches of 10
            for i in range(0, len(batches), BATCH_SIZE):
                batch_to_send = batches[i:i + BATCH_SIZE]

                response = requests.post(API_URL, json=batch_to_send)

                if response.status_code in [200, 201]:
                    print(f"Batch {i // BATCH_SIZE + 1} uploaded successfully.")
                    successful_batches+=1
                    # Clean up uploaded records
                    clean_live_log_last_batch(conn, record_ids,chunk_size=500)
                else:
                    print(f"Failed to upload batch {i // BATCH_SIZE + 1}. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
        update_batch_count(successful_batches)
        print("Process completed.")
        print(f"Response from final API (Batch {i // BATCH_SIZE + 1}): {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def schedule_live_log_upload_background(interval=100000):
    """
    Run the upload function in a background thread every `interval` seconds.
    """
    def background_task():
        while True:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''SELECT COUNT(*) FROM Live_Log''')
                    count = cursor.fetchone()[0]

                    if count > 1000:
                        upload_live_log_to_mongodb()
                    else:
                        print("Less than 1000 records in Live_Log. Skipping upload...")
            except Exception as e:
                print(f"Error in background task: {e}")
            time.sleep(interval/1000)  # Wait before the next check

    # Start the background task in a separate thread
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()

# Call this function to start the background thread
# schedule_live_log_upload_background(interval=15000)

def update_all_live_tags():
    """
    Fetch all entries from Live_Tags, resolve tagAddress from Tag_Table, and update live values.
    """
    try:
        # Step 1: Fetch data from the database
        tag_data = fetch_live_tag_data()

        # Step 2: Read values from OPC UA
        updates = read_opcua_values(tag_data)

        # Step 3: Update the database
        update_database(updates)

    except Exception as e:
        print(f"Error: {e}")
        # Global variable to store the user-defined interval (in seconds)
def update_all_live_tags_to_log():
    """
    Insert values into Live_Log table based on user-defined interval.
    """
    try:
        # Fetch the live tag data again to ensure we get the latest values
        tag_data = fetch_live_tag_data()

        # Read values from OPC UA
        updates = read_opcua_values(tag_data)

         # Generate a single consistent timestamp
        consistent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare and insert into the Live_Log table
        live_log_entries = []
        for value, record_id in updates:
            if isinstance(value, (list, dict)):
                value = json.dumps(value)  # Convert list/dict to JSON string
            else:
                value = str(value)  # Convert other types to string
            live_log_entries.append((record_id, value))

        # Insert into Live_Log table
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for record_id, value in live_log_entries:
                cursor.execute('''
                    INSERT INTO Live_Log (tagId, tagName, value, timestamp)
                    SELECT lt.tagId, tt.tagName, ?, ?
                    FROM Live_Tags lt
                    LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
                    WHERE lt.id = ?
                ''', (value, consistent_timestamp, record_id))

            conn.commit()

    except Exception as e:
        print(f"Error: {e}")
@app.route('/writeValue', methods=['POST'])
def write_value():
    data = request.json
    print("Received Data:", data)  # This will print the data to the console
    node_id = data.get("nodeId")
    value = data.get("value")

    if not node_id or value is None:
        return jsonify({"success": False, "error": "Missing nodeId or value in the request."})

    try:
        # Connect to the OPC UA server
        client = Client(ENDPOINT_URL)
        client.session_timeout = 30000  # Adjust timeout as needed
        client.connect()

        # Get the node object
        node = client.get_node(node_id)
        print("Received node:", node)  # This will print the data to the console

        # Fetch the DataType of the node
        data_type = node.get_data_type_as_variant_type()
        # print("Received datatype:", data_type)  # This will print the data to the console
        if not data_type:
            raise Exception(f"Could not fetch DataType for NodeId: {node_id}")

        # print(f"Fetched DataType: {data_type}")

        # Wrap the value in a ua.Variant object with the correct DataType
         # Wrap the value in a ua.Variant object with the correct DataType
        variant = ua.DataValue(ua.Variant(value, data_type))

        # Perform the write operation
        node.set_value(variant)
       
        # Disconnect from the client
        client.disconnect()

        return jsonify({"success": True, "message": f"Value written successfully to NodeId: {node_id}"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# @app.route('/readValues', methods=['GET'])
# def read_values():
#     try:
#         # Connect to SQL Database
#         conn = sqlite3.connect(DB_PATH)  # Update with your DB 
#         cursor = conn.cursor()


#         # Fetch node IDs from the SQL table
#         cursor.execute("SELECT DISTINCT tagAddress FROM Tag_Table")  # Update table/column names
#         node_ids = [row[0] for row in cursor.fetchall()]
#         # print("Node IDs: {}".format(node_ids));
#         if not node_ids:
#             return jsonify({"success": False, "error": "No node IDs found in the database"})

#         # Connect to the PLC
#         client = Client(ENDPOINT_URL)
#         client.session_timeout = 30000  # Adjust timeout as needed
#         client.connect()

#         results = []
#         for node_id in node_ids:
#             try:
#                 node = client.get_node(node_id)
#                 value = node.get_value()
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
#                 results.append({"nodeId": node_id, "value": value, "timestamp": timestamp})
#             except Exception as e:
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include timestamp for errors
#                 results.append({"nodeId": node_id, "error": str(e), "timestamp": timestamp})

#         client.disconnect()
#         conn.close()
#         return jsonify({"success": True, "results": results})

#     except sqlite3.Error as db_error:
#         return jsonify({"success": False, "error": f"Database error: {str(db_error)}"})

#     except Exception as e:
#         return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})
@app.route('/readValues', methods=['GET'])
def read_values():
    try:
        # Connect to SQL Database
        conn = sqlite3.connect(DB_PATH)  # Update with your DB 
        cursor = conn.cursor()


        # Fetch node IDs and their corresponding tag names
        cursor.execute("SELECT DISTINCT tagAddress, tagName FROM Tag_Table")  # Include tagName
        tag_data = cursor.fetchall()

        if not tag_data:
            return jsonify({"success": False, "error": "No tag data found in the database"})

        # Connect to the PLC
        client = Client(ENDPOINT_URL)
        client.session_timeout = 30000  # Adjust timeout as needed
        client.connect()

        results = []
        for tag_address, tag_name in tag_data:
            try:
                node = client.get_node(tag_address)
                value = node.get_value()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
                results.append({"nodeId": tag_address, "tagName": tag_name, "value": value, "timestamp": timestamp})
            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                results.append({"nodeId": tag_address, "tagName": tag_name, "error": str(e), "timestamp": timestamp})

        client.disconnect()
        conn.close()
        return jsonify({"success": True, "results": results})

    except sqlite3.Error as db_error:
        return jsonify({"success": False, "error": f"Database error: {str(db_error)}"})

    except Exception as e:
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})

def read_live_values(node_ids):
    """Connect to OPC UA server and emit live data to the frontend."""
    client = Client(ENDPOINT_URL)
    client.session_timeout = 30000  # Adjust timeout as needed
    try:
        # print("Attempting to connect to OPC UA server...")
        client.connect()
        # print("Connected to OPC UA server!")

        while True:
            results = []
            print("Fetching data for node IDs:", node_ids)  # Debug node IDs
            for node_id in node_ids:
                try:
                    # print(f"Reading value for node ID: {node_id}")  # Log node ID
                    node = client.get_node(node_id)
                    value = node.get_value()
                    # print(f"Value for node {node_id}: {value}")  # Log fetched value
                    results.append({"nodeId": node_id, "value": value})
                except Exception as e:
                    print(f"Error reading node {node_id}: {e}")  # Log errors
                    results.append({"nodeId": node_id, "error": str(e)})

            print("Emitting data to frontend:", results)  # Debug emitted data
            # socketio.emit('liveData', {"success": True, "results": results})
            time.sleep(1)  # Fetch data every 2 seconds
    except Exception as e:
        print(f"Error in OPC UA connection: {e}")  # Log connection errors
        # socketio.emit('liveData', {"success": False, "error": str(e)})
    finally:
        client.disconnect()
        print("Disconnected from OPC UA server!")  # Debug disconnection
# @app.route('/getLiveValues', methods=['GET'])
# def get_live_values():
#     try:
#         with sqlite3.connect(DB_PATH) as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 SELECT Id,value, timestamp,tagId
#                 FROM Live_Tags 
#             ''')
#             live_values = cursor.fetchall()

#         results = [{"tagId": value[3], "value": value[1], "timestamp": value[2]} for value in live_values]
#         return jsonify({"success": True, "data": results})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})
@app.route('/getLiveValues', methods=['GET'])
def get_live_values():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Live_Tags.Id, Live_Tags.value, Live_Tags.timestamp, Tag_Table.tagName
                FROM Live_Tags
                JOIN Tag_Table ON Live_Tags.tagId = Tag_Table.tagId
            ''')

            live_values = cursor.fetchall()

        results = [{"tagName": value[3], "value": value[1], "timestamp": value[2]} for value in live_values]
        return jsonify({"success": True, "data": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/startLiveRead', methods=['POST'])
def start_live_read():
    """API endpoint to initiate live data reading."""
    data = request.json
    print("Received request to start live reading:", data)  # Log request data

    node_ids = data.get("nodeIds", [])
    if not node_ids:
        print("No node IDs provided in request!")  # Log missing node IDs
        return jsonify({"success": False, "message": "No node IDs provided"}), 400

    print("Starting live reading for node IDs:", node_ids)  # Log starting point
    # Start the live reading thread
    thread = threading.Thread(target=read_live_values, args=(node_ids,))
    thread.daemon = True  # Ensures thread stops when the main app stops
    thread.start()

    return jsonify({"success": True, "message": "Live data reading started"})

@app.route('/get_recipe', methods=['GET'])
def get_recipe():
    conn = get_db_connection()
    recipe_id = request.args.get('recipe_id')

    print("Recipe ID received:", recipe_id)  # Debug log

    if not recipe_id:
        return jsonify({"success": False, "message": "Recipe ID is required"})

    try:
        # Fetch data from the Recipe table
        recipe_main = conn.execute("SELECT * FROM Recipe WHERE recipe_id = ?", (recipe_id,)).fetchone()
        if not recipe_main:
            return jsonify({"success": False, "message": "Recipe not found"})

        # Convert `recipe_main` to a dictionary
        recipe_main = dict(recipe_main)

        # Fetch data from Recipe_Details1 (which should contain Spacer and Alu_roller_type)
        recipe_pos = conn.execute("SELECT * FROM Recipe_Details1 WHERE recipe_id = ?", (recipe_id,)).fetchall()
        recipe_pos = [dict(pos) for pos in recipe_pos]  # Convert each row to a dictionary
        print("Fetched recipe_pos:", recipe_pos)  # Debugging the fetched data

        # Fetch data from Sub_Menu (which contains motor-related details)
        recipe_motor = conn.execute("SELECT * FROM Sub_Menu WHERE recipe_id = ?", (recipe_id,)).fetchone()
        recipe_motor = dict(recipe_motor) if recipe_motor else {}

        # Build the response data
        data = {
            "recipe_id": recipe_main.get("Recipe_ID"),
            "recipe_name": recipe_main.get("Recipe_Name"),
            "filter_size": recipe_main.get("Filter_Size"),
            "filter_code": recipe_main.get("Filter_Code"),
            "art_no": recipe_main.get("Art_No"),
            "Alu_coil_width": recipe_motor.get("alu_coil_width", ""),
            "Alu_roller_type": "",  # Default, will be overwritten with values from `recipe_pos`
            "Spacer": "",  # Default, will be overwritten with values from `recipe_pos`
            "Motor_speed": recipe_motor.get("motor_speed", ""),
            "Motor_stroke": recipe_motor.get("motor_stroke", ""),
            "Motor_force": recipe_motor.get("other_speed_force", ""),
        }
        

        # Add positions to the data and map the fields like Alu_roller_type and Spacer from `recipe_pos`
        for i, Pos in enumerate(recipe_pos, start=1):
    # For each position, check if it's in the Pos dictionary and assign it
        #  pos_key = f"Pos{i}"
        #  if pos_key in Pos:
        #    data[pos_key] = Pos[pos_key] if Pos[pos_key] is not None else ""
    
    # Overwrite Alu_roller_type and Spacer from `recipe_pos` table if present
         if "Alu_roller_type" in Pos:
           data["Alu_roller_type"] = Pos["Alu_roller_type"]
        if "Pos1" in Pos:
           data["Pos1"] = Pos["Pos1"]
        if "Pos2" in Pos:
           data["Pos2"] = Pos["Pos2"]
        if "Pos3" in Pos:
           data["Pos3"] = Pos["Pos3"]
        if "Pos4" in Pos:
           data["Pos4"] = Pos["Pos4"]
        if "Pos5" in Pos:
           data["Pos5"] = Pos["Pos5"]
        if "Pos6" in Pos:
           data["Pos6"] = Pos["Pos6"]
        if "Pos7" in Pos:
            data["Pos7"] = Pos["Pos7"]
        if "Pos8" in Pos:
            data["Pos8"] = Pos["Pos8"]
        if "Pos9" in Pos:
            data["Pos9"] = Pos["Pos9"]
        if "Spacer" in Pos:
          data["Spacer"] = Pos["Spacer"]


        print("Final response data:", data)  # Debug log
        return jsonify({"success": True, **data})

    except Exception as e:
        print("Error:", str(e))  # Log the error for debugging
        return jsonify({"success": False, "message": str(e)})
# NODE_IDS = {
#     "Motor_speed": "ns=2;i=2",  # Replace with actual Node ID for Motor_speed
#     "Motor_stroke": "ns=2;i=3", # Replace with actual Node ID for Motor_stroke
#     "Motor_force": "ns=2;i=4"   # Replace with actual Node ID for Motor_force
# }

@app.route('/get_last_plc_values', methods=['GET'])
def get_last_plc_values():
    client = Client(ENDPOINT_URL)  # OPC UA client
    try:
        # Connect to OPC UA server
        client.connect()
        # Fetch values for the given Node IDs
        coil_Width = client.get_node('ns=3;s="OpenRecipe"."coilWidth"').get_value()
        motor_force = client.get_node('ns=3;s="OpenRecipe"."servoMotorForce"').get_value()
        motor_stroke = client.get_node('ns=3;s="OpenRecipe"."servoMotorStroke"').get_value()
        motor_speed = client.get_node('ns=3;s="OpenRecipe"."servoMotorSpeed"').get_value()

        # Build response
        last_plc_values = {
            "Motor_speed": str(motor_speed),
            "Motor_stroke": str(motor_stroke),
            "Motor_force": str(motor_force),
            "coil_Width":  str(coil_Width)
        }
        return jsonify(last_plc_values)

    except Exception as e:
        print("Error fetching PLC values:", e)
        return jsonify({"error": "Failed to fetch PLC values"}), 500
    finally:
        client.disconnect()
        print("Disconnected from OPC UA Server")
# if __name__ == '__main__':
#     app.run(debug=False)
def run_periodic_update1():
    while True:
        
        update_all_live_tags()
        
        time.sleep(1)  # Update every 1 seconds
# Initialize the default update interval
update_interval = 20
interval_lock = threading.Lock()

@app.route('/api/update_interval_time', methods=['POST'])
def update_interval_time():
    global update_interval

    try:
        # Get the intervalTime value from the request body
        data = request.json
        interval_time = data.get('intervalTime')

        if not interval_time or interval_time <= 0:
            return jsonify({"success": False, "error": "Invalid interval time provided."})

        # Update the intervalTime value in the SQLite database
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Plc_Table SET intervalTime = ? WHERE plcId = 1", (interval_time,))
            conn.commit()

        # Safely update the global update_interval value
        with interval_lock:
            update_interval = interval_time

        return jsonify({"success": True, "message": "Interval time updated successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def run_periodic_update3():
    global update_interval

    while True:
        # Perform the periodic update task
        update_all_live_tags_to_log()  # Insert data into Live_Log after the interval

        # Safely access the update_interval value
        with interval_lock:
            # print("Interval time:",update_interval)
            sleep_time = update_interval

        time.sleep(sleep_time)  # Sleep for the specified interval
 # Sleep for the specified interval 
def run_periodic_update2():
    while True:
        
        update_batch_status()
        
        time.sleep(1)  # Update every 1 seconds
        
if __name__ == '__main__':
    print("Starting Flask app...")
    schedule_live_log_upload_background(interval=10000)
    threading.Thread(target=run_periodic_update1, daemon=True).start()
    threading.Thread(target=run_periodic_update2, daemon=True).start()
    threading.Thread(target=run_periodic_update3, daemon=True).start()
    threading.Thread(target=log_status, daemon=True).start()
    # socketio.run(app, host='0.0.0.0', port=5000)
    app.run(debug=True)

