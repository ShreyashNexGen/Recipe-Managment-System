from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import timedelta

app = Flask(__name__)

# Secret key for session encryption
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

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

if __name__ == '__main__':
    app.run(debug=False)
