from flask import *
import mysql.connector
import matplotlib.pyplot as plt
import os
import io
import base64
import datetime

app = Flask(__name__)

# MySQL configurations
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

def get_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')
# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s, %s)", 
                   (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        # Get full user record including id and name
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        # Check if user exists and password matches
        if user == user['username'] and password == user['password']:
            # Create session
            session['user_id'] = user['id'] 
            session['name'] = user['name']
        else:
            flash('Invalid login credentials')
            return redirect('/dashboard')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    expenses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dashboard.html', expenses=expenses)

# Add expense
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (%s, %s, %s, %s, %s)",
                   (session['user_id'], float(amount), category, description, datetime.datetime.strptime(date, '%Y-%m-%d')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_expense.html')

# Generate expense report
@app.route('/expenses')
def expenses():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT id, user_id, amount, category, date, description
                   FROM expenses 
                   WHERE user_id = %s 
                   ORDER BY date DESC""", (session['user_id'],))
    expenses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('expenses.html', expenses=expenses)

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s GROUP BY category", 
                (session['user_id'],))
    data = cur.fetchall()
    cur.close()
    conn.close()
    categories = [row['category'] for row in data]
    amounts = [float(row['total']) for row in data]
    plt.figure(figsize=(10,6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Expense Distribution by Category')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('report.html', graph_url=graph_url, expenses=data)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Run the app on all available network interfaces (0.0.0.0) on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
