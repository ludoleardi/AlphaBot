from flask import Flask, render_template, request, redirect, url_for, make_response
from sympy import *
import sqlite3 as sql
import hashlib
from time import sleep
app = Flask(__name__)

db_path = 'esercitazioneFlask/esercitazione.db'

#Usato per login
def calculate_hash(string):
    hash_object = hashlib.sha256(string.encode())
    hashed_string = hash_object.hexdigest()
    return hashed_string

#Pagina di login
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('psw')
        hashed_password = calculate_hash(password)

        db = sql.connect(db_path)
        cur = db.cursor()
        db_password = cur.execute(f'SELECT password FROM Users WHERE Username = "{username}"').fetchone()[0]
        db.close()
        
        if hashed_password == db_password:
            resp = redirect(url_for('calculate'))
            resp.set_cookie('username', username)
            return resp
        
    return render_template("login.html")

@app.route("/calculate", methods=['GET', 'POST'])
def calculate():
    res = ''
    db = sql.connect(db_path)
    cur = db.cursor()
    if request.method == 'POST':
        func = request.form.get('func')
        sx = request.form.get('sx')
        dx = request.form.get('dx')
        if sx == '' or dx == '':
            res = integrate(func)
            cur.execute(f"INSERT INTO Functions VALUES ('{func}', NULL, NULL, '{res}')")
            db.commit()
            print('Inserito')
        else:
            res = integrate(func, ('x', sx, dx))
            cur.execute(f"INSERT INTO Functions VALUES ('{func}', {Integer(sx)}, {Integer(dx)}, '{res}')")
            db.commit()
            print('Inserito')
            
    db.close()

    return render_template("calculate.html", result=res)
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')