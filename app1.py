# from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# import sqlite3
# import json
# import logging
# import datetime
# from datetime import datetime
# from datetime import timedelta
# from flask_socketio import SocketIO, emit
# from opcua import Client, ua
# from flask import send_from_directory
# import threading
# from threading import Thread
# import time
# import requests
# import json
# import sqlite3
# import platform
# import datetime
# import subprocess
# import wmi  # For Windows systems (install with `pip install WMI`)
# from bson import json_util
# from pymongo import MongoClient
# from flask_cors import CORS
# import pyodbc
# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend communication
# # socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
# # OPC UA connection options
# # Connection details
# server = 'SHREYASHNEXGEN\WINCCFLEX2014'
# database = 'Shreyash'
# conn = pyodbc.connect(
#     f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#     f"SERVER={server};"
#     f"DATABASE={database};"
#     f"Trusted_Connection=yes;"
# )
# import os
# # DB_PATH = 'a2z_database.db'
# # DB_PATH = 'Main_database.db'
# # Fetch the ENDPOINT_URL dynamically
# def fetch_endpoint_url():
#     """Fetch plcIp and plcPort from MSSQL database and construct ENDPOINT_URL."""
#     try:
#         cursor = conn.cursor()
        
#         # Fetch plcIp and plcPort from the database
#         cursor.execute("SELECT plcIp, plcPort FROM Plc_Table")
#         result = cursor.fetchone()
        
#         if result:
#             plc_ip, plc_port = result
#             endpoint_url = f"opc.tcp://{plc_ip}:{plc_port}"
#             return endpoint_url
#         else:
#             return "No PLC data available in the database."
#     except pyodbc.Error as e:
#         return f"Database error: {e}"
#     finally:
#         cursor.close()
# ENDPOINT_URL = fetch_endpoint_url()

# # # Get the base directory of the executable or script
# # base_dir = os.path.dirname(os.path.abspath(__file__))

# # # Paths to each database
# # database1_path = os.path.join(base_dir, 'suvi_database.db')
# # database2_path = os.path.join(base_dir, 'a2z_database.db')
# # database3_path = os.path.join(base_dir, 'RMS.db')
# # # Example: Configure SQLAlchemy or SQLite connections
# # app.config['DATABASE_1_URI'] = f'sqlite:///{database1_path}'
# # app.config['DATABASE_2_URI'] = f'sqlite:///{database2_path}'
# # app.config['DATABASE_3_URI'] = f'sqlite:///{database3_path}'
# # SQLite database setup
# # Secret key for session encryption
# app.secret_key = 'your_secret_key'
# app.config['SESSION_TYPE'] = 'filesystem'
# app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout


# # DB_PATH1 = 'suvi_database.db'
# # MONGO_URI = "mongodb://localhost:27017"  # MongoDB URI
# # MONGO_DB_NAME = "suvi_flask_db"          # MongoDB Database Name
# # MONGO_COLLECTION_NAME = "suvi_flask"       # MongoDB Collection Name      # MongoDB Collection Name
# # pos_values = []
# # submenu_values =[]
# # Function to browser
# def init_db():
#     """Initialize the MSSQL database."""
#     try:
#         cursor = conn.cursor()

#         # Create tables
#         tables = {
#             "Tag_Table": """
#                 CREATE TABLE Tag_Table (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     tagId NVARCHAR(255) UNIQUE NOT NULL,
#                     tagName NVARCHAR(255) UNIQUE NOT NULL,
#                     tagAddress NVARCHAR(255) NOT NULL,
#                     plcId NVARCHAR(255) NOT NULL
#                 )
#             """,
#             "Raw_Materials": """
#                     CREATE TABLE Raw_Materials (
#                         material_Id INT IDENTITY(1,1) PRIMARY KEY,
#                         typeCode NVARCHAR(255) NOT NULL,
#                         lotNo NVARCHAR(255) NOT NULL,
#                         materialType NVARCHAR(255) NOT NULL UNIQUE,
#                         make NVARCHAR(255) NOT NULL,
#                         [user] NVARCHAR(255) NOT NULL,
#                         barcode NVARCHAR(255) NOT NULL
#                     )
#             """,
#             "Recipe": """ CREATE TABLE Recipe (
#                        Recipe_ID INT PRIMARY KEY,
#                         Filter_Size NVARCHAR(255),
#                         Filter_Code NVARCHAR(255),
#                         Art_No INT,
#                         Recipe_Name NVARCHAR(255)
#                     )
#             """,
#             "Recipe_Details1": """
#                 CREATE TABLE Recipe_Details1 (
#                         Id INT IDENTITY(1,1) PRIMARY KEY,
#                         Pos1 NVARCHAR(255),
#                         Pos2 NVARCHAR(255),
#                         Pos3 NVARCHAR(255),
#                         Pos4 NVARCHAR(255),
#                         Pos5 NVARCHAR(255),
#                         Pos6 NVARCHAR(255),
#                         Pos7 NVARCHAR(255),
#                         Pos8 NVARCHAR(255),
#                         Pos9 NVARCHAR(255),
#                         Alu_coil_width NVARCHAR(255),
#                         Alu_roller_type INT,
#                         Spacer FLOAT,
#                         Recipe_ID INT FOREIGN KEY REFERENCES Recipe(Recipe_ID)
#                     )
#             """,
#             "Recipe_Log": """
#                     CREATE TABLE Recipe_Log (
#                         Batch_No INT IDENTITY(1,1) PRIMARY KEY,
#                         Batch_Code NVARCHAR(255) NOT NULL,
#                         Timestamp DATETIME2 NOT NULL DEFAULT GETDATE(),
#                         Recipe_ID INT NOT NULL FOREIGN KEY REFERENCES Recipe(Recipe_ID),
#                         motor_speed NVARCHAR(255),
#                         motor_stroke NVARCHAR(255),
#                         other_speed_force NVARCHAR(255),
#                         alu_coil_width NVARCHAR(255),
#                         Quantity INT,
#                         Batch_Running_Status NVARCHAR(255) NOT NULL,
#                         Batch_Completion_Status NVARCHAR(255) NOT NULL
#                     )
#             """,
#              "Sub_Menu":"""
#                     CREATE TABLE Sub_Menu (
#                         Recipe_ID INT PRIMARY KEY FOREIGN KEY REFERENCES Recipe(Recipe_ID),
#                         motor_speed NVARCHAR(255),
#                         motor_stroke NVARCHAR(255),
#                         other_speed_force NVARCHAR(255),
#                         alu_coil_width NVARCHAR(255)
#                     )
#                 """,
#             "Live_Tags": """
#                 CREATE TABLE Live_Tags (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     tagId NVARCHAR(255) NOT NULL,
#                     value NVARCHAR(255) NOT NULL,
#                     timestamp DATETIME DEFAULT GETDATE(),
#                     FOREIGN KEY (tagId) REFERENCES Tag_Table(tagId)
#                 )
#             """,
#             "Live_Log": """
#                 CREATE TABLE Live_Log (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     tagName NVARCHAR(255) NOT NULL,
#                     tagId NVARCHAR(255) NOT NULL,
#                     value NVARCHAR(255) NOT NULL,
#                     timestamp DATETIME DEFAULT GETDATE()
#                 )
#             """,
#             "connection_status": """
#                 CREATE TABLE connection_status (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     internet_status NVARCHAR(50) NOT NULL,
#                     plc_status NVARCHAR(50) NOT NULL,
#                     timestamp DATETIME DEFAULT GETDATE()
#                 )
#             """,
#             "internet_status": """
#                 CREATE TABLE internet_status (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     startTime NVARCHAR(50) NOT NULL,
#                     endTime NVARCHAR(50) NOT NULL,
#                     time_Duration NVARCHAR(50) NOT NULL,
#                     status NVARCHAR(50) NOT NULL
#                 )
#             """,
#             "plc_status": """
#                 CREATE TABLE plc_status (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     startTime NVARCHAR(50) NOT NULL,
#                     endTime NVARCHAR(50) NOT NULL,
#                     time_Duration NVARCHAR(50) NOT NULL,
#                     status NVARCHAR(50) NOT NULL
#                 )
#             """,
#             "users": """
#                 CREATE TABLE users (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     username NVARCHAR(255) NOT NULL UNIQUE,
#                     email NVARCHAR(255) NOT NULL UNIQUE,
#                     password NVARCHAR(255) NOT NULL,
#                     is_admin INT DEFAULT 0
#                 )
#             """,
#             "user_activity": """
#                 CREATE TABLE user_activity (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     username NVARCHAR(255) NOT NULL,
#                     login_time DATETIME,
#                     logout_time DATETIME,
#                     FOREIGN KEY (username) REFERENCES users(username)
#                 )
#             """,
#             "Plc_Table": """
#                 CREATE TABLE Plc_Table (
#                     Id INT IDENTITY(1,1) PRIMARY KEY,
#                     plcId INT DEFAULT 1,
#                     plcName NVARCHAR(50) DEFAULT 'Plc1',
#                     plcIp NVARCHAR(50) DEFAULT '192.168.0.1',
#                     plcPort INT DEFAULT 4840,
#                     intervalTime INT DEFAULT 20,
#                     serial_Key NVARCHAR(50) DEFAULT '12345'
#                 )
#             """,
#             "BatchTracker": """
#                 CREATE TABLE BatchTracker (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     number_of_batches_created INT NOT NULL
#                 )
#             """
#         }

#         for table, query in tables.items():
#             cursor.execute(f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table}' AND xtype='U') {query}")
#             conn.commit()

#         # Insert default Plc_Table entry if table is empty
#         cursor.execute("SELECT COUNT(*) FROM Plc_Table")
#         if cursor.fetchone()[0] == 0:
#             cursor.execute("""
#                 INSERT INTO Plc_Table (plcId, plcName, plcIp, plcPort, intervalTime, serial_Key)
#                 VALUES (1, 'Plc1', '192.168.0.1', 4840, 20, '11223344')
#             """)
#             conn.commit()

#         # Insert default BatchTracker entry if table is empty
#         cursor.execute("SELECT COUNT(*) FROM BatchTracker")
#         if cursor.fetchone()[0] == 0:
#             cursor.execute("INSERT INTO BatchTracker (number_of_batches_created) VALUES (0)")
#             conn.commit()

#         print("Database initialization and setup completed successfully.")
#     except pyodbc.Error as e:
#         print(f"Error initializing the database: {e}")

# # Initialize the database
# init_db()

# # Hardcoded user data for simplicity 
# USER_DATA = {
#     'username': 'admin',
#     'password_hash': generate_password_hash('password123')  # Secure hashed password
# }
# @app.route('/status', methods=['GET'])
# def get_status():
#     try:
#         cursor = conn.cursor()

#         # Fetch PLC IP and Interval Time
#         cursor.execute("SELECT plcIp, intervalTime FROM Plc_Table")
#         plc_data = cursor.fetchone()
#         plc_ip = plc_data[0] if plc_data else "Not Available"
#         interval_time = plc_data[1] if plc_data else "Not Set"

#         # Fetch Tag Count
#         cursor.execute("SELECT COUNT(*) FROM Tag_Table")
#         tags_count = cursor.fetchone()[0]

#         # Fetch Log Count from BatchTracker
#         cursor.execute("SELECT number_of_batches_created FROM BatchTracker")
#         result = cursor.fetchone()
#         logs_count = result[0] if result else 0

#         # Get Serial Key
#         serial_key = platform.node()  # Fetches the computer's hostname as serial key

#         # Update Serial Key in Plc_Table
#         cursor.execute("UPDATE Plc_Table SET serial_Key = ? WHERE plcId = 1", (serial_key,))
#         conn.commit()

#         # Internet and PLC connection statuses
#         internet_connected = check_internet_connection()
#         plc_connected = check_plc_connection(plc_ip)

#         # Return the statuses
#         return jsonify({
#             "Plc_IP": plc_ip,
#             "Internet_Connected": internet_connected,
#             "Plc_Connected": plc_connected,
#             "No_Of_Tags_Created": tags_count,
#             "No_Of_Logs_Created": logs_count,
#             "Interval_Time_Of_Log_Entry": interval_time,
#             "Serial_Key": serial_key
#         })
#     except pyodbc.Error as e:
#         return jsonify({"error": f"Database error: {str(e)}"})
#     except Exception as e:
#         return jsonify({"error": str(e)})
#     finally:
#         cursor.close()
# def check_internet_connection():
#     """Check if the server has internet connectivity."""
#     try:
#         import socket
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         return "Connected"
#     except Exception:
#         return "Not Connected"

# def check_plc_connection(plc_ip):
#     """Check if the PLC is reachable."""
#     try:
#         import os
#         response = os.system(f"ping -n 1 {plc_ip}")  # Replace `-c` with `-n` for Windows
#         return "Connected" if response == 0 else "Not Connected"
#     except Exception:
#         return "Unknown"

# def get_last_status(table_name): 
#     """Retrieve the last status from the specified table."""
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT TOP 1 status FROM {table_name} ORDER BY id DESC")
#     result = cursor.fetchone()
#     cursor.close()  # Close cursor instead of closing the connection
#     return result[0] if result else None

# def get_last_combined_status():
#     """Retrieve the last combined status (internet and PLC) from the connection_status table."""
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT TOP 1 internet_status, plc_status 
#         FROM connection_status
#         ORDER BY id DESC
#     """)
#     result = cursor.fetchone()
#     cursor.close()  # Close cursor instead of closing the connection
#     return result if result else (None, None)

# def calculate_duration(start_time, end_time):
#     """Calculate the duration between two timestamps."""
#     start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
#     end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
#     duration = end - start
#     return str(duration)

# def log_status():
#     """Log statuses for Internet and PLC into tables."""
#     # Initialize previous statuses and start times
#     last_internet_status = check_internet_connection()
#     last_plc_status = check_plc_connection("192.168.0.1")  # Replace with actual PLC IP
#     internet_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     plc_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     while True:
#         try:
#             # Get current statuses
#             internet_status = check_internet_connection()
#             plc_status = check_plc_connection("192.168.0.1")  # Replace with actual PLC IP
#             current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             # Get the last logged combined status
#             last_combined_status = get_last_combined_status()

#             # Use single connection for all operations
#             cursor = conn.cursor()

#             # Log to connection_status table only if status has changed
#             if (internet_status, plc_status) != last_combined_status:
#                 cursor.execute("""
#                     INSERT INTO connection_status (timestamp, internet_status, plc_status)
#                     VALUES (?, ?, ?)
#                 """, (current_time, internet_status, plc_status))
#                 conn.commit()

#             # Handle Internet status changes
#             if internet_status != last_internet_status:
#                 last_record_status = get_last_status("internet_status")
#                 if last_record_status != internet_status:
#                     duration = calculate_duration(internet_start_time, current_time)
#                     cursor.execute("""
#                         INSERT INTO internet_status (startTime, endTime, time_Duration, status)
#                         VALUES (?, ?, ?, ?)
#                     """, (internet_start_time, current_time, duration, internet_status))
#                     conn.commit()

#                 # Update start time and last status
#                 internet_start_time = current_time
#                 last_internet_status = internet_status

#             # Handle PLC status changes
#             if plc_status != last_plc_status:
#                 last_record_status = get_last_status("plc_status")
#                 if last_record_status != plc_status:
#                     duration = calculate_duration(plc_start_time, current_time)
#                     cursor.execute("""
#                         INSERT INTO plc_status (startTime, endTime, time_Duration, status)
#                         VALUES (?, ?, ?, ?)
#                     """, (plc_start_time, current_time, duration, plc_status))
#                     conn.commit()

#                 # Update start time and last status
#                 plc_start_time = current_time
#                 last_plc_status = plc_status

#             # Wait for 1 second before the next check
#             time.sleep(30)

#         except Exception as e:
#             print(f"Error: {e}")

# # # Close connection when done (optional: in case of script termination)
# # conn.close()


# @app.route('/status1', methods=['GET'])
# def get_status_summary():
#     """Fetch summary for pie charts."""
#     # conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT 
#             SUM(CASE WHEN internet_status = 'Connected' THEN 1 ELSE 0 END) AS internet_uptime,
#             SUM(CASE WHEN internet_status = 'Not Connected' THEN 1 ELSE 0 END) AS internet_downtime,
#             SUM(CASE WHEN plc_status = 'Connected' THEN 1 ELSE 0 END) AS plc_connected,
#             SUM(CASE WHEN plc_status = 'Not Connected' THEN 1 ELSE 0 END) AS plc_disconnected
#         FROM connection_status
#     """)
#     result = cursor.fetchone()
#     # conn.close()

#     return jsonify({
#         "internet": {"uptime": result[0], "downtime": result[1]},
#         "plc": {"connected": result[2], "disconnected": result[3]}
#     })


# def get_db_connection():
#     """Establishes a connection to MSSQL Server."""
#     try:
#         conn = pyodbc.connect(
#             f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#             f"SERVER={server};"
#             f"DATABASE={database};"
#             f"Trusted_Connection=yes;"
#         )
#         return conn
#     except pyodbc.Error as e:
#         flash(f"Database connection error: {e}", "danger")
#         return None

# @app.route('/')
# def index():
#     """Main dashboard route with pagination."""
#     if 'username' not in session:  # User must be logged in
#         return redirect(url_for('login'))

#     # Pagination
#     page = max(1, request.args.get('page', 1, type=int))
#     per_page = 10
#     offset = (page - 1) * per_page

#     conn = get_db_connection()
#     if not conn:
#         return redirect(url_for('login'))

#     cursor = conn.cursor()

#     # Fetch paginated data
#     cursor.execute("""
#      SELECT * FROM Recipe
#     ORDER BY Recipe_ID  
#     OFFSET ? ROWS
#     FETCH NEXT ? ROWS ONLY
#     """, (offset, per_page))

#     recipes = cursor.fetchall()

#     # Calculate total pages
#     cursor.execute("SELECT COUNT(*) FROM Recipe")
#     total_count = cursor.fetchone()[0]
#     total_pages = (total_count + per_page - 1) // per_page

#     conn.close()

#     return render_template(
#         'dashboard.html',
#         # recipes=recipes,  # Pass data to template
#         # page=page,
#         # total_pages=total_pages
#     )

# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register', 'static']  # Allow public routes and static files
#     if request.endpoint not in allowed_routes and 'id' not in session:
#         if not request.endpoint or request.endpoint.startswith('static'):  # Allow static files
#             return
#         flash('Please log in to access this page.', 'warning')
#         return redirect(url_for('login'))

# @app.route('/dashboard')
# def dashboard():
#     if 'username' not in session:
#         flash('Please log in to access the dashboard.', 'warning')
#         return redirect(url_for('login'))
#     return render_template('dashboard.html', username=session['username'])

# @app.route('/recipe')
# def recipe_list():
#     """Fetch and display paginated recipe list from MSSQL."""
#     if 'username' not in session:  # Check if the user is logged in
#         return redirect(url_for('login'))

#     # Pagination logic
#     page = max(1, request.args.get('page', 1, type=int))
#     per_page = 10
#     offset = (page - 1) * per_page

#     conn = get_db_connection()
#     if not conn:
#         return redirect(url_for('login'))  # Redirect if DB connection fails

#     cursor = conn.cursor()

#     # Fetch paginated recipes
#     cursor.execute("""
#         SELECT * FROM Recipe 
#         ORDER BY Recipe_ID
#         OFFSET ? ROWS 
#         FETCH NEXT ? ROWS ONLY
#     """, (offset, per_page))
#     recipes = cursor.fetchall()

#     # Fetch distinct material types
#     cursor.execute("SELECT DISTINCT materialType FROM Raw_Materials")
#     pos_values = [row[0] for row in cursor.fetchall()]

#     # Get total recipe count
#     cursor.execute("SELECT COUNT(*) FROM Recipe")
#     total_count = cursor.fetchone()[0]
#     total_pages = (total_count + per_page - 1) // per_page

#     conn.close()

#     return render_template(
#         'recipe.html',
#         recipes=recipes,
#         pos_values=pos_values,
#         page=page,
#         total_pages=total_pages
#     )

# @app.route('/api/recipe_log', methods=['GET'])
# def get_recipe_log():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM Recipe_Log")  # Adjust query if needed
#     rows = cursor.fetchall()  # Fetch list of tuples

#     # Convert tuples into a list of dictionaries
#     recipe_logs = [
#         {
#             "Batch_Code": row[1],
#             "Timestamp": row[2],
#             "Recipe_ID": row[3],
#             "motor_speed": row[4],
#             "motor_stroke": row[5],
#             "other_speed_force": row[6],
#             "alu_coil_width": row[7],
#             "Quantity": row[8],
#             "Batch_Running_Status": row[9],
#             "Batch_Completion_Status": row[10]
#         }
#         for row in rows
#     ]

#     conn.close()
#     return jsonify(recipe_logs)  # Return JSON response
# def update_batch_status():
#     """Fetch and update batch status based on PLC values."""
#     while True:
#         conn = get_db_connection()
#         if not conn:
#             continue  # Skip iteration if DB connection fails

#         cursor1 = conn.cursor()
#         cursor2 = conn.cursor()
        
#         cursor1.execute("""
#             SELECT Batch_Code, Quantity FROM Recipe_Log 
#             WHERE Batch_Completion_Status IN ('Pending', 'Partially Completed')
#         """)
#         recipe_logs = cursor1.fetchall()
#         # print("recipe_logs: ",recipe_logs)
#         client = Client(ENDPOINT_URL)
    
#         client.session_timeout = 30000  # Adjust timeout as needed

#         try:
#             client.connect()
            
#             for log in recipe_logs:
#                 batch_code, total_quantity = log

#                 # PLC field paths (replace with actual paths)
#                 quantity_field_path = 'ns=3;s="OpenRecipe"."actBatchQty"'
#                 machine_state_field_path = 'ns=3;s="OpenRecipe"."machineState"'

#                 current_quantity = client.get_node(quantity_field_path).get_value()
#                 machine_state = client.get_node(machine_state_field_path).get_value()

#                 # Calculate completion percentage
#                 completion_percentage = (current_quantity / total_quantity) * 100

#                 # Determine running status
#                 running_status = "Pending" if machine_state == 0 else "Running"

#                 # Determine completion status
#                 if completion_percentage < 60:
#                     completion_status = "Pending"
#                 elif 60 <= completion_percentage < 100:
#                     completion_status = "Partially Completed"
#                 else:
#                     completion_status = "Completed"
#                     running_status = "Completed"

#                     # Set `machineState` to `0` in PLC
#                     node = client.get_node(machine_state_field_path)
#                     variant = ua.DataValue(ua.Variant(0, ua.VariantType.Int32))
#                     node.set_value(variant)
#                 # print("everything ok")
#                 # Update MSSQL database
#                 cursor2.execute("""
#                     UPDATE Recipe_Log
#                     SET Batch_Running_Status = ?, Batch_Completion_Status = ?
#                     WHERE Batch_Code = ?
#                 """, (running_status, completion_status, batch_code))

#                 conn.commit()

#         except Exception as e:
#             print(f"Error updating batch status: {e}")
#         finally:
#             client.disconnect()
#             cursor1.close()
#             cursor2.close()
#             conn.close()

# @app.route('/role', methods=['GET', 'POST'])
# def role():
#     """Manage user roles (Admin only)."""
#     if session.get('username') != 'Admin':  # Ensure only Admins can access
#         flash('Access denied: Admins only.', 'danger')
#         return redirect(url_for('dashboard'))

#     conn = get_db_connection()
#     if not conn:
#         return redirect(url_for('dashboard'))

#     cursor = conn.cursor()

#     # Fetch unique usernames
#     cursor.execute("SELECT DISTINCT username FROM users")
#     users = [row[0] for row in cursor.fetchall()]

#     if request.method == 'POST':
#         selected_user = request.form.get('username')
#         roles = request.form.getlist('roles')

#         if selected_user and roles:
#             roles_str = ','.join(roles)  # Convert roles list to string

#             # Update roles in the MSSQL database
#             cursor.execute("""
#                 UPDATE users SET roles = ? WHERE username = ?
#             """, (roles_str, selected_user))

#             conn.commit()
#             flash(f'Roles updated for {selected_user}', 'success')

#     cursor.close()
#     conn.close()
#     return render_template('roles.html', users=users)
# @app.route('/get_roles', methods=['POST'])
# def get_roles():
#     """Fetch user roles from MSSQL based on the provided username."""
#     username = request.json.get('username')  # Get username from the AJAX request
#     if not username:
#         return jsonify({'error': 'Username is required'}), 400

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({'error': 'Database connection failed'}), 500

#     cursor = conn.cursor()

#     try:
#         # Fetch roles for the selected user
#         cursor.execute("SELECT roles FROM users WHERE username = ?", (username,))
#         result = cursor.fetchone()

#         roles = result[0].split(',') if result and result[0] else []
#         return jsonify({'roles': roles})

#     except pyodbc.Error as e:
#         return jsonify({'error': f'Database query error: {str(e)}'}), 500

#     finally:
#         cursor.close()
#         conn.close()

# @app.route('/event_log', methods=['GET'])
# def event_log():
#     """Fetch and display user login/logout activity logs with pagination."""
#     if session.get('username') != 'Admin':  # Replace 'Admin' with your admin identifier
#         flash('Access denied: Admins only.', 'danger')
#         return redirect(url_for('dashboard'))

#     conn = get_db_connection()
#     if not conn:
#         return redirect(url_for('dashboard'))

#     cursor = conn.cursor()

#     # Fetch user summary data for activity logs (handling logout properly)
#     cursor.execute("""
#         SELECT 
#             username,
#             MAX(login_time) AS last_login_time,
#             (
#                 SELECT TOP 1 logout_time 
#                 FROM user_activity 
#                 WHERE username = ua.username 
#                 AND logout_time IS NOT NULL 
#                 ORDER BY logout_time DESC
#             ) AS last_logout_time
#         FROM user_activity ua
#         GROUP BY username
#     """)

#     user_summary = []
#     for row in cursor.fetchall():
#         username, last_login_time, last_logout_time = row
#         last_login_date = last_login_time.strftime("%Y-%m-%d") if last_login_time else "N/A"
#         last_login_time = last_login_time.strftime("%H:%M:%S") if last_login_time else "N/A"
#         last_logout_date = last_logout_time.strftime("%Y-%m-%d") if last_logout_time else "N/A"
#         last_logout_time = last_logout_time.strftime("%H:%M:%S") if last_logout_time else "N/A"

#         user_summary.append({
#             'username': username,
#             'last_login_date': last_login_date,
#             'last_login_time': last_login_time,
#             'last_logout_date': last_logout_date,
#             'last_logout_time': last_logout_time if last_logout_time else "Currently Logged In"
#         })

#     # Pagination setup
#     page = request.args.get('page', 1, type=int)
#     per_page = 5
#     offset = (page - 1) * per_page

#     selected_username = request.args.get('username')
#     selected_user_details = []
#     total_pages = None

#     if selected_username:
#         cursor.execute("""
#             SELECT 
#                 CONVERT(VARCHAR, login_time, 23) AS login_date,
#                 CONVERT(VARCHAR, login_time, 8) AS login_time,
#                 CASE 
#                     WHEN logout_time IS NULL THEN NULL 
#                     ELSE CONVERT(VARCHAR, logout_time, 23) 
#                 END AS logout_date,
#                 CASE 
#                     WHEN logout_time IS NULL THEN NULL 
#                     ELSE CONVERT(VARCHAR, logout_time, 8) 
#                 END AS logout_time
#             FROM user_activity
#             WHERE username = ?
#             ORDER BY login_time DESC
#             OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
#         """, (selected_username, offset, per_page))

#         selected_user_details = [
#             {
#                 'login_date': row[0],
#                 'login_time': row[1],
#                 'logout_date': row[2] or "Currently Logged In",
#                 'logout_time': row[3] or "Currently Logged In",
#             }
#             for row in cursor.fetchall()
#         ]

#         # Get total log count for pagination
#         cursor.execute("SELECT COUNT(*) FROM user_activity WHERE username = ?", (selected_username,))
#         total_logs = cursor.fetchone()[0]
#         total_pages = (total_logs + per_page - 1) // per_page  # Calculate total pages

#     conn.close()

#     return render_template(
#         'event_log.html',
#         user_summary=user_summary,
#         selected_username=selected_username,
#         selected_user_details=selected_user_details,
#         page=page,
#         total_pages=total_pages
#     )

# @app.route('/reset-password', methods=['POST'])
# def reset_password():
    
#     user_id = request.form['user_id']
#     new_password = request.form['new_password']

#     # Hash the new password (important for security)
#     hashed_password = generate_password_hash(new_password)

#     # Update the password in the database
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
#     conn.commit()
#     conn.close()

#     flash('Password has been reset successfully!', 'success')
#     return redirect(url_for('users'))
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """User login with password hashing and activity tracking."""
#     conn = get_db_connection()
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

        
#         if not conn:
#             return redirect(url_for('login'))

#         cursor = conn.cursor()
        
#         # Fetch user details
#         cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
#         user = cursor.fetchone()

#         if user and check_password_hash(user[2], password):  # Verifying hashed password
#             session['id'] = user[0]
#             session['username'] = user[1]
#             session['is_admin'] = user[3]

#             # Insert login activity (MSSQL uses `GETDATE()` for current timestamp)
#             cursor.execute("INSERT INTO user_activity (username, login_time) VALUES (?, GETDATE())", (username,))
#             conn.commit()

#             flash('Login successful!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password.', 'danger')

#         conn.close()

#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """User registration with hashed passwords and duplicate username/email check."""
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')

#         # Check if passwords match
#         if password != confirm_password:
#             flash('Passwords do not match!', 'danger')
#             return redirect(url_for('register'))

#         # Hash the password
#         hashed_password = generate_password_hash(password)

#         conn = get_db_connection()
#         if not conn:
#             return redirect(url_for('register'))

#         try:
#             cursor = conn.cursor()

#             # Check if username or email already exists
#             cursor.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
#             if cursor.fetchone():
#                 flash('Username or email already taken!', 'danger')
#                 conn.close()
#                 return redirect(url_for('register'))

#             # Insert new user into MSSQL database
#             cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
#                            (username, email, hashed_password))
#             conn.commit()

#             flash('Registration successful! Please log in.', 'success')
#             return redirect(url_for('login'))

#         except pyodbc.Error as e:
#             flash(f"Database error: {e}", 'danger')
#         finally:
#             print("REGISTER DONE")

#     return render_template('register.html')

# @app.route('/users')
# def users():
#     """Admin-only route to fetch user details from MSSQL database."""
#     if session.get('username') != 'Admin':  # Ensure only Admin can access
#         flash('Access denied: Admins only.', 'danger')
#         return redirect(url_for('dashboard'))

#     conn = get_db_connection()
#     if not conn:
#         return redirect(url_for('dashboard'))

#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT id, username, email, is_admin FROM users")
#         users_data = cursor.fetchall()

#         users_list = []
#         for row in users_data:
#             users_list.append({
#                 'id': row[0],
#                 'username': row[1],
#                 'email': row[2],
#                 'is_admin': 'Yes' if row[3] else 'No'
#             })

#         return render_template('users.html', users=users_list)

#     except pyodbc.Error as e:
#         flash(f"Database error: {e}", 'danger')
#     finally:
#         conn.close()

# @app.route('/validate-admin-password', methods=['POST'])
# def validate_admin_password():
#     data = request.json
#     admin_password = "admin123"  # Predefined admin password

#     if data.get('password') == admin_password:
#         return jsonify({'success': True})
#     else:
#         return jsonify({'success': False})
# @app.route('/logout')
# def logout():
#     """Logs out the user and updates their logout time in MSSQL."""
#     if 'username' in session:
#         username = session['username']

#         conn = get_db_connection()
#         if not conn:
#             return redirect(url_for('dashboard'))  # Redirect if connection fails

#         try:
#             cursor = conn.cursor()

#             # Update the logout time for the latest login session
#             cursor.execute("""
#                 UPDATE user_activity 
#                 SET logout_time = GETDATE() 
#                 WHERE username = ? 
#                 AND logout_time IS NULL
#             """, (username,))
#             conn.commit()

#             # Remove user from session
#             session.pop('username', None)

#             flash('You have been logged out successfully.', 'success')

#         except pyodbc.Error as e:
#             flash(f"Database error: {e}", 'danger')
#         finally:
#             conn.close()

#     return redirect(url_for('login'))


# @app.route('/tag-overview')
# def tag_overview():
#     """Displays a paginated tag overview."""
#     if 'username' not in session:  # Check if the user is logged in
#         flash("Login first to access the Tag Overview.", "warning")
#         return redirect(url_for('login'))  # Redirect to login if not logged in

#     # Get the page and limit parameters from the query string
#     current_page = int(request.args.get('page', 1))  # Default to page 1
#     limit = int(request.args.get('limit', 10))  # Default limit is 10
    
#     # Calculate offset for pagination
#     offset = (current_page - 1) * limit

#     # Establish database connection
#     conn = get_db_connection()
#     if not conn:
#         flash("Database connection failed.", "danger")
#         return redirect(url_for('dashboard'))

#     try:
#         cursor = conn.cursor()

#         # Fetch paginated data
#         cursor.execute("""
#             SELECT * FROM Tag_Table 
#             ORDER BY id 
#             OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
#         """, (offset, limit))
#         tags = cursor.fetchall()

#         # Fetch the total number of rows
#         cursor.execute("SELECT COUNT(*) FROM Tag_Table")
#         total_rows = cursor.fetchone()[0]
#         total_pages = (total_rows + limit - 1) // limit  # Calculate total pages

#     except pyodbc.Error as e:
#         flash(f"Database error: {e}", "danger")
#         return redirect(url_for('dashboard'))
    
#     finally:
#         conn.close()

#     # Render the template with tags and pagination details
#     return render_template(
#         'tag_overview.html',
#         tags=tags,
#         page=current_page,
#         total_pages=total_pages,
#         limit=limit,
#         active_menu='tags',
#         active_submenu='tag-overview'
#     )

# @app.route('/update-tag/<string:tagId>', methods=['PUT'])
# def update_tag(tagId):
#     """Update an existing tag in the Tag_Table."""
#     try:
#         # Parse JSON data from the request
#         data = request.get_json()
#         tagName = data.get('tagName')
#         tagAddress = data.get('tagAddress')
#         plcId = data.get('plcId')

#         if not tagName or not tagAddress or not plcId:
#             return jsonify({"success": False, "error": "Missing required fields"}), 400

#         # Connect to MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"}), 500

#         cursor = conn.cursor()

#         # Check if the tag exists
#         cursor.execute("SELECT 1 FROM Tag_Table WHERE tagId = ?", (tagId,))
#         if not cursor.fetchone():
#             conn.close()
#             return jsonify({"success": False, "error": "Tag not found"}), 404

#         # Update the tag details in the database
#         cursor.execute("""
#             UPDATE Tag_Table
#             SET tagName = ?, tagAddress = ?, plcId = ?
#             WHERE tagId = ?
#         """, (tagName, tagAddress, plcId, tagId))

#         conn.commit()
#         conn.close()

#         # Fetch and update the live value of the updated tag
#         fetch_and_update_live_value(tagAddress)

#         # Respond with success message
#         return jsonify({"success": True, "message": "Tag updated successfully"})

#     except pyodbc.Error as e:
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

#     except Exception as e:
#         return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


# @app.route('/delete-tag/<int:tag_id>', methods=['DELETE'])
# def delete_tag(tag_id):
#     """Delete a tag from Tag_Table and Live_Tags in MSSQL."""
#     try:
#         # Check if user is logged in
#         if 'username' not in session:
#             return jsonify({"success": False, "error": "Unauthorized"}), 401

#         # Connect to MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"}), 500

#         cursor = conn.cursor()

#         # Execute deletion queries
#         cursor.execute('DELETE FROM Tag_Table WHERE tagId = ?', (tag_id,))
#         cursor.execute('DELETE FROM Live_Tags WHERE tagId = ?', (tag_id,))
#         conn.commit()

#         # Check if any rows were affected
#         if cursor.rowcount == 0:
#             return jsonify({"success": False, "error": "Tag not found"}), 404

#         return jsonify({"success": True, "message": "Tag deleted successfully"})
    
#     except pyodbc.Error as e:
#         print(f"Database error: {e}")
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
    
#     except Exception as e:
#         print(f"Error while deleting tag: {e}")
#         return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500
    
#     finally:
#         if conn:
#             conn.close()



# @app.route('/live-tag')
# def live_tag():
#     """Fetch paginated live tag data from MSSQL."""
#     if 'username' not in session:  # Check if the user is logged in
#         return redirect(url_for('login'))

#     # Get the current page from the query string (default to 1)
#     current_page = int(request.args.get('page', 1))

#     # Pagination setup: 10 items per page
#     items_per_page = 10
#     offset = (current_page - 1) * items_per_page

#     # Connect to MSSQL database
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"success": False, "error": "Database connection failed"}), 500

#     cursor = conn.cursor()

#     try:
#         # Fetch paginated live tag data
#         cursor.execute("""
#             SELECT Live_Tags.Id, Tag_Table.tagName, Live_Tags.value, Live_Tags.timestamp
#             FROM Live_Tags
#             JOIN Tag_Table ON Live_Tags.tagId = Tag_Table.tagId
#             ORDER BY Live_Tags.timestamp DESC
#             OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
#         """, (offset, items_per_page))
#         live_tags = cursor.fetchall()

#         # Fetch total number of rows for pagination
#         cursor.execute("SELECT COUNT(*) FROM Live_Tags")
#         total_rows = cursor.fetchone()[0]
#         total_pages = (total_rows + items_per_page - 1) // items_per_page  # Calculate total pages

#     except pyodbc.Error as e:
#         print(f"Database error: {e}")
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

#     finally:
#         conn.close()

#     return render_template(
#         'live_tag.html',
#         live_tags=live_tags,       # Pass the retrieved live tag data
#         page=current_page,         # Pass the current page number
#         total_pages=total_pages,   # Pass total number of pages
#         active_menu='tags',        # Keep the Tags dropdown open
#         active_submenu='live-tag'  # Highlight the Live Tags submenu
#     )

# @app.route('/plc')
# def plc():
#     """Fetch PLC and Machine data from MSSQL."""
#     if session.get('username') != 'Admin':  # Ensure only Admin can access
#         flash('Access denied: Admins only.', 'danger')
#         return redirect(url_for('dashboard'))

#     # Connect to MSSQL database
#     conn = get_db_connection()
#     if not conn:
#         flash("Database connection failed", "danger")
#         return redirect(url_for('dashboard'))

#     cursor = conn.cursor()

#     try:
#         # Fetch PLC data
#         cursor.execute("SELECT * FROM Plc_Table")  # Adjust query as per your DB schema
#         plc_tags = cursor.fetchall()

#         # Fetch Machine data
#         cursor.execute("SELECT * FROM Machine_Table")  # Adjust query as per your DB schema
#         machine_tags = cursor.fetchall()

#     except pyodbc.Error as e:
#         print(f"Database error: {e}")
#         flash(f"Database error: {str(e)}", "danger")
#         return redirect(url_for('dashboard'))

#     finally:
#         conn.close()

#     # Render the template with the PLC and Machine data
#     return render_template('plc.html', plc_tags=plc_tags, machine_tags=machine_tags)

    
# @app.route('/raw-material', methods=['GET', 'POST'])
# def raw_material():
#     """Handle raw material addition (POST) and retrieval with pagination (GET)."""
    
#     if 'username' not in session:
#         return redirect(url_for('login'))
    
#     if request.method == 'POST':
#         try:
#             # Extract required fields from form
#             type_code = request.form['typeCode']
#             lot_no = request.form['lotNo']
#             material_type = request.form['materialType']

#             # Auto-generate fields
#             make = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             user = "admin"
#             barcode = f"-{type_code}-{lot_no}"  # Example barcode

#             # Connect to MSSQL database
#             conn = get_db_connection()
#             if not conn:
#                 return jsonify({"success": False, "message": "Database connection failed"}), 500
            
#             cursor = conn.cursor()

#             # Insert data into the Raw_Materials table
#             cursor.execute("""
#                 INSERT INTO Raw_Materials (typeCode, lotNo, materialType, make, [user], barcode) 
#                 VALUES (?, ?, ?, ?, ?, ?)""",
#                 (type_code, lot_no, material_type, make, user, barcode))
#             conn.commit()
            
#             return jsonify({"success": True, "message": "Material added successfully!"})

#         except pyodbc.Error as e:
#             print(f"Database Error: {e}")
#             return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

#         finally:
#             conn.close()

#     # Handle GET request for pagination
#     try:
#         current_page = int(request.args.get('page', 1))
#         limit = int(request.args.get('limit', 10))
#         offset = (current_page - 1) * limit

#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "message": "Database connection failed"}), 500
        
#         cursor = conn.cursor()

#         # Fetch paginated raw materials
#         cursor.execute("""
#             SELECT * FROM Raw_Materials 
#             ORDER BY material_Id
#             OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
#         """, (offset, limit))
#         raw_materials = cursor.fetchall()

#         # Calculate total pages
#         cursor.execute("SELECT COUNT(*) FROM Raw_Materials")
#         total_rows = cursor.fetchone()[0]
#         total_pages = (total_rows + limit - 1) // limit

#         conn.close()

#         # Render the template with paginated data
#         return render_template(
#             'raw_material.html',
#             raw_materials=raw_materials,
#             page=current_page,
#             total_pages=total_pages,
#             limit=limit
#         )

#     except pyodbc.Error as e:
#         print(f"Database Error: {e}")
#         return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# @app.route('/delete-raw-material/<int:raw_material_id>', methods=['DELETE'])
# def delete_raw_material(raw_material_id):
#     """Delete a raw material entry from MSSQL database."""
    
#     try:
#         print(f"Attempting to delete raw material with ID: {raw_material_id}")

#         # Check if user is logged in
#         if 'username' not in session:
#             print("Unauthorized access attempt.")
#             return jsonify({"success": False, "error": "Unauthorized"}), 401

#         # Connect to the MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"}), 500

#         cursor = conn.cursor()

#         # Check if the material exists
#         cursor.execute('SELECT * FROM Raw_Materials WHERE material_Id = ?', (raw_material_id,))
#         row = cursor.fetchone()

#         if row is None:
#             print(f"Material with ID {raw_material_id} not found.")
#             return jsonify({"success": False, "error": "Raw material not found"}), 404

#         # Delete the raw material
#         cursor.execute('DELETE FROM Raw_Materials WHERE material_Id = ?', (raw_material_id,))
#         conn.commit()

#         if cursor.rowcount == 0:
#             print(f"Failed to delete material with ID {raw_material_id}.")
#             return jsonify({"success": False, "error": "Failed to delete material"}), 500

#         print(f"Successfully deleted material with ID {raw_material_id}.")
#         return jsonify({"success": True})

#     except pyodbc.Error as e:
#         print(f"Database Error: {e}")
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

#     finally:
#         if conn:
#             conn.close()

# @app.route('/update-raw-material/<int:material_Id>', methods=['POST'])
# def update_raw_material(material_Id):
#     """Update raw material details in MSSQL database."""
    
#     try:
#         # Parse JSON data from the request
#         data = request.json
#         typeCode = data.get("typeCode")
#         lotNo = data.get("lotNo")
#         make = data.get("make")
#         user = data.get("user")
#         materialType = data.get("materialType")
#         barcode = data.get("barcode")

#         # Validate required fields
#         missing_fields = [field for field in ["typeCode", "lotNo", "make", "user", "materialType", "barcode"] if not data.get(field)]
#         if missing_fields:
#             return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing_fields)}"}), 400

#         # Connect to MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"}), 500

#         cursor = conn.cursor()

#         # Check if the material_Id exists
#         cursor.execute("SELECT COUNT(*) FROM Raw_Materials WHERE material_Id = ?", (material_Id,))
#         if cursor.fetchone()[0] == 0:
#             return jsonify({"success": False, "error": "Material with the given ID does not exist."}), 404

#         # Update the record
#         cursor.execute('''
#             UPDATE Raw_Materials
#             SET typeCode = ?, lotNo = ?, make = ?, user = ?, materialType = ?, barcode = ?
#             WHERE material_Id = ?
#         ''', (typeCode, lotNo, make, user, materialType, barcode, material_Id))
#         conn.commit()

#         if cursor.rowcount == 0:
#             return jsonify({"success": False, "error": "No changes were made to the raw material."}), 400

#         return jsonify({"success": True, "message": "Raw material updated successfully."})

#     except pyodbc.IntegrityError as e:
#         if "UNIQUE constraint failed: Raw_Materials.materialType" in str(e):
#             return jsonify({"success": False, "error": "Material Type must be unique."}), 409
#         return jsonify({"success": False, "error": f"Database integrity error: {str(e)}"}), 400

#     except pyodbc.Error as e:
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

#     except Exception as e:
#         return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

#     finally:
#         if conn:
#             conn.close()


# @app.route('/delete-recipe/<int:recipe_id>', methods=['DELETE'])
# def delete_recipe(recipe_id):
#     """Delete a recipe from MSSQL database."""
    
#     try:
#         # Debugging: Check if session contains username
#         if 'username' not in session:
#             print("Session does not contain 'username'. Current session:", session)
#             return jsonify({"success": False, "error": "Unauthorized access"}), 401

#         # Connect to MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"}), 500

#         cursor = conn.cursor()

#         # Check if the recipe exists before deletion
#         cursor.execute("SELECT COUNT(*) FROM Recipe WHERE Recipe_ID = ?", (recipe_id,))
#         if cursor.fetchone()[0] == 0:
#             return jsonify({"success": False, "error": "Recipe not found"}), 404

#         # Delete the recipe
#         cursor.execute("DELETE FROM Recipe WHERE Recipe_ID = ?", (recipe_id,))
#         conn.commit()

#         if cursor.rowcount == 0:
#             return jsonify({"success": False, "error": "Failed to delete recipe"}), 500

#         return jsonify({"success": True, "message": "Recipe deleted successfully"})

#     except pyodbc.Error as e:
#         return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

#     except Exception as e:
#         print(f"Error while deleting recipe: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500

#     finally:
#         if conn:
#             conn.close()
# def fetch_data_as_dict(cursor):
#     """Helper function to convert query result to dictionary."""
#     columns = [column[0] for column in cursor.description]
#     result = []
#     for row in cursor.fetchall():
#         result.append(dict(zip(columns, row)))
#     return result
# @app.route('/recipe/<int:recipe_id>')
# def recipe_details(recipe_id):
#     """Fetch and display recipe details."""
#     try:
#         # Check user session
#         if 'username' not in session:
#             flash("Please log in to access this page.", "warning")
#             return redirect(url_for('login'))

#         # Establish database connection
#         conn = get_db_connection()
#         if not conn:
#             flash("Database connection failed.", "danger")
#             return redirect(url_for('login'))
#         cursor1 = conn.cursor()
#         cursor1.execute("SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?", (recipe_id,))
#         recipe_details = cursor1.fetchall()

#         cursor2 = conn.cursor()
#         cursor2.execute("SELECT * FROM Sub_Menu WHERE Recipe_ID = ?", (recipe_id,))
#         sub_menu = cursor2.fetchall()
#         print("sub_menu:",sub_menu)


#         if not recipe_details:
#             flash("Recipe not found!", "danger")
#             return redirect(url_for('index'))

#         # Process data safely
#         pos_values = extract_pos_values(recipe_details) if recipe_details else []
#         submenu_values = extract_submenu_vaues(sub_menu) if sub_menu else []
#         barcode_value = "S3"  # Replace with actual barcode retrieval logic

#         flash(f"POS values written to PLC successfully for Recipe ID {recipe_id}.", "success")

#         return render_template(
#             'recipe_details.html',
#             recipe_details=recipe_details,
#             sub_menu=sub_menu[0],
#             pos_values=pos_values[:-1],  # Assuming last value should be removed
#             barcode_value=barcode_value
#         )

#     except pyodbc.Error as e:
#         flash(f"Database error: {str(e)}", "danger")
#         print(f"Database error at pyodbc error: {str(e)}", "danger")
        
#         return redirect(url_for('index'))

#     except Exception as e:
#         flash(f"An unexpected error occurred: {str(e)}", "danger")
#         print(f"An unexpected error occurred at exception: {str(e)}", "danger")
#         return redirect(url_for('index'))

#     finally:
#         if conn:
#             conn.close()  
# def extract_pos_values(recipe_details):
#     if not recipe_details:
#         return []

#     # Assuming the structure of each tuple in `recipe_details`
#     first_row = recipe_details[0]  # Get the first tuple

#     pos_values = [
#         first_row[1],  # Assuming `pos1` is at index 1
#         first_row[2],  # Assuming `pos2` is at index 2
#         first_row[3],  # Assuming `pos3` is at index 3
#         first_row[4],  # Assuming `pos4` is at index 4
#         first_row[5],  # Assuming `pos5` is at index 5
#         first_row[6],  # Assuming `pos6` is at index 6
#         first_row[7],  # Assuming `pos7` is at index 7
#         first_row[8],  # Assuming `pos8` is at index 8
#         first_row[9],  # Assuming `pos9` is at index 9
#         first_row[10],  # Assuming `recipe_id` is at index 10
#     ]
   
#     return pos_values

# def extract_submenu_vaues(sub_menu):
#     if not sub_menu:
#         return []

#     first_row = sub_menu[0]  # Get the first tuple

#     submenu_values = [
#         first_row[1],  # Assuming `motor_speed` is at index 1
#         first_row[2],  # Assuming `motor_stroke` is at index 2
#         first_row[3],  # Assuming `other_Speed_force` is at index 3
#         first_row[4],  # Assuming `alu_coil_width` is at index 4
#     ]
#     return submenu_values

# @app.route('/compare-pos', methods=['POST'])
# def compare_pos():
#     data = request.json  # Receive data from frontend
#     pos_value = data.get('posValue')
#     barcode_value = data.get('barcodeValue')

#     if pos_value is None or barcode_value is None:
#         return jsonify({"error": "Invalid data"}), 400

#     # Comparison logic
#     match = pos_value == barcode_value

#     return jsonify({"match": match})


# @app.route('/update_recipe', methods=['POST'])
# def update_recipe():
#     """Update an existing recipe with new details."""
    
#     # Ensure user is logged in
#     if 'username' not in session:
#         flash("Please log in to update recipes.", "warning")
#         return redirect(url_for('login'))

#     # Extract form data
#     recipe_id = request.form.get('recipe_id')
#     recipe_name = request.form.get('recipe_name')
#     filter_size = request.form.get('filter_size')
#     filter_code = request.form.get('filter_code')
#     art_no = request.form.get('art_no')
#     alu_coil_width = request.form.get('Alu_coil_width')
#     motor_speed = request.form.get('Motor_speed')
    
#     # Extract POS values (1-9)
#     pos_values = [request.form.get(f'pos{i}', None) for i in range(1, 10)]

#     # Validate required fields
#     required_fields = [recipe_id, recipe_name, filter_size, filter_code, art_no, alu_coil_width, motor_speed]
#     if any(field is None or field == "" for field in required_fields):
#         flash("All fields are required.", "danger")
#         return redirect(url_for('recipe_list'))

#     conn = get_db_connection()
#     if not conn:
#         flash("Database connection failed.", "danger")
#         return redirect(url_for('recipe_list'))

#     try:
#         cursor = conn.cursor()

#         # Update `Recipe` table
#         cursor.execute(
#             '''UPDATE Recipe 
#                SET Recipe_Name = ?, Filter_Size = ?, Filter_Code = ?, Art_No = ?
#                WHERE Recipe_ID = ?''',
#             (recipe_name, filter_size, filter_code, art_no, recipe_id)
#         )

#         # Update `Recipe_Details1` table
#         cursor.execute(
#             '''UPDATE Recipe_Details1 
#                SET Pos1 = ?, Pos2 = ?, Pos3 = ?, Pos4 = ?, Pos5 = ?, 
#                    Pos6 = ?, Pos7 = ?, Pos8 = ?, Pos9 = ?, Alu_coil_width = ?
#                WHERE Recipe_ID = ?''',
#             (*pos_values, alu_coil_width, recipe_id)
#         )

#         # Update `Sub_Menu` table
#         cursor.execute(
#             '''UPDATE Sub_Menu 
#                SET motor_speed = ?
#                WHERE Recipe_ID = ?''',
#             (motor_speed, recipe_id)
#         )

#         # Commit changes
#         conn.commit()

#         flash("Recipe updated successfully!", "success")

#     except pyodbc.Error as e:
#         flash(f"Database error: {str(e)}", "danger")
#         conn.rollback()  # Rollback in case of error

#     except Exception as e:
#         flash(f"Unexpected error: {str(e)}", "danger")

#     finally:
#         conn.close()

#     return redirect(url_for('recipe_list'))

# @app.route('/add_recipe', methods=['POST'])
# def add_recipe():
#     """Add a new recipe to the database."""
    
#     # Ensure user is logged in
#     if 'username' not in session:
#         flash("Please log in to add recipes.", "warning")
#         return redirect(url_for('login'))

#     # Extract form data
#     recipe_id = request.form.get('recipe_id')
#     recipe_name = request.form.get('recipe_name')
#     filter_size = request.form.get('filter_size')
#     filter_code = request.form.get('filter_code')
#     art_no = request.form.get('art_no')
    
#     alu_coil_width = request.form.get('Alu_coil_width')
#     alu_roller_type = request.form.get('Alu_roller_type')
#     spacer = request.form.get('Spacer')
#     motor_speed = request.form.get('Motor_speed')
#     motor_stroke = request.form.get('Motor_stroke')
#     motor_force = request.form.get('Motor_force')
    
#     # Extract POS values (1-9)
#     pos_values = [request.form.get(f'pos{i}', None) for i in range(1, 10)]

#     # Validate required fields
#     required_fields = [recipe_id, recipe_name, filter_size, filter_code, art_no, alu_coil_width, motor_speed, motor_stroke, motor_force]
#     if any(field is None or field.strip() == "" for field in required_fields):
#         flash("All required fields must be filled!", "danger")
#         return redirect(url_for('recipe_list'))

#     conn = get_db_connection()
#     # if not conn:
#     #     flash("Database connection failed.", "danger")
#     #     print("connection failed.")
#     #     return redirect(url_for('recipe_list'))
#     print("Got Connections")
#     try:
#         cursor = conn.cursor()

#         # Insert into `Recipe` table
#         cursor.execute(
#             '''INSERT INTO Recipe (Recipe_ID, Recipe_Name, Filter_Size, Filter_Code, Art_No) 
#                VALUES (?, ?, ?, ?, ?)''',
#             (recipe_id, recipe_name, filter_size, filter_code, art_no)
#         )

#         # Insert into `Recipe_Details1` table
#         cursor.execute(
#             '''INSERT INTO Recipe_Details1 
#                (Recipe_ID, Pos1, Pos2, Pos3, Pos4, Pos5, Pos6, Pos7, Pos8, Pos9, Alu_coil_width, Alu_roller_type, Spacer) 
#                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#             (recipe_id, *pos_values, alu_coil_width, alu_roller_type, spacer)
#         )

#         # Insert into `Sub_Menu` table
#         cursor.execute(
#             '''INSERT INTO Sub_Menu 
#                (Recipe_ID, motor_speed, motor_stroke, other_speed_force, alu_coil_width) 
#                VALUES (?, ?, ?, ?, ?)''',
#             (recipe_id, motor_speed, motor_stroke, motor_force, alu_coil_width)
#         )

#         # Commit changes
#         conn.commit()
#         flash("Recipe added successfully!", "success")

#     except pyodbc.Error as e:
#         flash(f"Database error: {str(e)}", "danger")
#         print(f"Here is the issue: {str(e)}", "danger")

#         conn.rollback()  # Rollback changes on error

#     except Exception as e:
#         flash(f"Unexpected error: {str(e)}", "danger")

#     finally:
#         conn.close()  # Close connection safely

#     return redirect(url_for('recipe_list'))

# def update_plc_with_values(pos_values, submenu_values):
#     """
#     Update PLC with POS values, Recipe ID (assumed as the last element in pos_values), 
#     and submenu values.
#     """
#     from opcua import Client, ua

#     client = Client(ENDPOINT_URL)
#     client.session_timeout = 30000  # Adjust timeout as needed

#     try:
#         client.connect()

#         # Ensure pos_values is a list with at least 10 elements (9 POS values + 1 Recipe ID)
#         if not isinstance(pos_values, list) or len(pos_values) < 10:
#             raise ValueError("pos_values must be a list with at least 10 elements (including Recipe ID).")

#         # Extract Recipe ID (last element)
#         recipe_id = int(pos_values[-1])
#         pos_values = pos_values[:-1]  # Remove Recipe ID from the list, keeping only POS values

#         # Write POS values (1 to 9) to PLC nodes
#         for i in range(1, 10):
#             pos_value = pos_values[i - 1]  # Access by index (0-based for lists)
#             node_id = f'ns=3;s="OpenRecipe"."selectedRoll{i}"'

#             try:
#                 # Get the node object
#                 node = client.get_node(node_id)
#                 # Determine the value to set
#                 node.set_value(ua.DataValue(ua.Variant(bool(pos_value), ua.VariantType.Boolean)))
#             except Exception as node_error:
#                 print(f"Error processing Node ID {node_id}: {node_error}")

#         # Write the Recipe ID to a specific OPC UA node
#         try:
#             recipe_node_id = 'ns=3;s="OpenRecipe"."recipeId"'  # Replace with actual node ID for Recipe ID
#             recipe_node = client.get_node(recipe_node_id)
#             recipe_node.set_value(ua.DataValue(ua.Variant(recipe_id, ua.VariantType.Int32)))
#         except Exception as recipe_error:
#             print(f"Error writing Recipe ID to Node ID {recipe_node_id}: {recipe_error}")
#         submenu_fields = ["servoMotorForce", "servoMotorSpeed", "servoMotorStroke", "coilWidth"]
#         # Write submenu values to specific nodes
#         try:
#          submenu_values = [float(value) for value in submenu_values] 
#         except ValueError as conversion_error:
#          raise ValueError(f"Error converting submenu values to float: {conversion_error}")

#         for field_name, submenu_value in zip(submenu_fields, submenu_values):
#             submenu_node_id = f'ns=3;s="OpenRecipe"."{field_name}"'  # Replace with actual node ID pattern
#             try:
#                 # Get the node object
#                 node = client.get_node(submenu_node_id)
#                 node.set_value(ua.DataValue(ua.Variant(submenu_value, ua.VariantType.Float)))
#             except Exception as submenu_error:
#                 print(f"Error processing Submenu Node ID {submenu_node_id}: {submenu_error}")

#         print("POS values, Recipe ID, and Submenu values written successfully to PLC.")
#     except Exception as e:
#         print(f"Error updating PLC: {e}")
#     finally:
#         client.disconnect() 

# from datetime import datetime
# @app.route('/start_recipe/<int:recipe_id>', methods=['POST'])
# def start_recipe(recipe_id):
#     """ Start a recipe batch and log the process """
#     # Check if user is logged in
    
#     if 'username' not in session:
#         flash("Please log in to start a recipe.", "warning")
#         return redirect(url_for('login'))

#     conn = get_db_connection()
#     if not conn:
#         flash("Database connection failed.", "danger")
#         return redirect(url_for('recipe_list'))
    
#     try:
#         cursor = conn.cursor()
#         print("1")
#         # Fetch Recipe Details
#         cursor.execute("SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?", (recipe_id,))
#         recipe_details = cursor.fetchone()
#         cursor.execute("SELECT * FROM Sub_Menu WHERE Recipe_ID = ?", (recipe_id,))
#         sub_menu = cursor.fetchone()
#         print(sub_menu)
#         if not recipe_details or not sub_menu:
#             flash("Recipe details not found!", "danger")
#             return redirect(url_for('recipe_details', recipe_id=recipe_id))
#         # Extract Position and Submenu Values
#         pos_values = extract_pos_values([recipe_details])
#         submenu_values = extract_submenu_vaues([sub_menu])
#         update_plc_with_values(pos_values, submenu_values)
#         # Get JSON Payload
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Invalid JSON payload"}), 400
#         print("5")
#         quantity = data.get('quantity')
#         if not quantity:
#             return jsonify({"error": "Quantity is required"}), 400
#         print("6")
#         # Generate Batch Code and Timestamp
#         batch_code = f"BATCH-{recipe_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         print("7")
#         # Insert into `Recipe_Log` Table
#         cursor.execute(
#     '''
#     INSERT INTO Recipe_Log 
#     (Batch_Code, Timestamp, Recipe_ID, motor_speed, motor_stroke, 
#     other_speed_force, alu_coil_width, Quantity, Batch_Running_Status, Batch_Completion_Status)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''',
#     (
#         batch_code,
#         timestamp,
#         recipe_id,
#         sub_menu[1],  # motor_speed
#         sub_menu[2],  # motor_stroke
#         sub_menu[3],  # other_speed_force
#         sub_menu[4],  # alu_coil_width
#         quantity,
#         'Running',
#         'Pending'
#     )
# )

       
#         print("8")
#         conn.commit()
#         flash(f"Recipe batch started successfully! Batch Code: {batch_code}", "success")
#         print("9")
#     except pyodbc.Error as e:
#         conn.rollback()  # Rollback changes on error
#         flash(f"Database error: {str(e)}", "danger")
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         flash(f"Unexpected error: {str(e)}", "danger")
#         return jsonify({"error in last": f"Unexpected error: {str(e)}"}), 500

#     finally:
#         conn.close()

#     return jsonify({"message": "Recipe batch started successfully", "batch_code": batch_code})
# # shreyash's new changes 
# @app.route('/addTag', methods=['POST'])
# def add_tag():
#     """ Add a new tag to the database """

#     # Parse JSON Request
#     data = request.get_json()
#     if not data:
#         return jsonify({"success": False, "error": "Invalid JSON payload"}), 400

#     tag_id = data.get("tagId")
#     tag_name = data.get("tagName")
#     tag_address = data.get("tagAddress")
#     plc_id = data.get("plcId")

#     # Validate Required Fields
#     if not all([tag_id, tag_name, tag_address, plc_id]):
#         return jsonify({"success": False, "error": "Missing required fields."}), 400

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"success": False, "error": "Database connection failed."}), 500

#     try:
#         with conn.cursor() as cursor:
#             # Insert the new tag
#             cursor.execute(
#                 '''
#                 INSERT INTO Tag_Table (tagId, tagName, tagAddress, plcId)
#                 VALUES (?, ?, ?, ?)
#                 ''', (tag_id, tag_name, tag_address, plc_id)
#             )
#             conn.commit()

#         # Fetch and update live value for the new tag
#         fetch_and_update_live_value(tag_address)

#         return jsonify({"success": True, "message": "Tag added successfully."}), 201

#     except pyodbc.IntegrityError:
#         return jsonify({"success": False, "error": "TagId already exists."}), 409
#     except pyodbc.Error as e:
#         return jsonify({"success": False, "error": str(e)}), 500
#     finally:
#         conn.close()

# def fetch_and_update_live_value(tag_address):
#     """Fetch live value for a tag and update the Live_Tags table."""
    
#     # Establish database connection
#     conn = get_db_connection()
#     if not conn:
#         print("Failed to connect to database.")
#         return

#     client = Client(ENDPOINT_URL)
#     client.session_timeout = 30000  # Adjust timeout as needed

#     try:
#         client.connect()
#         node = client.get_node(tag_address)
#         value = node.get_value()

#         # Convert the value into a JSON string if necessary
#         if isinstance(value, (list, dict)):
#             value = json.dumps(value)
#         else:
#             value = str(value)

#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         with conn.cursor() as cursor:
#             # Fetch tagId from Tag_Table
#             cursor.execute("SELECT Tagid FROM Tag_Table WHERE tagAddress = ?", (tag_address,))
#             tag_id = cursor.fetchone()

#             if tag_id:
#                 tag_id = tag_id[0]

#                 # Use MERGE statement for upsert (INSERT or UPDATE)
#                 cursor.execute('''
#                     MERGE INTO Live_Tags AS target
#                     USING (SELECT ? AS tagId) AS source
#                     ON target.tagId = source.tagId
#                     WHEN MATCHED THEN
#                         UPDATE SET value = ?, timestamp = ?
#                     WHEN NOT MATCHED THEN
#                         INSERT (value, tagId, timestamp) VALUES (?, ?, ?);
#                 ''', (tag_id, value, timestamp, value, tag_id, timestamp))

#                 conn.commit()

#                 # Emit live data to the frontend via SocketIO
#                 # socketio.emit('liveData', {"success": True, "tagAddress": tag_address, "value": value})

#     except Exception as e:
#         # socketio.emit('liveData', {"success": False, "error": str(e)})
#         print(f"Error fetching and updating live value: {e}")

#     finally:
#         client.disconnect()
#         conn.close()

# def fetch_live_tag_data():
#     """
#     Fetch live tags and their corresponding tag addresses from the database.
#     Returns a list of dictionaries.
#     """
#     conn = get_db_connection()
#     if not conn:
#         return []

#     try:
#         with conn.cursor() as cursor:
#             query = '''
#                 SELECT lt.id, lt.tagId, tt.tagAddress 
#                 FROM Live_Tags lt
#                 LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
#             '''
#             cursor.execute(query)

#             # Fetch results and return as a list of dictionaries
#             columns = [column[0] for column in cursor.description]
#             return [dict(zip(columns, row)) for row in cursor.fetchall()]

#     except pyodbc.Error as e:
#         print(f"Error fetching live tag data: {e}")
#         return []

#     finally:
#         conn.close()
# def read_opcua_values(tag_data): 
#     """
#     Connect to OPC UA server and read values for the given tag addresses.
#     """
#     client = Client(ENDPOINT_URL)
#     client.session_timeout = 30000  # Adjust timeout as needed
#     updates = []

#     try:
#         # print("Connecting to OPC UA server...")
#         client.connect()
#         # print("Connected to OPC UA server!")

#         # Start the overall timing for the entire operation
#         overall_start_time = time.time()

#         for row in tag_data:
#             # print("Processing row:", row)  # Debugging output

#             # Ensure the dictionary contains required keys
#             if not isinstance(row, dict) or not all(k in row for k in ("id", "tagId", "tagAddress")):
#                 # print(f"Invalid row format: {row}, skipping...")
#                 continue

#             live_tag_id = row["id"]          # Extract 'id'
#             tag_id = row["tagId"]            # Extract 'tagId'
#             tag_address = row["tagAddress"]  # Extract 'tagAddress'

#             # print(f"Processing tagId {tag_id} with tagAddress: {tag_address}")

#             if not tag_address:
#                 print(f"No tagAddress found for tagId {tag_id}. Skipping update.")
#                 continue

#             # Start timing for individual tag fetching
#             tag_start_time = time.time()

#             try:
#                 # Fetch the live value from OPC UA server
#                 node = client.get_node(tag_address)
#                 value = node.get_value()

#                 # Calculate individual tag fetching time
#                 tag_end_time = time.time()
#                 tag_elapsed_time = (tag_end_time - tag_start_time) * 1000  # in milliseconds
#                 # print(f"Fetched value {value} for tagId {tag_id}. Time taken: {tag_elapsed_time:.2f} ms.")

#                 # Store the result
#                 updates.append((value, live_tag_id))
#             except Exception as e:
#                 print(f"Error fetching live value for tagId {tag_id}: {e}")

#         # Calculate overall session duration
#         overall_end_time = time.time()
#         overall_elapsed_time = (overall_end_time - overall_start_time) * 1000  # in milliseconds
#         # print(f"Disconnected from OPC UA server. Overall session duration: {overall_elapsed_time:.2f} ms.")

#     finally:
#         client.disconnect()

#     return updates
# def update_database(updates):
#     """
#     Bulk update the Live_Tags table with new live values.
#     Converts lists or dictionaries in 'value' to JSON strings.
#     """
#     if not updates:
#         return

#     updates_serialized = []  # Store serialized updates for Live_Tags
#     consistent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     for value, record_id in updates:
#         if isinstance(value, (list, dict)):
#             value = json.dumps(value)  # Convert list/dict to JSON string
#         else:
#             value = str(value)  # Convert other types to string
        
#         # Prepare data for bulk update
#         updates_serialized.append((value, consistent_timestamp, record_id))

#     # Database operations
#     conn = get_db_connection()
#     if not conn:
#         return

#     try:
#         with conn.cursor() as cursor:
#             cursor.executemany('''
#                 UPDATE Live_Tags
#                 SET value = ?, timestamp = ?
#                 WHERE id = ?
#             ''', updates_serialized)

#             conn.commit()
#             # print(f"✅ {len(updates_serialized)} records updated successfully!")

#     except pyodbc.Error as e:
#         print(f"Error updating Live_Tags: {e}")

#     finally:
#         conn.close()  
# # API_URL = "https://api.ngsmart.in:5000/suvi/api/v1/machine-data"  # Change this to your Flask API URL
# # API_URL = "https://api.ngsmart.in:5000/suvi/api/v1/machine-data"
# API_URL =   "http://localhost:4000/suvi/api/v1/machine-data"
# BATCH_SIZE = 10

# def is_json(value):
#     """
#     Check if a value is a valid JSON.
#     """
#     try:
#         json.loads(value)
#         return True
#     except ValueError:
#         return False
# def process_value(tag_name, value):
#     """
#     Process the value field:
#     - If it's an array, convert each element into a separate field like field1, field2, etc.
#     - If it's not an array, return as-is.
#     """
#     if isinstance(value, list):
#         return {f"{tag_name}{i+1}": v for i, v in enumerate(value)}
#     else:
#         return {tag_name: value}
# def timestamp_to_epoch(timestamp):
#     """
#     Convert timestamp from 'YYYY-MM-DD HH:MM:SS' (string) or datetime.datetime object to epoch seconds.
#     If the timestamp is already in epoch form (integer), return it directly.
#     """
#     try:
#         # If timestamp is an integer (epoch time)
#         if isinstance(timestamp, int):
#             return timestamp
        
#         # If timestamp is a string in 'YYYY-MM-DD HH:MM:SS' format
#         elif isinstance(timestamp, str):
#             # Handle milliseconds if present
#             if '.' in timestamp:
#                 datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
#             else:
#                 datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
#             return int(datetime_obj.timestamp())
        
#         # If timestamp is a datetime.datetime object
#         elif isinstance(timestamp, datetime):
#             return int(timestamp.timestamp())
        
#         # Handle unexpected timestamp types
#         else:
#             print(f"Unexpected timestamp type: {type(timestamp)}")
#             return None
#     except ValueError as e:
#         print(f"Error converting timestamp: {e}")
#         return None
# def get_current_batch_count():
#     """
#     Fetch the current total number of batches from the database.
#     """
#     conn = get_db_connection()
#     if not conn:
#         return 0  # Return 0 if unable to connect to DB

#     try:
#         with conn.cursor() as cursor:
#             cursor.execute('SELECT number_of_batches_created FROM BatchTracker WHERE id = 1')
#             result = cursor.fetchone()
#             return int(result[0]) if result and result[0] is not None else 0

#     except pyodbc.Error as e:
#         print(f"Error fetching batch count: {e}")
#         return 0

#     finally:
#         conn.close()

# def update_batch_count(new_batches):
#     """
#     Add the count of new batches to the existing total and update the database.
#     """
#     conn = get_db_connection()
#     if not conn:
#         return None  # Return None if DB connection fails

#     try:
#         with conn.cursor() as cursor:
#             # Fetch the current batch count
#             cursor.execute('SELECT number_of_batches_created FROM BatchTracker WHERE id = 1')
#             result = cursor.fetchone()
#             current_count = int(result[0]) if result and result[0] is not None else 0

#             # print(f"Current batch count: {current_count}")

#             # Calculate updated count
#             updated_count = current_count + new_batches

#             # Update the database with the new count
#             cursor.execute('UPDATE BatchTracker SET number_of_batches_created = ? WHERE id = 1', (updated_count,))
#             conn.commit()

#             # print(f"Updated batch count: {updated_count}")
#             return updated_count

#     except pyodbc.Error as e:
#         print(f"Error updating batch count: {e}")
#         return None

#     finally:
#         conn.close()

# def clean_live_log_last_batch(record_ids, chunk_size=500):
#     """
#     Clean up successfully uploaded records from MSSQL in chunks to avoid parameter limit errors.
#     """
#     conn = get_db_connection()
#     if not conn:
#         return False  # Return False if DB connection fails

#     try:
#         cursor = conn.cursor()

#         # Process deletions in chunks
#         for i in range(0, len(record_ids), chunk_size):
#             chunk = record_ids[i:i + chunk_size]
            
#             # Create dynamic placeholders
#             placeholders = ', '.join(['?'] * len(chunk))
#             query = f'DELETE FROM Live_Log WHERE id IN ({placeholders})'

#             # Execute batch delete
#             cursor.execute(query, chunk)
#             conn.commit()

#         print("✅ Successfully cleaned up uploaded records from MSSQL.")
#         return True

#     except pyodbc.Error as e:
#         print(f"❌ Error during cleanup: {e}")
#         return False

#     finally:
#         conn.close()

# def fetch_plc_info():
#     """Fetch plcId and serialKey from Plc_Table in MSSQL."""
#     conn = get_db_connection()
#     if not conn:
#         return None, None  # Return None if DB connection fails

#     try:
#         cursor = conn.cursor()

#         # Use "TOP 1" instead of "LIMIT 1" for MSSQL
#         cursor.execute("SELECT TOP 1 plcId, serial_Key FROM Plc_Table")
#         plc_info = cursor.fetchone()

#         return plc_info if plc_info else (None, None)

#     except pyodbc.Error as e:
#         print(f"❌ Error fetching PLC info: {e}")
#         return None, None

#     finally:
#         conn.close()  # Ensure the connection is closed

# def upload_live_log_to_mongodb():
#     """
#     Fetch records from MSSQL, format them, send them to Flask API, and clean up MSSQL.
#     """
#     try:
#         # Fetch plcId and serialKey from Plc_Table
#         plc_id, serial_key = fetch_plc_info()
#         if plc_id is None or serial_key is None:
#             print("❌ Error: plcId or serialKey not found in Plc_Table.")
#             return

#         # Connect to MSSQL
#         conn = get_db_connection()
#         if not conn:
#             return

#         try:
#             cursor = conn.cursor()

#             # Fetch all records grouped by timestamp
#             cursor.execute('''
#                 SELECT id, tagName, value, timestamp
#                 FROM Live_Log
#                 ORDER BY timestamp ASC, id ASC
#             ''')
#             records = cursor.fetchall()

#             if not records:
#                 print("✅ No records to upload.")
#                 return

#             # Group records by timestamp
#             grouped_data = {}
#             record_ids = []

#             for record in records:
#                 record_id, tag_name, value, timestamp = record

#                 # Convert timestamp to epoch format
#                 epoch_timestamp = timestamp_to_epoch(timestamp)
#                 if epoch_timestamp is None:
#                     continue  # Skip if timestamp conversion failed

#                 # Parse value if it's JSON
#                 parsed_value = json.loads(value) if is_json(value) else value

#                 # Process value to split arrays into separate fields
#                 processed_data = process_value(tag_name, parsed_value)

#                 if epoch_timestamp not in grouped_data:
#                     grouped_data[epoch_timestamp] = []
#                 grouped_data[epoch_timestamp].append(processed_data)

#                 # Collect record IDs for cleanup
#                 record_ids.append(record_id)

#             # Prepare the batch format
#             batches = []
#             for epoch_timestamp, tags in grouped_data.items():
#                 # Combine all tags for the same timestamp into one dictionary
#                 combined_tags = {}
#                 for tag in tags:
#                     combined_tags.update(tag)

#                 batch = {
#                     "plcId": plc_id,
#                     "serialNo": serial_key,
#                     "values": [{
#                         "dbId": 3,
#                         "dbNo": 1001,
#                         "dbName": "dbCloud",
#                         "data": [{
#                             "temp": 1,
#                             "timeStamp": epoch_timestamp * 1000,
#                             **combined_tags
#                         }]
#                     }]
#                 }
#                 batches.append(batch)

#             successful_batches = 0

#             # Send data in batches of 10
#             for i in range(0, len(batches), BATCH_SIZE):
#                 batch_to_send = batches[i:i + BATCH_SIZE]

#                 response = requests.post(API_URL, json=batch_to_send)

#                 if response.status_code in [200, 201]:
#                     print(f"✅ Batch {i // BATCH_SIZE + 1} uploaded successfully.")
#                     successful_batches += 1

#                     # Clean up uploaded records
#                     clean_live_log_last_batch(record_ids, chunk_size=500)
#                 else:
#                     print(f"❌ Failed to upload batch {i // BATCH_SIZE + 1}. Status code: {response.status_code}")
#                     print(f"Response: {response.text}")

#             # Update batch count in MSSQL
#             update_batch_count(successful_batches)
#             print("✅ Process completed.")

#         except pyodbc.Error as e:
#             print(f"❌ Database query error: {e}")

#         finally:
#             conn.close()  # Ensure the connection is closed

#     except Exception as e:
#         print(f"❌ Error: {e}")

# def schedule_live_log_upload_background(interval=100000):
#     """
#     Run the upload function in a background thread every `interval` milliseconds.
#     """
#     def background_task():
#         while True:
#             try:
#                 conn = get_db_connection()
#                 if not conn:
#                     print("❌ Skipping task due to DB connection failure.")
#                     time.sleep(interval / 1000)
#                     continue

#                 try:
#                     cursor = conn.cursor()
#                     cursor.execute("SELECT COUNT(*) FROM Live_Log")
#                     count = cursor.fetchone()[0]

#                     if count > 1000:
#                         print("📢 More than 1000 records found. Uploading...")
#                         upload_live_log_to_mongodb()
#                     else:
#                         print("ℹ️ Less than 1000 records in Live_Log. Skipping upload...")

#                 except pyodbc.Error as e:
#                     print(f"❌ Error executing query: {e}")

#                 finally:
#                     conn.close()  # Ensure connection is closed properly

#             except Exception as e:
#                 print(f"❌ Error in background task: {e}")

#             time.sleep(interval / 1000)  # Wait before the next check

#     # Start the background task in a separate daemon thread
#     thread = threading.Thread(target=background_task, daemon=True)
#     thread.start()

# # Call this function to start the background thread
# # schedule_live_log_upload_background(interval=15000)

# def update_all_live_tags():
#     """
#     Fetch all entries from Live_Tags, resolve tagAddress from Tag_Table, and update live values.
#     """
#     try:
#         # Step 1: Fetch data from the database
#         tag_data = fetch_live_tag_data()

#         # Step 2: Read values from OPC UA
#         updates = read_opcua_values(tag_data)

#         # Step 3: Update the database
#         update_database(updates)

#     except Exception as e:
#         print(f"Error: {e}")
#         # Global variable to store the user-defined interval (in seconds)

# def update_all_live_tags_to_log():
#     """
#     Insert values into Live_Log table based on user-defined interval.
#     """
#     try:
#         # Fetch the latest live tag data
#         tag_data = fetch_live_tag_data()

#         # Read values from OPC UA
#         updates = read_opcua_values(tag_data)

#         # Generate a single consistent timestamp for all records
#         consistent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Prepare live log entries
#         live_log_entries = []
#         for value, record_id in updates:
#             if isinstance(value, (list, dict)):
#                 value = json.dumps(value)  # Convert list/dict to JSON string
#             else:
#                 value = str(value)  # Convert other types to string
#             live_log_entries.append((value, consistent_timestamp, record_id))

#         # Insert into Live_Log table
#         conn = get_db_connection()
#         if not conn:
#             print("❌ Database connection failed. Skipping update.")
#             return

#         try:
#             cursor = conn.cursor()
            
#             sql_query = '''
#                 INSERT INTO Live_Log (tagId, tagName, value, timestamp)
#                 SELECT lt.tagId, tt.tagName, ?, ?
#                 FROM Live_Tags lt
#                 LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
#                 WHERE lt.id = ?
#             '''
            
#             cursor.executemany(sql_query, live_log_entries)  # Batch insert for efficiency
#             conn.commit()
#             print(f"✅ {len(live_log_entries)} records inserted into Live_Log successfully.")

#         except pyodbc.Error as e:
#             print(f"❌ SQL Execution Error: {e}")

#         finally:
#             conn.close()  # Ensure connection is closed properly

#     except Exception as e:
#         print(f"❌ Error in update_all_live_tags_to_log: {e}")

# @app.route('/writeValue', methods=['POST'])
# def write_value():
#     data = request.json
#     print("Received Data:", data)  # This will print the data to the console
#     node_id = data.get("nodeId")
#     value = data.get("value")

#     if not node_id or value is None:
#         return jsonify({"success": False, "error": "Missing nodeId or value in the request."})

#     try:
#         # Connect to the OPC UA server
#         client = Client(ENDPOINT_URL)
#         client.session_timeout = 30000  # Adjust timeout as needed
#         client.connect()

#         # Get the node object
#         node = client.get_node(node_id)
#         print("Received node:", node)  # This will print the data to the console

#         # Fetch the DataType of the node
#         data_type = node.get_data_type_as_variant_type()
#         # print("Received datatype:", data_type)  # This will print the data to the console
#         if not data_type:
#             raise Exception(f"Could not fetch DataType for NodeId: {node_id}")

#         # print(f"Fetched DataType: {data_type}")

#         # Wrap the value in a ua.Variant object with the correct DataType
#          # Wrap the value in a ua.Variant object with the correct DataType
#         variant = ua.DataValue(ua.Variant(value, data_type))

#         # Perform the write operation
#         node.set_value(variant)
       
#         # Disconnect from the client
#         client.disconnect()

#         return jsonify({"success": True, "message": f"Value written successfully to NodeId: {node_id}"})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})


# @app.route('/readValues', methods=['GET'])
# def read_values():
#     try:
#         # Connect to SQL Database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"})

#         cursor = conn.cursor()

#         # Fetch node IDs and their corresponding tag names
#         cursor.execute("SELECT DISTINCT tagAddress, tagName FROM Tag_Table")  # Include tagName
#         tag_data = cursor.fetchall()

#         if not tag_data:
#             conn.close()
#             return jsonify({"success": False, "error": "No tag data found in the database"})

#         # Connect to the PLC
#         client = Client(ENDPOINT_URL)
#         client.session_timeout = 30000  # Adjust timeout as needed
#         client.connect()

#         results = []
#         for tag_address, tag_name in tag_data:
#             try:
#                 node = client.get_node(tag_address)
#                 value = node.get_value()
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
#                 results.append({"nodeId": tag_address, "tagName": tag_name, "value": value, "timestamp": timestamp})
#             except Exception as e:
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 results.append({"nodeId": tag_address, "tagName": tag_name, "error": str(e), "timestamp": timestamp})

#         # Disconnect client & close DB connection
#         client.disconnect()
#         conn.close()

#         return jsonify({"success": True, "results": results})

#     except pyodbc.Error as db_error:
#         return jsonify({"success": False, "error": f"Database error: {str(db_error)}"})

#     except Exception as e:
#         return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})
# def read_live_values(node_ids):
#     """Connect to OPC UA server and emit live data to the frontend."""
#     client = Client(ENDPOINT_URL)
#     client.session_timeout = 30000  # Adjust timeout as needed
#     try:
#         # print("Attempting to connect to OPC UA server...")
#         client.connect()
#         # print("Connected to OPC UA server!")

#         while True:
#             results = []
#             # print("Fetching data for node IDs:", node_ids)  # Debug node IDs
#             for node_id in node_ids:
#                 try:
#                     # print(f"Reading value for node ID: {node_id}")  # Log node ID
#                     node = client.get_node(node_id)
#                     value = node.get_value()
#                     # print(f"Value for node {node_id}: {value}")  # Log fetched value
#                     results.append({"nodeId": node_id, "value": value})
#                 except Exception as e:
#                     print(f"Error reading node {node_id}: {e}")  # Log errors
#                     results.append({"nodeId": node_id, "error": str(e)})

#             # print("Emitting data to frontend:", results)  # Debug emitted data
#             # socketio.emit('liveData', {"success": True, "results": results})
#             time.sleep(1)  # Fetch data every 2 seconds
#     except Exception as e:
#         print(f"Error in OPC UA connection: {e}")  # Log connection errors
#         # socketio.emit('liveData', {"success": False, "error": str(e)})
#     finally:
#         client.disconnect()
#         # print("Disconnected from OPC UA server!")  # Debug disconnection


# @app.route('/getLiveValues', methods=['GET'])
# def get_live_values():
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed"})

#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT Live_Tags.Id, Live_Tags.value, Live_Tags.timestamp, Tag_Table.tagName
#             FROM Live_Tags
#             INNER JOIN Tag_Table ON Live_Tags.tagId = Tag_Table.tagId
#         ''')

#         live_values = cursor.fetchall()
        
#         results = [{"tagName": row.tagName, "value": row.value, "timestamp": row.timestamp} for row in live_values]

#         conn.close()
#         return jsonify({"success": True, "data": results})

#     except pyodbc.Error as db_error:
#         return jsonify({"success": False, "error": f"Database error: {str(db_error)}"})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})

# @app.route('/startLiveRead', methods=['POST'])
# def start_live_read():
#     """API endpoint to initiate live data reading."""
#     data = request.json
#     print("Received request to start live reading:", data)  # Log request data

#     node_ids = data.get("nodeIds", [])
#     if not node_ids:
#         print("No node IDs provided in request!")  # Log missing node IDs
#         return jsonify({"success": False, "message": "No node IDs provided"}), 400

#     print("Starting live reading for node IDs:", node_ids)  # Log starting point
#     # Start the live reading thread
#     thread = threading.Thread(target=read_live_values, args=(node_ids,))
#     thread.daemon = True  # Ensures thread stops when the main app stops
#     thread.start()

#     return jsonify({"success": True, "message": "Live data reading started"})

# @app.route('/get_recipe', methods=['GET'])
# def get_recipe():
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"success": False, "message": "Database connection failed"})

#     recipe_id = request.args.get('recipe_id')

#     print("📌 Recipe ID received:", recipe_id)  # Debug log

#     if not recipe_id:
#         return jsonify({"success": False, "message": "Recipe ID is required"})

#     try:
#         cursor = conn.cursor()

#         # Fetch data from the Recipe table
#         cursor.execute("SELECT * FROM Recipe WHERE recipe_id = ?", (recipe_id,))
#         recipe_main = cursor.fetchone()
#         # print("recipe_main: ",recipe_main)
#         if not recipe_main:
#             return jsonify({"success": False, "message": "Recipe not found"})

#                # Extract column names
#         columns = [column[0] for column in cursor.description]

#         # Convert `recipe_main` tuple to a dictionary
#         recipe_main_dict = dict(zip(columns, recipe_main))
#         print("recipe_main_dict: ",recipe_main_dict)

#         # Fetch data from Recipe_Details1 (contains Spacer & Alu_roller_type)
#         cursor.execute("SELECT * FROM Recipe_Details1 WHERE recipe_id = ?", (recipe_id,))
#         recipe_pos = cursor.fetchall()
#         recipe_pos_list = [{column[0]: value for column, value in zip(cursor.description, row)} for row in recipe_pos]
#         print("📌 Fetched Recipe Positions:", recipe_pos_list)  # Debug log

#         # Fetch data from Sub_Menu (contains motor-related details)
#         cursor.execute("SELECT * FROM Sub_Menu WHERE recipe_id = ?", (recipe_id,))
#         recipe_motor = cursor.fetchone()
#         recipe_motor_dict = {column[0]: value for column, value in zip(cursor.description, recipe_motor)} if recipe_motor else {}

#         # Build the response data
#         data = {
#            "recipe_id": recipe_main_dict.get("Recipe_ID"),
#            "recipe_name": recipe_main_dict.get("Recipe_Name"),
#            "filter_size": recipe_main_dict.get("Filter_Size"),
#            "filter_code": recipe_main_dict.get("Filter_Code"),
#             "art_no": recipe_main_dict.get("Art_No"),
#             "Alu_coil_width": recipe_motor_dict.get("alu_coil_width", ""),
#             "Alu_roller_type": "",  # Default, will be overwritten
#             "Spacer": "",  # Default, will be overwritten
#             "Motor_speed": recipe_motor_dict.get("motor_speed", ""),
#             "Motor_stroke": recipe_motor_dict.get("motor_stroke", ""),
#             "Motor_force": recipe_motor_dict.get("other_speed_force", ""),
#         }

#         # Overwrite Alu_roller_type and Spacer from `recipe_pos` table
#         for pos in recipe_pos_list:
#             data["Alu_roller_type"] = pos.get("Alu_roller_type", "")
#             data["Spacer"] = pos.get("Spacer", "")

#             # Add positions dynamically
#             for i in range(1, 10):  # Pos1 to Pos9
#                 pos_key = f"Pos{i}"
#                 if pos_key in pos:
#                     data[pos_key] = pos[pos_key]

#         print("📌 Final response data:", data)  # Debug log

#         return jsonify({"success": True, **data})

#     except pyodbc.Error as db_error:
#         print(f"❌ Database error: {db_error}")  # Debug log
#         return jsonify({"success": False, "message": f"Database error: {str(db_error)}"})

#     except Exception as e:
#         print(f"❌ Unexpected error: {e}")  # Debug log
#         return jsonify({"success": False, "message": str(e)})

#     finally:
#         conn.close()  # Ensure the connection is closed

# @app.route('/get_last_plc_values', methods=['GET'])
# def get_last_plc_values():
#     client = Client(ENDPOINT_URL)  # OPC UA client
#     try:
#         # Connect to OPC UA server
#         client.connect()
#         # Fetch values for the given Node IDs
#         coil_Width = client.get_node('ns=3;s="OpenRecipe"."coilWidth"').get_value()
#         motor_force = client.get_node('ns=3;s="OpenRecipe"."servoMotorForce"').get_value()
#         motor_stroke = client.get_node('ns=3;s="OpenRecipe"."servoMotorStroke"').get_value()
#         motor_speed = client.get_node('ns=3;s="OpenRecipe"."servoMotorSpeed"').get_value()

#         # Build response
#         last_plc_values = {
#             "Motor_speed": str(motor_speed),
#             "Motor_stroke": str(motor_stroke),
#             "Motor_force": str(motor_force),
#             "coil_Width":  str(coil_Width)
#         }
#         return jsonify(last_plc_values)

#     except Exception as e:
#         print("Error fetching PLC values:", e)
#         return jsonify({"error": "Failed to fetch PLC values"}), 500
#     finally:
#         client.disconnect()
#         print("Disconnected from OPC UA Server")

# def run_periodic_update1():
#     while True:
        
#         update_all_live_tags()
        
#         time.sleep(1)  # Update every 1 seconds
# # Initialize the default update interval
# update_interval = 20
# interval_lock = threading.Lock()

# @app.route('/api/update_interval_time', methods=['POST'])
# def update_interval_time():
#     global update_interval

#     try:
#         # Get the intervalTime value from the request body
#         data = request.json
#         interval_time = data.get('intervalTime')

#         if not interval_time or interval_time <= 0:
#             return jsonify({"success": False, "error": "Invalid interval time provided."})

#         # Update the intervalTime value in the MSSQL database
#         conn = get_db_connection()
#         if not conn:
#             return jsonify({"success": False, "error": "Database connection failed."})
        
#         try:
#             cursor = conn.cursor()
#             cursor.execute("UPDATE Plc_Table SET intervalTime = ? WHERE plcId = 1", (interval_time,))
#             conn.commit()
#         except pyodbc.Error as db_error:
#             print(f"❌ Database error: {db_error}")
#             return jsonify({"success": False, "error": "Database update failed."})
#         finally:
#             conn.close()
        
#         # Safely update the global update_interval value
#         with interval_lock:
#             update_interval = interval_time

#         return jsonify({"success": True, "message": "Interval time updated successfully."})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})

# def run_periodic_update3():
#     global update_interval

#     while True:
#         # Perform the periodic update task
#         update_all_live_tags_to_log()  # Insert data into Live_Log after the interval

#         # Safely access the update_interval value
#         with interval_lock:
#             # print("Interval time:",update_interval)
#             sleep_time = update_interval

#         time.sleep(sleep_time)  # Sleep for the specified interval
#  # Sleep for the specified interval 
# def run_periodic_update2():
#     while True:
        
#         update_batch_status()
        
#         time.sleep(1)  # Update every 1 seconds
        
# if __name__ == '__main__':
#     print("Starting Flask app...")
#     schedule_live_log_upload_background(interval=10000)
#     threading.Thread(target=run_periodic_update1, daemon=True).start()
#     threading.Thread(target=run_periodic_update2, daemon=True).start()
#     threading.Thread(target=run_periodic_update3, daemon=True).start()
#     threading.Thread(target=log_status, daemon=True).start()
#     # socketio.run(app, host='0.0.0.0', port=5000)
#     app.run(debug=True)


from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/assign_tray_to_pick_list', methods=['POST'])
def assign_tray_to_pick_list():
    try:
        # Get the JSON payload from the request
        data = request.get_json()

        # Validate that required fields exist
        if not data or "TrayCode" not in data or "Sensor_id" not in data:
            return jsonify({"error": "Invalid request, missing required fields"}), 400

        # Return the expected response
        response_data = [
            {
                "Ground": "2,3,5",
                "Mezzanine": "null",
                "Status": "Success",
                "message": "",
                "pl_no": "24443223021000"
            }
        ]
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
