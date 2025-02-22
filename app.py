from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with a strong secret key in production

# -----------------------------
# Home Route
# -----------------------------
@app.route('/')
def home():
    return render_template('home.html')

# -----------------------------
# Recipe Endpoints
# -----------------------------
@app.route('/view_recipes')
def view_recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.name, r.date_added, u.username
        FROM recipes r
        LEFT JOIN users u ON r.created_by = u.id
        ORDER BY r.date_added DESC;
    """)
    recipes_data = cur.fetchall()
    cur.close()
    conn.close()
    recipes = [{"id": r[0], "name": r[1], "date_added": r[2], "username": r[3]} for r in recipes_data]
    return render_template('view_recipes.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch recipe info (including the user who created it)
    cur.execute("""
        SELECT r.id, r.name, r.date_added, u.username
        FROM recipes r
        LEFT JOIN users u ON r.created_by = u.id
        WHERE r.id = %s;
    """, (recipe_id,))
    recipe_row = cur.fetchone()
    if not recipe_row:
        cur.close()
        conn.close()
        return "Recipe not found", 404

    recipe = {
        "id": recipe_row[0],
        "name": recipe_row[1],
        "date_added": recipe_row[2],
        "username": recipe_row[3]
    }

    # Fetch recipe ingredients from the join table
    cur.execute("""
        SELECT i.id, i.name, ri.quantity
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = %s;
    """, (recipe_id,))
    ingredients_data = cur.fetchall()
    recipe["ingredients"] = [{"id": i[0], "name": i[1], "quantity": i[2]} for i in ingredients_data]

    # Debug: Print the fetched ingredients to the console
    print("Fetched ingredients for recipe", recipe_id, ":", recipe["ingredients"])

    # (Optional: Fetch recipe steps and comments here)
    cur.execute("""
        SELECT step_number, description
        FROM recipe_steps
        WHERE recipe_id = %s
        ORDER BY step_number;
    """, (recipe_id,))
    steps_data = cur.fetchall()
    recipe["steps"] = [{"step_number": s[0], "description": s[1]} for s in steps_data]

    cur.execute("""
        SELECT c.id, c.comment, c.date_added, u.username
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.recipe_id = %s
        ORDER BY c.date_added;
    """, (recipe_id,))
    comments_data = cur.fetchall()
    recipe["comments"] = [{"id": c[0], "comment": c[1], "date_added": c[2], "username": c[3]} for c in comments_data]

    cur.close()
    conn.close()

    return render_template('view_recipe.html', recipe=recipe)

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch recipe info
    cur.execute("""
        SELECT r.id, r.name, r.date_added, u.username
        FROM recipes r
        LEFT JOIN users u ON r.created_by = u.id
        WHERE r.id = %s;
    """, (recipe_id,))
    recipe_row = cur.fetchone()
    if not recipe_row:
        cur.close()
        conn.close()
        return "Recipe not found", 404

    recipe = {
        "id": recipe_row[0],
        "name": recipe_row[1],
        "date_added": recipe_row[2],
        "username": recipe_row[3]
    }

    # Fetch recipe steps
    cur.execute("""
        SELECT step_number, description
        FROM recipe_steps
        WHERE recipe_id = %s
        ORDER BY step_number;
    """, (recipe_id,))
    steps_data = cur.fetchall()
    recipe["steps"] = [{"step_number": s[0], "description": s[1]} for s in steps_data]

    # Fetch recipe ingredients
    cur.execute("""
        SELECT i.id, i.name, ri.quantity
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = %s;
    """, (recipe_id,))
    ingredients_data = cur.fetchall()
    recipe["ingredients"] = [{"id": i[0], "name": i[1], "quantity": i[2]} for i in ingredients_data]

    # Fetch comments
    cur.execute("""
        SELECT c.id, c.comment, c.date_added, u.username
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.recipe_id = %s
        ORDER BY c.date_added;
    """, (recipe_id,))
    comments_data = cur.fetchall()
    recipe["comments"] = [{"id": c[0], "comment": c[1], "date_added": c[2], "username": c[3]} for c in comments_data]

    cur.close()
    conn.close()
    return render_template('view_recipe.html', recipe=recipe)

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    name = request.form.get('name')
    steps_list = request.form.getlist('steps[]')
    created_by = request.form.get('user_id')
    
    # Debug prints
    print("Recipe Name:", name)
    print("Steps:", steps_list)
    
    if not name or not steps_list:
        flash("Recipe name and steps are required.")
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert recipe record and get its ID
    cur.execute("INSERT INTO recipes (name, created_by) VALUES (%s, %s) RETURNING id;", (name, created_by))
    recipe_id = cur.fetchone()[0]
    conn.commit()
    
    # Insert each recipe step
    for i, step in enumerate(steps_list, start=1):
        cur.execute(
            "INSERT INTO recipe_steps (recipe_id, step_number, description) VALUES (%s, %s, %s);",
            (recipe_id, i, step)
        )
    
    # Fetch ingredient IDs and quantities from the form
    ingredient_ids = request.form.getlist('ingredient_ids[]')
    ingredient_quantities = request.form.getlist('ingredient_quantities[]')
    
    # Debug prints for ingredients
    print("Ingredient IDs:", ingredient_ids)
    print("Ingredient Quantities:", ingredient_quantities)
    
    # Loop through provided ingredients and insert them into the join table
    for ing_id, quantity in zip(ingredient_ids, ingredient_quantities):
        # Only insert if a valid ingredient ID is provided (i.e., not an empty string)
        if ing_id:
            cur.execute(
                "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (%s, %s, %s);",
                (recipe_id, ing_id, quantity)
            )
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash("Recipe added successfully.")
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

    name = request.form.get('name')
    # If multiple steps were added dynamically, they will be available as a list:
    steps_list = request.form.getlist('steps[]')
    created_by = request.form.get('user_id')
    
    if not name or not steps_list:
        flash("Recipe name and steps are required.")
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO recipes (name, created_by) VALUES (%s, %s) RETURNING id;",
                (name, created_by))
    recipe_id = cur.fetchone()[0]
    conn.commit()
    
    for i, step in enumerate(steps_list, start=1):
        cur.execute(
            "INSERT INTO recipe_steps (recipe_id, step_number, description) VALUES (%s, %s, %s);",
            (recipe_id, i, step)
        )
    
    # Process ingredient arrays:
    ingredient_names = request.form.getlist('ingredient_names[]')
    ingredient_quantities = request.form.getlist('ingredient_quantities[]')
    for name, quantity in zip(ingredient_names, ingredient_quantities):
        # Insert ingredient if it doesn't exist
        cur.execute("INSERT INTO ingredients (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (name,))
        cur.execute("SELECT id FROM ingredients WHERE name = %s;", (name,))
        ingredient_id = cur.fetchone()[0]
        cur.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (%s, %s, %s);",
                    (recipe_id, ingredient_id, quantity))
    
    conn.commit()
    cur.close()
    conn.close()
    flash("Recipe added successfully.")
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

@app.route('/remove_recipe', methods=['POST'])
def remove_recipe():
    recipe_id = request.form.get('recipe_id')
    if recipe_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Recipe removed successfully.")
    return redirect(url_for('view_recipes'))

# -----------------------------
# Ingredient Endpoints
# -----------------------------
@app.route('/view_ingredients')
def view_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, date_added FROM ingredients ORDER BY name;")
    ingredients_data = cur.fetchall()
    cur.close()
    conn.close()
    ingredients = [{"id": i[0], "name": i[1], "date_added": i[2]} for i in ingredients_data]
    return render_template('view_ingredients.html', ingredients=ingredients)

@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    name = request.form.get('name')
    if not name:
        flash("Ingredient name is required.")
        return redirect(url_for('view_ingredients'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO ingredients (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (name,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Ingredient added successfully.")
    return redirect(url_for('view_ingredients'))

@app.route('/remove_ingredient', methods=['POST'])
def remove_ingredient():
    ingredient_id = request.form.get('ingredient_id')
    if ingredient_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredients WHERE id = %s;", (ingredient_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Ingredient removed successfully.")
    return redirect(url_for('view_ingredients'))

# -----------------------------
# Comments Endpoint
# -----------------------------
@app.route('/add_comment/<int:recipe_id>', methods=['POST'])
def add_comment(recipe_id):
    comment_text = request.form.get('comment')
    user_id = request.form.get('user_id')
    if not comment_text:
        flash("Comment cannot be empty.")
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (recipe_id, user_id, comment) VALUES (%s, %s, %s);",
                (recipe_id, user_id, comment_text))
    conn.commit()
    cur.close()
    conn.close()
    flash("Comment added.")
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

# -----------------------------
# User Authentication Endpoints
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        if not username or not email or not password or not confirm:
            flash("All fields are required.")
            return redirect(url_for('register'))
        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s;", (username, email))
        existing = cur.fetchone()
        if existing:
            flash("Username or email already registered.")
            cur.close()
            conn.close()
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
                    (username, email, password_hash))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        
        flash("Registration successful. Welcome, {}!".format(username))
        return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Please enter both username and password.")
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user is None or not check_password_hash(user[1], password):
            flash("Invalid username or password.")
            return redirect(url_for('login'))
        
        session['user_id'] = user[0]
        session['username'] = username
        
        print(f"User {username} (ID: {user[0]}) logged in successfully.")
        
        flash("Login successful. Welcome back, {}!".format(username))
        return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    # Ensure the user is logged in
    if not session.get('user_id'):
        flash("You need to log in to view your profile.")
        return redirect(url_for('login'))
    # For now, simply render a placeholder profile page
    return render_template('profile.html')

# -----------------------------
# Context Processors
# -----------------------------
@app.context_processor
def inject_user():
    current_user = session.get('username')
    user_id = session.get('user_id')
    return dict(current_user=current_user, user_id=user_id)

@app.context_processor
def inject_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes;")
    recipes_data = cur.fetchall()
    cur.execute("SELECT id, name FROM ingredients;")
    ingredients_data = cur.fetchall()
    cur.close()
    conn.close()
    recipes = [{"id": r[0], "name": r[1]} for r in recipes_data]
    ingredients = [{"id": i[0], "name": i[1]} for i in ingredients_data]
    return dict(recipes=recipes, ingredients=ingredients)

@app.route('/find_recipes', methods=['POST'])
def find_recipes():
    data = request.get_json()
    available = data.get("available_ingredients", [])
    if not available:
        return jsonify({"error": "No available ingredients provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    query_full = """
        SELECT r.id, r.name
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        GROUP BY r.id, r.name
        HAVING COUNT(*) = COUNT(CASE WHEN ri.ingredient_id = ANY(%s) THEN 1 END);
    """
    cur.execute(query_full, (available,))
    full_recipes_data = cur.fetchall()
    full_recipes = [{"id": r[0], "name": r[1]} for r in full_recipes_data]

    query_missing = """
        SELECT r.id, r.name, COUNT(*) as total_required,
               COUNT(CASE WHEN ri.ingredient_id = ANY(%s) THEN 1 END) as available_count
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        GROUP BY r.id, r.name
        HAVING (COUNT(*) - COUNT(CASE WHEN ri.ingredient_id = ANY(%s) THEN 1 END)) = 1;
    """
    cur.execute(query_missing, (available, available))
    missing_recipes_data = cur.fetchall()
    missing_recipes = []
    for row in missing_recipes_data:
        recipe_id = row[0]
        recipe_name = row[1]
        query_missing_ing = """
            SELECT i.id, i.name
            FROM ingredients i
            JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = %s AND i.id NOT IN (SELECT unnest(%s))
        """
        cur.execute(query_missing_ing, (recipe_id, available))
        missing_ing = cur.fetchone()
        if missing_ing:
            missing_recipes.append({
                "id": recipe_id,
                "name": recipe_name,
                "missing_ingredient": {"id": missing_ing[0], "name": missing_ing[1]}
            })
    cur.close()
    conn.close()
    return jsonify({
        "recipes_available": full_recipes,
        "recipes_missing": missing_recipes
    })

if __name__ == '__main__':
    app.run(debug=True)
