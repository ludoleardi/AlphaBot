from flask import Flask, render_template, request, redirect, url_for
import AlphaBot
import sqlite3 as sql
import hashlib
from time import sleep
app = Flask(__name__)

#Inizializzazione Alphabot e DB
piero = AlphaBot.AlphaBot()
db_path = '../Alphabot.db'

db = sql.connect(db_path)
cur = db.cursor()
shortcuts = [s[0] for s in cur.execute("SELECT Shortcut FROM MOVEMENTS").fetchall()] #Selezione shortcut per riferimento
db.close()

#Comandi Base
base_commands = {'F': piero.forward, 'B': piero.backward, 'L': piero.left, 'R':piero.right}

#Usato per login
def calculate_hash(string):
    hash_object = hashlib.sha256(string.encode())
    hashed_string = hash_object.hexdigest()
    return hashed_string

# Pagina Login
#Username: Admin
#Password: Admin
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
            return redirect(url_for("controls"))
        
    return render_template("login.html")

# Pagina controlli
@app.route("/controls", methods=['GET', 'POST'])
def controls():
    if request.method == 'POST':
        #print(request.form.get('avanti'))
        if request.form.get('avanti') == 'avanti':
            piero.forward()
            sleep(1)
            piero.stop()
        elif request.form.get('indietro') == 'indietro':
            piero.backward()
            sleep(1)
            piero.stop()
        elif request.form.get('sinistra') == 'sinistra':
            piero.left()
            sleep(1)
            piero.stop()
        elif request.form.get('destra') == 'destra':
            piero.left()
            sleep(1)
            piero.stop()
        #Comando complesso
        elif request.form.get('submit') == 'submit':
            text = request.form['speciale']
            print(text)
            if text in shortcuts:
                db = sql.connect(db_path)
                cur = db.cursor()
                seq = cur.execute(f"SELECT Sequence FROM MOVEMENTS WHERE Shortcut = '{text}'").fetchone()[0]
                db.close()
                commands = seq.split(';')[::2]
                times = seq.split(';')[1::2]
                print(commands, times)
                for command, t in zip(commands, times):
                    base_commands[command]()
                    sleep(float(t))
                    piero.stop()
        else:
            print("Unknown")
    elif request.method == 'GET':
        return render_template('controls.html')
    
    return render_template("controls.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')