from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
# Secret key for session encryption
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Sample user data (hardcoded for simplicity, in production use a database)
USER_DATA = {
    'username': 'admin',
    'password_hash': generate_password_hash('password123')  # hashed password for security
}

def get_db_connection():
    conn = sqlite3.connect('RMS.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for the main page displaying the Recipe Table
@app.route('/')
def index():
    if 'username' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Get the current page number from the query parameter (default to 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Define how many items to display per page
    offset = (page - 1) * per_page

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch paginated recipes
    recipes = conn.execute(
        'SELECT * FROM Recipe LIMIT ? OFFSET ?', (per_page, offset)
    ).fetchall()

    # Fetch distinct Pos_Values from Pos_Options table
    cursor.execute("SELECT DISTINCT Pos_Values FROM Pos_Options")
    pos_values = [row[0] for row in cursor.fetchall()]

    # Get total count of recipes for pagination controls
    total_count = conn.execute('SELECT COUNT(*) FROM Recipe').fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page  # Calculate total pages

    # Close the connection
    conn.close()

    return render_template(
        'recipe.html',
        recipes=recipes,
        pos_values=pos_values,
        page=page,
        total_pages=total_pages
    )

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:  # If already logged in, redirect to home page
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists and password is correct
        if username == USER_DATA['username'] and check_password_hash(USER_DATA['password_hash'], password):
            session['username'] = username  # Store user session
            flash("Login successful!", 'success')
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials, please try again.", 'danger')

    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user session
    flash("Logged out successfully.", 'info')
    return redirect(url_for('login'))

# Route for the recipe details page
@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    conn = get_db_connection()
    # Fetch RecipeDetails for the given Recipe ID
    recipe_details = conn.execute('SELECT * FROM Recipe_Details1 WHERE Recipe_ID = ?', (recipe_id,)).fetchone()

    # Fetch SubMenu for the given Recipe ID
    sub_menu = conn.execute('SELECT * FROM Sub_Menu WHERE Recipe_ID = ?', (recipe_id,)).fetchone()
    conn.close()
    return render_template('recipe_details.html', recipe_details=recipe_details, sub_menu=sub_menu)

# Route for adding a new recipe
@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        filter_size = request.form.get('filter_size')
        filter_code = request.form.get('filter_code')
        art_no = request.form.get('art_no')
        Id = request.form.get('recipe_id')
        pos1 = request.form.get('pos1')
        pos2 = request.form.get('pos2')
        pos3 = request.form.get('pos3')
        pos4 = request.form.get('pos4')
        pos5 = request.form.get('pos5')
        pos6 = request.form.get('pos6')
        pos7 = request.form.get('pos7')
        pos8 = request.form.get('pos8')
        pos9 = request.form.get('pos9')
        Alu_coil_width = request.form.get('Alu_coil_width')
        Alu_roller_type = request.form.get('Alu_roller_type')
        Spacer = request.form.get('Spacer')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new recipe into the 'recipe' table
        cursor.execute(''' 
            INSERT INTO Recipe (Recipe_ID, Filter_Size, Filter_Code, Art_No) 
            VALUES (?, ?, ?, ?) 
        ''', (recipe_id, filter_size, filter_code, art_no))
        
        cursor.execute('''
            INSERT INTO Recipe_Details1 (Id, Pos1, Pos2, Pos3, Pos4, Pos5, Pos6, Pos7, Pos8, Pos9, Alu_coil_width, Alu_roller_type, Spacer, Recipe_ID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (Id, pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8, pos9, Alu_coil_width, Alu_roller_type, Spacer, recipe_id))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

    return redirect(url_for('index'))  # Redirect to main page or recipe list

if __name__ == '__main__':
    app.run(debug=True)
