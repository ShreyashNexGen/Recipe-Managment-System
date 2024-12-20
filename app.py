from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
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
from bson import json_util
from pymongo import MongoClient
from flask_cors import CORS
app = Flask(__name__)
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow connections from any origin
# OPC UA connection options
ENDPOINT_URL = "opc.tcp://192.168.0.1:4840"

# SQLite database setup
# Secret key for session encryption
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout
DB_PATH = 'a2z_database.db'
DB_PATH1 = 'suvi_database.db'
MONGO_URI = "mongodb://localhost:27017"  # MongoDB URI
MONGO_DB_NAME = "suvi_flask_db"          # MongoDB Database Name
MONGO_COLLECTION_NAME = "suvi_flask"       # MongoDB Collection Name      # MongoDB Collection Name
# Function to browser
def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DB_PATH1) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tag_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tagId TEXT UNIQUE NOT NULL,
                tagName TEXT UNIQUE NOT NULL,
                tagAddress TEXT NOT NULL,
                plcId TEXT NOT NULL
            )
        ''')
         # Create Live_Tags table to store continuously updated tag values
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Live_Tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tagId TEXT NOT NULL,
                value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tagId) REFERENCES Tag_Table(tagId)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Live_Log (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
              tagId TEXT NOT NULL,
              value TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
            )
        ''')
        


        
        
        conn.commit()


# Hardcoded user data for simplicity 
USER_DATA = {
    'username': 'admin',
    'password_hash': generate_password_hash('password123')  # Secure hashed password
}

def get_db_connection():
    try:
        conn = sqlite3.connect('RMS.db')
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
    pos_values = [row[0] for row in conn.execute("SELECT DISTINCT Pos_Values FROM Pos_Options").fetchall()]

    # Calculate total pages
    total_count = conn.execute('SELECT COUNT(*) FROM Recipe').fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page

    conn.close()

    return render_template(
        'dashboard.html',
    )

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route('/recipe')
def recipe_list():
    # Logic for listing recipes
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    recipes = conn.execute(
        'SELECT * FROM Recipe LIMIT ? OFFSET ?', (per_page, offset)
    ).fetchall()
    pos_values = [row[0] for row in conn.execute("SELECT DISTINCT Pos_Values FROM Pos_Options").fetchall()]
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
                conn.execute(
                    '''
                    UPDATE Recipe_Log
                    SET Batch_Running_Status = ?, Batch_Completion_Status = ?
                    WHERE Batch_Code = ?
                    ''',
                    (running_status, completion_status, batch_code)
                )
                conn.commit()
        except Exception as e:
            print(f"Error updating batch status: {e}")
        finally:
            client.disconnect()
            conn.close()

        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:  # Redirect logged-in users
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USER_DATA['username'] and check_password_hash(USER_DATA['password_hash'], password):
            session['username'] = username  # Create session
            session.permanent = True  # Set session timeout
            flash("Login successful!", 'success')
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials, please try again.", 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear session
    flash("Logged out successfully.", 'info')
    return redirect(url_for('login'))



@app.route('/tag-overview')
def tag_overview():
    # Get the page and limit parameters from the query string
    current_page = int(request.args.get('page', 1))  # Default to page 1 if not provided
    limit = int(request.args.get('limit', 10))  # Default limit is 10 if not provided
    
    # Database connection
    conn = sqlite3.connect(DB_PATH1)
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
        conn = sqlite3.connect(DB_PATH1)
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
        conn = sqlite3.connect(DB_PATH1)  # Make sure we're connecting to the right database
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



@app.route('/live-tag')
def live_tag():
    # Get the current page from the query string (default to 1)
    current_page = int(request.args.get('page', 1))

    # Connect to the database
    conn = sqlite3.connect('a2z_database.db')
    conn.row_factory = sqlite3.Row  # Rows are returned as dictionaries
    cursor = conn.cursor()

    # Pagination setup: 10 items per page
    items_per_page = 10
    offset = (current_page - 1) * items_per_page

    # Fetch data for the current page
    cursor.execute('SELECT * FROM Live_Tags LIMIT ? OFFSET ?', (items_per_page, offset))
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
    # Connect to the database
    conn = sqlite3.connect('a2z_database.db')
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
    


@app.route('/raw-material', methods=['GET', 'POST'])
def raw_material():
    # Handle POST request for adding a new material
    if request.method == 'POST':
        try:
            material_id = request.form['material_Id']
            type_code = request.form['typeCode']
            lot_no = request.form['lotNo']
            material_type = request.form['materialType']
            make = request.form.get('make', '')  # Optional
            user = request.form.get('user', '')  # Optional
            barcode = request.form.get('barcode', '')  # Optional

            # Connect to the database
            conn = sqlite3.connect('a2z_database.db')
            cursor = conn.cursor()

            # Insert into the database
            cursor.execute("""
                INSERT INTO Raw_Materials (material_Id, typeCode, lotNo, make, user, materialType, barcode) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                (material_id, type_code, lot_no, make, user, material_type, barcode))
            conn.commit()
            conn.close()

            # Return a proper success response
            return jsonify({"success": True, "message": "Material added successfully!"})

        except Exception as e:
            # Print the error for debugging
            print(f"Error: {e}")
            return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})

    # Handle GET request to display the raw materials
    current_page = int(request.args.get('page', 1))  # Default to page 1 if not provided
    limit = int(request.args.get('limit', 10))  # Get limit from URL parameter (default 10)
    conn = sqlite3.connect('a2z_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pagination setup
    offset = (current_page - 1) * limit

    # Fetch data for the current page based on the limit
    cursor.execute('SELECT * FROM Raw_Materials LIMIT ? OFFSET ?', (limit, offset))
    raw_materials = cursor.fetchall()

    # Calculate total pages
    cursor.execute('SELECT COUNT(*) FROM Raw_Materials')
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows + limit - 1) // limit  # Calculate total pages based on limit

    conn.close()

    # Render the template with the raw material data
    return render_template(
        'raw_material.html',
        raw_materials=raw_materials,
        page=current_page,
        total_pages=total_pages,
        limit=limit  # Pass the selected limit to the template
    )

@app.route('/delete-raw-material/<int:raw_material_id>', methods=['DELETE'])
def delete_raw_material(raw_material_id):
    try:
        print(f"Attempting to delete raw material with ID: {raw_material_id}")

        # Check if user is logged in
        if 'username' not in session:
            print("Unauthorized access attempt.")
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Connect to the SQLite database
        conn = sqlite3.connect('a2z_database.db')
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
    data = request.json
    typecode = data.get("typeCode")
    lotNo = data.get("lotNo")
    make = data.get("make")
    user = data.get("user")
    materialType = data.get("materialType")
    barcode = data.get("barcode")

    if not typecode or not lotNo or not make or not user or not materialType or not barcode:
        return jsonify({"success": False, "error": "Missing fields in the request."})

    try:
        # Connect to the database and update the record
        with sqlite3.connect('a2z_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Raw_Materials
                SET typeCode = ?, lotNo = ?, make = ?, user = ?, materialType = ?, barcode = ?
                WHERE material_Id = ?
            ''', (typecode, lotNo, make, user, materialType, material_Id,barcode))
            conn.commit()

            return jsonify({"success": True, "message": "Raw material updated successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/delete-recipe/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    try:
        # Debugging: Check if session contains username
        if 'username' not in session:
            print("Session does not contain 'username'. Current session:", session)
            return jsonify({"success": False, "error": "Unauthorized access"}), 401
        
        # Database connection and deletion logic
        conn = sqlite3.connect('RMS.db')
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
   
    try:
        pos_values = extract_pos_values(recipe_details)
        barcode_value = "S3"  # Replace this with actual logic to fetch the barcode value
        # print (dict(recipe_details));
        # print("Values from subtable: ",pos_values)
        update_plc_with_pos_values(pos_values)
        flash(f"POS values written to PLC successfully for Recipe ID {recipe_id}.", "success")
    except Exception as e:
        flash(f"Error writing POS values: {e}", "danger")

    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    conn.close()

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


def update_plc_with_pos_values(pos_values):
    """
    Update PLC with POS values and Recipe ID (assumed as the last element in pos_values).
    """
    client = Client(ENDPOINT_URL)
    client.session_timeout = 30000  # Adjust timeout as needed
    
    try:
        client.connect()
        # Ensure pos_values is a list with at least 10 elements (9 POS values + 1 Recipe ID)
        # if not isinstance(pos_values, list) or len(pos_values) < 10:
        #     raise ValueError("pos_values must be a list with at least 10 elements (including Recipe ID).")

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
                if pos_value:  # Check if the value is present (not None or empty)
                    node.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                   
                else:
                    node.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                   

            except Exception as node_error:
                print(f"Error processing Node ID {node_id}: {node_error}")

        # Write the Recipe ID to a specific OPC UA node
        try:
            recipe_node_id = 'ns=3;s="OpenRecipe"."recipeId"'  # Replace with actual node ID for Recipe ID
            recipe_node = client.get_node(recipe_node_id)
           

            recipe_node.set_value(ua.DataValue(ua.Variant(recipe_id, ua.VariantType.Int32)))
           

        except Exception as recipe_error:
            print(f"Error writing Recipe ID to Node ID {recipe_node_id}: {recipe_error}")

    
       
        client.disconnect()
      
    except Exception as e:
        print(f"Error updating PLC: {e}")

@app.route('/start_recipe/<int:recipe_id>', methods=['POST'])
def start_recipe(recipe_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    recipe_details = conn.execute('SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    
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
        with sqlite3.connect(DB_PATH1) as conn:
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
        # Fetch the tagId from the Tag_Table for this tagAddress
        with sqlite3.connect(DB_PATH1) as conn:
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
                    cursor.execute('''UPDATE Live_Tags SET value = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?''',
                                   (value, existing_entry[0]))
                else:
                    # Insert the new value into Live_Tags table
                    cursor.execute('''INSERT INTO Live_Tags (value, tagId, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)''',
                                   (value, tag_id))

                conn.commit()

        # Emit live data to the frontend via SocketIO
        socketio.emit('liveData', {"success": True, "tagAddress": tag_address, "value": value})

    except Exception as e:
        socketio.emit('liveData', {"success": False, "error": str(e)})

    finally:
        client.disconnect()

def fetch_live_tag_data():
    """
    Fetch live tags and their corresponding tag addresses from the database.
    """
    with sqlite3.connect(DB_PATH1) as conn:
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

import json

def update_database(updates):
    """
    Update the Live_Tags table with the new live values.
    Insert the updated values into the Live_Log table as a historical record.
    Include the tagName in the Live_Log entry.
    Convert lists or dictionaries in 'value' to JSON strings.
    """
    updates_serialized = []  # To store serialized updates for Live_Tags
    live_log_entries = []    # To store entries for the Live_Log table

    for value, record_id in updates:
        if isinstance(value, (list, dict)):
            value = json.dumps(value)  # Convert list/dict to JSON string
        else:
            value = str(value)  # Convert other types to string
        
        # Prepare for Live_Tags update
        updates_serialized.append((value, record_id))

        # Prepare for Live_Log insert (fetch tagId dynamically)
        live_log_entries.append((record_id, value))

    # Database operations
    with sqlite3.connect(DB_PATH1) as conn:
        cursor = conn.cursor()

        # 1. Update the Live_Tags table
        cursor.executemany('''
            UPDATE Live_Tags
            SET value = ?, timestamp = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', updates_serialized)

        # 2. Insert into Live_Log table (fetch tagId and tagName using record_id)
        for record_id, value in live_log_entries:
            cursor.execute('''
                INSERT INTO Live_Log (tagId, tagName, value, timestamp)
                SELECT lt.tagId, tt.tagName, ?, CURRENT_TIMESTAMP
                FROM Live_Tags lt
                LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
                WHERE lt.id = ?
            ''', (value, record_id))

        conn.commit()
      

API_URL = "http://localhost:4000/suvi/api/v1/machine-data"  # Change this to your Flask API URL

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

def clean_live_log_last_100(conn, record_ids):
    """
    Clean up successfully uploaded records from SQLite.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            DELETE FROM Live_Log
            WHERE id IN ({','.join(['?'] * len(record_ids))})
        ''', record_ids)
        conn.commit()
        print("Successfully cleaned up uploaded records from SQLite.")
    except Exception as e:
        print(f"Error cleaning records: {e}")

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

def upload_live_log_to_mongodb():
    """
    Fetch records from SQLite, format them, send them to Flask API, and clean up SQLite.
    """
    try:
        # Connect to SQLite
        with sqlite3.connect(DB_PATH1) as conn:
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
                    "plcId": 3,
                    "serialNo": 11223344,
                    "values": [{"dbId": 2,"dbNo":1001,"dbName":"dbCloud", "data": [{"temp":1,"timestamp": epoch_timestamp*1000, **combined_tags}]}]
                }
                batches.append(batch)

            # Send data in batches of 10
            for i in range(0, len(batches), BATCH_SIZE):
                batch_to_send = batches[i:i + BATCH_SIZE]

                response = requests.post(API_URL, json=batch_to_send)

                if response.status_code in [200, 201]:
                    print(f"Batch {i // BATCH_SIZE + 1} uploaded successfully.")
                    # Clean up uploaded records
                    clean_live_log_last_100(conn, record_ids)
                else:
                    print(f"Failed to upload batch {i // BATCH_SIZE + 1}. Status code: {response.status_code}")
                    print(f"Response: {response.text}")

        print("Process completed.")
        print(f"Response from final API (Batch {i // BATCH_SIZE + 1}): {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error: {e}")

def schedule_live_log_upload_background(interval=15):
    """
    Run the upload function in a background thread every `interval` seconds.
    """
    def background_task():
        while True:
            try:
                with sqlite3.connect(DB_PATH1) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''SELECT COUNT(*) FROM Live_Log''')
                    count = cursor.fetchone()[0]

                    if count > 1000:
                        upload_live_log_to_mongodb()
                    else:
                        print("Less than 1000 records in Live_Log. Skipping upload...")
            except Exception as e:
                print(f"Error in background task: {e}")
            time.sleep(interval)  # Wait before the next check

    # Start the background task in a separate thread
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()

# Call this function to start the background thread
schedule_live_log_upload_background(interval=15)
# Connect to MongoDB
# mongo_client = MongoClient(MONGO_URI)
# mongo_db = mongo_client[MONGO_DB_NAME]
# mongo_collection = mongo_db[MONGO_COLLECTION_NAME]

# @app.route('/upload_data', methods=['POST'])
# def upload_data():
#     try:
#         # Get the JSON data from the request
#         data = request.get_json()
        
#         if not data:
#             return jsonify({"message": "No data received"}), 400

#         # Forward the data to the final API
#         response = requests.post(
#             'http://localhost:4000/suvi/api/v1/machine-data',
#             json=data,
#             headers={'Content-Type': 'application/json'}
#         )

#         # Check the response from the final API
#         if response.status_code == 201:
#             print("Data successfully forwarded to final API.")

#             # Attempt to save data to MongoDB
#             try:
#                 mongo_collection.insert_many(data)
#                 print("Data successfully saved to MongoDB.")
#                 return jsonify({
#                     "message": "Data successfully uploaded to final API and saved in MongoDB"
#                 }), 201
#             except Exception as mongo_error:
#                 print(f"Error saving data to MongoDB: {mongo_error}")
#                 return jsonify({
#                     "message": "Data uploaded to final API but failed to save in MongoDB",
#                     "mongo_error": str(mongo_error)
#                 }), 500
#         else:
#             return jsonify({
#                 "message": "Failed to upload data to final API",
#                 "status_code": response.status_code,
#                 "response_text": response.text
#             }), response.status_code

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

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

@app.route('/readValues', methods=['GET'])
def read_values():
    try:
        # Connect to SQL Database
        conn = sqlite3.connect('suvi_database.db')  # Update with your DB 
        cursor = conn.cursor()


        # Fetch node IDs from the SQL table
        cursor.execute("SELECT DISTINCT tagAddress FROM Tag_Table")  # Update table/column names
        node_ids = [row[0] for row in cursor.fetchall()]
        # print("Node IDs: {}".format(node_ids));
        if not node_ids:
            return jsonify({"success": False, "error": "No node IDs found in the database"})

        # Connect to the PLC
        client = Client(ENDPOINT_URL)
        client.session_timeout = 30000  # Adjust timeout as needed
        client.connect()

        results = []
        for node_id in node_ids:
            try:
                node = client.get_node(node_id)
                value = node.get_value()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
                results.append({"nodeId": node_id, "value": value, "timestamp": timestamp})
            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include timestamp for errors
                results.append({"nodeId": node_id, "error": str(e), "timestamp": timestamp})

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
            socketio.emit('liveData', {"success": True, "results": results})
            time.sleep(1)  # Fetch data every 2 seconds
    except Exception as e:
        print(f"Error in OPC UA connection: {e}")  # Log connection errors
        socketio.emit('liveData', {"success": False, "error": str(e)})
    finally:
        client.disconnect()
        print("Disconnected from OPC UA server!")  # Debug disconnection
@app.route('/getLiveValues', methods=['GET'])
def get_live_values():
    try:
        with sqlite3.connect(DB_PATH1) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Id,value, timestamp,tagId
                FROM Live_Tags 
            ''')
            live_values = cursor.fetchall()

        results = [{"tagId": value[3], "value": value[1], "timestamp": value[2]} for value in live_values]
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

def run_periodic_update2():
    while True:
        
        update_batch_status()
        
        time.sleep(1)  # Update every 1 seconds
        
if __name__ == '__main__':
    print("Starting Flask app...")
    threading.Thread(target=run_periodic_update1, daemon=True).start()
    threading.Thread(target=run_periodic_update2, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
