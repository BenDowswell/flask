from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)

# Route to fetch all recipes
@app.route('/recipes', methods=['GET'])
def get_recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, instructions FROM recipes;")
    recipes = cur.fetchall()
    cur.close()
    conn.close()
    
    recipe_list = [{"id": r[0], "name": r[1], "instructions": r[2]} for r in recipes]
    return jsonify(recipe_list)

# Route to fetch a recipe by ID
@app.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, instructions FROM recipes WHERE id = %s;", (recipe_id,))
    recipe = cur.fetchone()
    cur.close()
    conn.close()

    if recipe:
        return jsonify({"id": recipe[0], "name": recipe[1], "instructions": recipe[2]})
    else:
        return jsonify({"error": "Recipe not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
