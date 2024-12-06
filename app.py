from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime
from datetime import timedelta
from flask_socketio import SocketIO, emit
from opcua import Client, ua
from flask import send_from_directory
import threading
from threading import Thread
import time
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
# Function to browser
def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DB_PATH) as conn:
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
                value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tagId) REFERENCES Tag_Table(tagId)
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
        recipes=recipes,
        pos_values=pos_values,
        page=page,
        total_pages=total_pages
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
    # Connect to the database and fetch tag data
    conn = sqlite3.connect('a2z_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all data from the Tag_Table
    cursor.execute('SELECT * FROM Tag_Table')
    tags = cursor.fetchall()

    conn.close()

    # Pagination example values (customize as needed)
    total_pages = 5  # Total number of pages (you can calculate this dynamically)
    current_page = 1  # Current page (adjust as per your logic)

    return render_template(
        'tag_overview.html',
        tags=tags,                # Pass the fetched tag data
        page=current_page,        # Pass the current page
        total_pages=total_pages,  # Pass the total number of pages
        active_menu='tags',       # Keep dropdown open
        active_submenu='tag-overview'  # Highlight active submenu
    )

@app.route('/delete-tag/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    try:
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Connect to the specific database
        conn = sqlite3.connect('a2z_database.db')  # Make sure we're connecting to the right database
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Execute deletion query
        cursor.execute('DELETE FROM Tag_Table WHERE tagId = ?', (tag_id,))
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
        material_id = request.form['material_Id']
        type_code = request.form['typeCode']
        lot_no = request.form['lotNo']
        make = request.form['make']
        user = request.form['user']
        material_type = request.form['materialType']
        barcode = request.form['barcode']

        # Connect to the database
        conn = sqlite3.connect('a2z_database.db')
        cursor = conn.cursor()

        # Insert new raw material into the Raw_Materials table
        cursor.execute("INSERT INTO Raw_Materials (material_Id,typeCode, lotNo,make,user,materialType,barcode) VALUES (?,?,?,?,?,?, ?)", ( material_id ,type_code,lot_no ,make ,user, material_type, barcode))
        conn.commit()
        conn.close()

        # Redirect to the same page to refresh the list after inserting new data
        return redirect(url_for('raw_material'))

    # Handle GET request to display the raw materials
    current_page = int(request.args.get('page', 1))
    conn = sqlite3.connect('a2z_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pagination setup
    items_per_page = 10
    offset = (current_page - 1) * items_per_page

    # Fetch data for the current page
    cursor.execute('SELECT * FROM Raw_Materials LIMIT ? OFFSET ?', (items_per_page, offset))
    raw_materials = cursor.fetchall()

    # Calculate total pages
    cursor.execute('SELECT COUNT(*) FROM Raw_Materials')
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows + items_per_page - 1) // items_per_page

    conn.close()

    # Render the template with the raw material data
    return render_template(
        'raw_material.html',
        raw_materials=raw_materials,
        page=current_page,
        total_pages=total_pages
    )


@app.route('/delete-raw-material/<int:raw_material_id>', methods=['DELETE'])
def delete_raw_material(raw_material_id):
    try:
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Connect to the specific database (a2z_database.db)
        conn = sqlite3.connect('a2z_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Execute deletion query
        cursor.execute('DELETE FROM Raw_Materials WHERE material_Id = ?', (raw_material_id,))
        conn.commit()

        # Check if the deletion actually occurred
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Raw material not found"}), 404

        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Error while deleting raw material: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
    finally:
        conn.close()









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
    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    conn.close()

    if not recipe_details:
        flash("Recipe not found!", "danger")
        return redirect(url_for('index'))

    return render_template('recipe_details.html', recipe_details=recipe_details, sub_menu=sub_menu)

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))

    recipe_id = request.form.get('recipe_id')
    filter_size = request.form.get('filter_size')
    filter_code = request.form.get('filter_code')
    art_no = request.form.get('art_no')
    pos_values = [request.form.get(f'pos{i}') for i in range(1, 10)]
    alu_coil_width = request.form.get('Alu_coil_width')
    alu_roller_type = request.form.get('Alu_roller_type')
    spacer = request.form.get('Spacer')
    print(pos_values);
    update_plc_with_pos_values(pos_values)
    if not (recipe_id and filter_size and filter_code and art_no):
        flash("All required fields must be filled!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO Recipe (Recipe_ID, Filter_Size, Filter_Code, Art_No) 
            VALUES (?, ?, ?, ?)''',
            (recipe_id, filter_size, filter_code, art_no)
        )
        cursor.execute(
            '''INSERT INTO Recipe_Details1 
            (Id, Pos1, Pos2, Pos3, Pos4, Pos5, Pos6, Pos7, Pos8, Pos9, Alu_coil_width, Alu_roller_type, Spacer, Recipe_ID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (recipe_id, *pos_values, alu_coil_width, alu_roller_type, spacer, recipe_id)
        )
        conn.commit()
        flash("Recipe added successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('index'))
# Function to update PLC via OPC UA based on POS values
from opcua import Client, ua

def update_plc_with_pos_values(pos_values):
    client = Client(ENDPOINT_URL)
    try:
        print("Connecting to OPC UA server...")
        client.connect()
        print("Connected to OPC UA server.")

        # Ensure pos_values is a list with at least 9 elements
        if not isinstance(pos_values, list) or len(pos_values) < 9:
            raise ValueError("pos_values must be a list with at least 9 elements.")

        # Iterate through POS values (1 to 9)
        for i in range(1, 10):
            pos_value = pos_values[i - 1]  # Access by index (0-based for lists)
            node_id = f'ns=3;s="OpenRecipe"."selectedRoll{i}"'
            print(f"Processing node: {node_id}, POS value: {pos_value}")

            try:
                # Get the node object
                node = client.get_node(node_id)
                print(f"Fetched node for Node ID: {node_id}")

                # Determine the value to set
                if pos_value:  # Check if the value is present (not None or empty)
                    node.set_value( ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                    print(f"Set value True for Node ID: {node_id}")
                else:
                    node.set_value( ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    print(f"Set value False for Node ID: {node_id}")

            except Exception as node_error:
                print(f"Error processing Node ID {node_id}: {node_error}")

        # Disconnect from the client
        print("Disconnecting from OPC UA server...")
        client.disconnect()
        print("Disconnected successfully.")

    except Exception as e:
        print(f"Error updating PLC: {e}")

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
    try:
        client.connect()

        # Fetch the value from the OPC UA server for the given tagAddress
        node = client.get_node(tag_address)
        value = node.get_value()

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

# def update_all_live_tags():
#     """Fetch all entries from Live_Tags, resolve tagAddress from Tag_Table, and update live values."""
#     client = Client(ENDPOINT_URL)
#     try:
#         print("Connecting to OPC UA server...")
#         client.connect()
#         start_time = time.time()  # Start timing
#         print("Connected to OPC UA server!")

#         with sqlite3.connect(DB_PATH) as conn:
#             cursor = conn.cursor()

#             # Fetch all tagIds from Live_Tags
#             cursor.execute('''SELECT id, tagId FROM Live_Tags''')
#             live_tags = cursor.fetchall()

#             for live_tag in live_tags:
#                 live_tag_id, tag_id = live_tag
#                 try:
#                     # Fetch tagAddress for the current tagId from Tag_Table
#                     cursor.execute('''SELECT tagAddress FROM Tag_Table WHERE Tagid = ?''', (tag_id,))
#                     result = cursor.fetchone()
#                     if not result:
#                         print(f"No tagAddress found for tagId {tag_id}. Skipping update.")
#                         continue

#                     tag_address = result[0]

#                     # Fetch the live value from OPC UA server
#                     node = client.get_node(tag_address)
#                     value = node.get_value()

#                     # Update the value in Live_Tags table
#                     cursor.execute('''
#                         UPDATE Live_Tags
#                         SET value = ?, timestamp = CURRENT_TIMESTAMP
#                         WHERE id = ?
#                     ''', (value, live_tag_id))
#                     conn.commit()

#                     print(f"Updated Live_Tags entry for tagId {tag_id} with value {value}.")
#                 except Exception as e:
#                     print(f"Error updating live value for tagId {tag_id}: {e}")

#     except Exception as e:
#         print(f"Error connecting to OPC UA server: {e}")
#     finally:
#         client.disconnect()
#         end_time = time.time()  # End timing
#         elapsed_time = end_time - start_time
#         print(f"Disconnected from OPC UA server. Session duration: {elapsed_time * 1000:.2f} ms.")



#update to make it faster
# def update_all_live_tags():
#     """Fetch all entries from Live_Tags, resolve tagAddress from Tag_Table, and update live values."""
#     try:
#         # Step 1: Fetch data from the database
#         with sqlite3.connect(DB_PATH) as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 SELECT lt.id, lt.tagId, tt.tagAddress 
#                 FROM Live_Tags lt 
#                 LEFT JOIN Tag_Table tt ON lt.tagId = tt.Tagid
#             ''')
#             live_tags = cursor.fetchall()

#         # Step 2: Connect to OPC UA server and update values
#         client = Client(ENDPOINT_URL)
#         print("Connecting to OPC UA server...")
#         client.connect()
#         print("Connected to OPC UA server!")
#         start_time = time.time()  # Start timing

#         updates = []
#         for live_tag in live_tags:
#             live_tag_id, tag_id, tag_address = live_tag
#             if not tag_address:
#                 print(f"No tagAddress found for tagId {tag_id}. Skipping update.")
#                 continue
#             start_time = time.time()  # Start timing

#             try:
#                 # Fetch the live value from OPC UA server
#                 node = client.get_node(tag_address)
#                 value = node.get_value()
#                 end_time = time.time()  # End timing
#                 updates.append((value, live_tag_id))

#                 print(f"Fetched value {value} for tagId {tag_id}.")
#             except Exception as e:
#                 print(f"Error fetching live value for tagId {tag_id}: {e}")

#         client.disconnect()
#         end_time = time.time()  # End timing
#         elapsed_time = (end_time - start_time)*1000;
#         print(f"Disconnected from OPC UA server. Session duration: {elapsed_time:.2f} ms.")

#         # Step 3: Update the database
#         with sqlite3.connect(DB_PATH) as conn:
#             cursor = conn.cursor()
#             cursor.executemany('''
#                 UPDATE Live_Tags
#                 SET value = ?, timestamp = CURRENT_TIMESTAMP
#                 WHERE id = ?
#             ''', updates)
#             conn.commit()
#             print(f"Updated {len(updates)} entries in the database.")

#     except Exception as e:
#         print(f"Error: {e}")
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
    updates = []

    try:
        print("Connecting to OPC UA server...")
        client.connect()
        print("Connected to OPC UA server!")

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
                print(f"Fetched value {value} for tagId {tag_id}. Time taken: {tag_elapsed_time:.2f} ms.")

                # Store the result
                updates.append((value, live_tag_id))
            except Exception as e:
                print(f"Error fetching live value for tagId {tag_id}: {e}")

        # Calculate overall session duration
        overall_end_time = time.time()
        overall_elapsed_time = (overall_end_time - overall_start_time) * 1000  # in milliseconds
        print(f"Disconnected from OPC UA server. Overall session duration: {overall_elapsed_time:.2f} ms.")

    finally:
        client.disconnect()

    return updates

def update_database(updates):
    """
    Update the database with the new live values.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            UPDATE Live_Tags
            SET value = ?, timestamp = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', updates)
        conn.commit()
        print(f"Updated {len(updates)} entries in the database.")

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
        client.connect()

        # Get the node object
        node = client.get_node(node_id)
        print("Received node:", node)  # This will print the data to the console

        # Fetch the DataType of the node
        data_type = node.get_data_type_as_variant_type()
        # print("Received datatype:", data_type)  # This will print the data to the console
        if not data_type:
            raise Exception(f"Could not fetch DataType for NodeId: {node_id}")

        print(f"Fetched DataType: {data_type}")

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
# @app.route('/readValues', methods=['POST'])
# def read_values():
#     data = request.json
#     node_ids = data.get("nodeIds", [])

#     try:
#         client = Client(ENDPOINT_URL)
#         client.connect()

#         results = []
#         for node_id in node_ids:
#             node = client.get_node(node_id)
#             value = node.get_value()
#             results.append({"nodeId": node_id, "value": value})

#         client.disconnect()
#         return jsonify({"success": True, "results": results})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})

@app.route('/readValues', methods=['GET'])
def read_values():
    try:
        # Connect to SQL Database
        conn = sqlite3.connect('a2z_database.db')  # Update with your DB details
        cursor = conn.cursor()


        # Fetch node IDs from the SQL table
        cursor.execute("SELECT DISTINCT tagAddress FROM Tag_Table")  # Update table/column names
        node_ids = [row[0] for row in cursor.fetchall()]
        print("Node IDs: {}".format(node_ids));
        if not node_ids:
            return jsonify({"success": False, "error": "No node IDs found in the database"})

        # Connect to the PLC
        client = Client(ENDPOINT_URL)
        client.connect()

        results = []
        for node_id in node_ids:
            try:
                node = client.get_node(node_id)
                value = node.get_value()
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
                results.append({"nodeId": node_id, "value": value, "timestamp": timestamp})
            except Exception as e:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include timestamp for errors
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
    try:
        print("Attempting to connect to OPC UA server...")
        client.connect()
        print("Connected to OPC UA server!")

        while True:
            results = []
            print("Fetching data for node IDs:", node_ids)  # Debug node IDs
            for node_id in node_ids:
                try:
                    print(f"Reading value for node ID: {node_id}")  # Log node ID
                    node = client.get_node(node_id)
                    value = node.get_value()
                    print(f"Value for node {node_id}: {value}")  # Log fetched value
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
        with sqlite3.connect(DB_PATH) as conn:
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
# if __name__ == '__main__':
#     app.run(debug=False)
def run_periodic_update():
    while True:
        update_all_live_tags()
        time.sleep(1)  # Update every 10 seconds
if __name__ == '__main__':
    print("Starting Flask app...")
    threading.Thread(target=run_periodic_update, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
