from flask import *
from flask_mysqldb import MySQL
import os
import matplotlib.pyplot as plt
import io
import base64
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(8)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST','localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER','root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD','')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE','mysql')

mysql = MySQL(app)
def get_db():
    return mysql.connection

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = get_db().cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        get_db().commit()
        cur.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = get_db().cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and password == user[2]:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        flash('Invalid login credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/expenses')
def expenses():
    if 'user_id' not in session:
        return redirect('/login')
    cur = get_db().cursor()
    cur.execute("SELECT id, user_id, DATE_FORMAT(date, '%%Y-%%m-%%d') as date, category, amount, description FROM expenses WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    expense_tuples = cur.fetchall()
    cur.close()
    columns = ['id', 'user_id', 'date', 'category', 'amount', 'description']
    expenses = [dict(zip(columns, expense_tuple)) for expense_tuple in expense_tuples]
    return render_template('expenses.html', expenses=expenses)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        cur = get_db().cursor()
        cur.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (%s, %s, %s, %s, %s)",
                    (session['user_id'], float(amount), category, description, date))
        get_db().commit()
        cur.close()
        return redirect('/dashboard')
    return render_template('add_expense.html')

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect('/login')
    cur = get_db().cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id = %s GROUP BY category", (session['user_id'],))
    data = cur.fetchall()
    cur.close()
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]
    plt.figure(figsize=(10, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Expense Distribution by Category')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('report.html', graph_url=graph_url, expenses=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)