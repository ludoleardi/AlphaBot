import semaforo
from flask import Flask, render_template, request, redirect, url_for
import datetime
import sqlite3 as sql
import hashlib

app = Flask(__name__)

s = semaforo.semaforo()

db_path = 'LEARDI_LUDOVICO/semaforoLeardi.db'

#Usato per login
def calculate_hash(string):
    hash_object = hashlib.sha256(string.encode())
    hashed_string = hash_object.hexdigest()
    return hashed_string

#Pagina di login
#user: Admin
#password: Admin
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #Ottengo i dati dal form e calcolo il digest della password
        username = request.form.get('user')
        password = request.form.get('psw')
        db_password = None
        hashed_password = calculate_hash(password)

        #Apro il db e ottengo il digest dell'utente corrispondente
        db = sql.connect(db_path)
        cur = db.cursor()
        res = cur.execute(f'SELECT password FROM Users WHERE Username = "{username}"').fetchone()
        if res is not None:
            db_password = res[0]
        db.close()
        
        #Confronto i due digest, eventualmente faccio il redirect alla pagina di controllo
        if db_password is not None and hashed_password == db_password:
            resp = redirect(url_for('config'))
            resp.set_cookie('username', username)
            return resp
        
    return render_template("login.html")

#Pagina di configurazione
@app.route('/config', methods=['GET', 'POST'])
def config():
    #Apro il db e ottengo gli ultimi tempi del semaforo
    db = sql.connect(db_path)
    cur = db.cursor()
    res = cur.execute(f'SELECT * FROM Semaforo').fetchall()

    #Ottengo l'user
    username = request.cookies.get('username')

    #Nel db sono presenti dei tempi (considero i più recenti)
    if res != []:
        res = res[-1]#ultima riga

        rosso = res[0]
        giallo = res[1]
        verde = res[2]
        spento = res[3]
        lampeggiamento = res[4]
        stato_db = res[5]
    else: #nel db non sono presenti tempi, imposto default e inserisco
        rosso = 2
        giallo = 1
        verde = 2
        spento = 1
        lampeggiamento = 1
        stato_db = 'ATTIVO'

        cur.execute(f"INSERT INTO Semaforo VALUES ({rosso}, {giallo}, {verde}, {spento}, {lampeggiamento}, '{stato_db}')")
        db.commit()
    db.close()

    #Ottengo i valori inseriti nel form
    if request.method == 'POST':
        verde = request.form.get('verde')
        giallo = request.form.get('giallo')
        rosso = request.form.get('rosso')
        spento = request.form.get('spento')
        lampeggiamento = request.form.get('lampeggiamento')
        stato = request.form.get('stato')

        #Inserisco i nuovi valori nel db
        db = sql.connect(db_path)
        cur = db.cursor()
        cur.execute(f"INSERT INTO Semaforo VALUES({rosso}, {giallo}, {verde}, {spento}, {lampeggiamento}, '{stato}')")
        db.commit()

        #Verifico se lo stato è cambiato
        if stato_db != stato:
            cur.execute(f"INSERT INTO Modifiche VALUES('{stato}', '{datetime.datetime.now()}', '{username}')")
            db.commit()
        db.close()
        return render_template('config.html', rosso=rosso, giallo=giallo, verde=verde, spento=spento, lampeggiamento=lampeggiamento, stato=stato)

    #passo i tempi per usarli come placeholder in html configurazione
    return render_template('config.html', rosso=rosso, giallo=giallo, verde=verde, spento=spento, lampeggiamento=lampeggiamento, stato=stato_db)

#Pagina di test
@app.route('/test')
def test():
    #Apro il db e ottengo gli ultimi tempi del semaforo
    db = sql.connect(db_path)
    cur = db.cursor()
    res = cur.execute(f'SELECT * FROM Semaforo').fetchall()
    db.close()

    #Nel db sono presenti dei tempi
    if res != []:
        res = res[-1] #ultima riga

        rosso = res[0]
        giallo = res[1]
        verde = res[2]
        spento = res[3]
        lampeggiamento = res[4]
        stato = res[5]

    if stato == "ATTIVO":
        s.rosso(rosso)
        s.verde(verde)
        s.giallo(giallo)
    else:
        for _ in range(3):
            s.giallo(lampeggiamento)
            s.luci_spente(spento)
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
