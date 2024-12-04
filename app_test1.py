from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from opcua import Client

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

def connect_to_opcua_server():
    opcua_server_url = "opc.tcp://localhost:4840"  # Replace with your OPC UA server URL
    client = Client(opcua_server_url)
    client.connect()
    return client

def write_recipe_to_plc(client, recipe_id, recipe_data):
    # Assuming you have a node in your OPC UA server to write data (you need to define it in your server)
    recipe_node = client.get_node("ns=2;s=RecipeData")  # Example OPC UA node for RecipeData
    # Write data to the node
    recipe_node.set_value(recipe_data)  # Assuming recipe_data is in a suitable format for the PLC

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get the current page number from the query parameter (default to 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch paginated recipes
    recipes = conn.execute('SELECT * FROM Recipe LIMIT ? OFFSET ?', (per_page, offset)).fetchall()

    # Fetch distinct Pos_Values from Pos_Options table
    cursor.execute("SELECT DISTINCT Pos_Values FROM Pos_Options")
    pos_values = [row[0] for row in cursor.fetchall()]

    # Get total count of recipes for pagination controls
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

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        filter_size = request.form.get('filter_size')
        filter_code = request.form.get('filter_code')
        art_no = request.form.get('art_no')
        pos1 = request.form.get('pos1')
        pos2 = request.form.get('pos2')
        pos3 = request.form.get('pos3')
        pos4 = request.form.get('pos4')
        pos5 = request.form.get('pos5')
        pos6 = request.form.get('pos6')
        pos7 = request.form.get('pos7')
        pos8 = request.form.get('pos8')
        pos9 = request.form.get('pos9')
        alu_coil_width = request.form.get('Alu_coil_width')
        alu_roller_type = request.form.get('Alu_roller_type')
        spacer = request.form.get('Spacer')

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
        ''', (recipe_id, pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8, pos9, alu_coil_width, alu_roller_type, spacer, recipe_id))

        conn.commit()
        conn.close()

        # After adding the recipe, connect to the OPC UA server and write data
        client = connect_to_opcua_server()
        recipe_data = {
            'Recipe_ID': recipe_id,
            'Filter_Size': filter_size,
            'Filter_Code': filter_code,
            'Art_No': art_no,
            'Pos1': pos1,
            'Pos2': pos2,
            'Pos3': pos3,
            'Pos4': pos4,
            'Pos5': pos5,
            'Pos6': pos6,
            'Pos7': pos7,
            'Pos8': pos8,
            'Pos9': pos9,
            'Alu_coil_width': alu_coil_width,
            'Alu_roller_type': alu_roller_type,
            'Spacer': spacer
        }
        write_recipe_to_plc(client, recipe_id, recipe_data)
        client.disconnect()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
