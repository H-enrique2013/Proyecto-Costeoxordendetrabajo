from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Carga variables desde .env


import os  # Usar para acceder a variables de entorno

app = Flask(__name__)

# Configuración directamente desde variables de entorno
app.config['SECRET_KEY'] = os.environ.get('HEX_SEC_KEY')  # o usa 'SECRET_KEY' si ese es el nombre
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user is not None:
        session['email'] = email
        session['name'] = user[1]
        session['surnames'] = user[2]
        return redirect(url_for('tasks'))
    else:
        return render_template('index.html', message="Las credenciales no son correctas")


@app.route('/tasks', methods=['GET'])
def tasks():
    email = session.get('email')
    if not email:
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE email = %s", [email])
    tasks = cur.fetchall()
    columnNames = [column[0] for column in cur.description]
    insertObject = [dict(zip(columnNames, record)) for record in tasks]
    cur.close()

    return render_template('tasks.html', tasks=insertObject)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/new-task', methods=['POST'])
def newTask():
    title = request.form['title']
    description = request.form['description']
    email = session.get('email')
    dateTask = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if title and description and email:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO tasks (email, title, description, date_task) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (email, title, description, dateTask))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('tasks'))


@app.route('/new-user', methods=['POST'])
def newUser():
    name = request.form['name']
    surnames = request.form['surnames']
    email = request.form['email']
    password = request.form['password']

    if name and surnames and email and password:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO users (name, surnames, email, password) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (name, surnames, email, password))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('tasks'))


@app.route("/delete-task", methods=["POST"])
def deleteTask():
    id = request.form['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=True)
