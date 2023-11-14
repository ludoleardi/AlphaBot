import AlphaBot
import socket
import time
import RPi.GPIO as GPIO
import sqlite3 as sql

piero = AlphaBot.AlphaBot()

db = sql.connect("movements.db")
cur = db.cursor()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("0.0.0.0", 8000)
s.bind(server_address)
s.listen()
connection, address = s.accept()

base_commands = {'F': piero.forward, 'B': piero.backward, 'L': piero.left, 'R':piero.right}
shortcuts = [s[0] for s in cur.execute("SELECT Shortcut FROM MOVEMENTS").fetchall()]

db.close()
try:
    while True:
        i = connection.recv(4096).decode('utf-8')
        if i in shortcuts:
            db = sql.connect("movements.db")
            cur = db.cursor()
            seq = cur.execute(f"SELECT Sequence FROM MOVEMENTS WHERE Shortcut = '{i}'").fetchone()[0]
            db.close()
            commands = seq.split(';')[::2]
            times = seq.split(';')[1::2]
            print(commands, times)
            for command, t in zip(commands, times):
                base_commands[command]()
                time.sleep(float(t))
                piero.stop()
        else:
            c, t = i.split(';')
            if c in base_commands:
                base_commands[c]()
                time.sleep(float(t))
                piero.stop()
except KeyboardInterrupt:
    db.close()
    connection.close()
    print('closing')