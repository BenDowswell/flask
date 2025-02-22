from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection

app = Flask(__name__)

@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM ingredients;")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()

    ingredient_list = [{"id": i[0], "name": i[1]} for i in ingredients]
    return render_template('home.html', ingredients=ingredient_list)

@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    ingredient_name = request.form.get('name')

    if ingredient_name:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO ingredients (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (ingredient_name,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('home'))

@app.route('/remove_ingredient', methods=['POST'])
def remove_ingredient():
    ingredient_id = request.form.get('ingredient_id')

    if ingredient_id:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM ingredients WHERE id = %s;", (ingredient_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('home'))

@app.route('/ingredients')
def view_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM ingredients;")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()

    ingredient_list = [{"id": i[0], "name": i[1]} for i in ingredients]
    return render_template('ingredients.html', ingredients=ingredient_list)


if __name__ == '__main__':
    app.run(debug=True)
