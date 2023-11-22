import socket
import sqlite3 as sql
from threading import Thread
"""
---STRUTTURA MESSAGGI---

Messaggio assegnazione fiume e localita (da server a client): fiume;localita
Messaggio livello (da client a server): idstazione;livello;timestamp (data ora)

Avvenuta ricezione: OK
Pericolo imminente: IMM
Pericolo in corso: WAR
"""

DB_PATH = 'fiumi.db'
SERVER_ADDRESS = ('0.0.0.0', 8000)

class Client(Thread):
    def __init__(self, connection: socket.socket, address):
        Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        id = int(self.connection.recv(4096).decode()) #ricevo l'id con cui si presenta il client
        #apro il db
        db = sql.connect(DB_PATH)
        cur = db.cursor()
        #ricavo fiume e localita dal db tramite ID ricevuto e invio a client
        self.fiume, self.localita = cur.execute(f'SELECT fiume, localita FROM livelli WHERE id_stazione = {id}').fetchall()[0]
        db.close()
        self.connection.sendall(f'{self.fiume};{self.localita}'.encode())

        while True: #ricezione livello dal client
            id, livello, timestamp = self.connection.recv(4096).decode().split(';') #ricevo messaggio dal client e divido i campi

            #ottengo livello di guardia dal DB
            db = sql.connect(DB_PATH)
            cur = db.cursor()
            guardia = cur.execute(f'SELECT livello FROM livelli WHERE id_stazione = {int(id)}').fetchall()[0][0]
            db.close()

            #controllo il livello ricevuto in relazione al livello di guardia
            if float(livello) < guardia * 0.3: #livello inferiore al 30% del livello di guardia
                self.connection.sendall('OK'.encode())
            elif float(livello) >= guardia * 0.3 and float(livello) < guardia * 0.7: #tra il 30% e il 70% del livello di guardia
                self.connection.sendall('IMM'.encode())
                print(f'Pericolo imminente @{self.fiume}-{self.localita} {timestamp}')
            elif float(livello) >= guardia * 0.7: #livello superiore al 70% del livello di guardia
                self.connection.sendall('WAR'.encode())
                print(f'Pericolo in corso @{self.fiume}-{self.localita} {timestamp}')
         

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Server TCP
    server.bind(SERVER_ADDRESS) #Assegnazione IP e porta a socket
    server.listen()

    try:
        while True:
                connection, address = server.accept() #Accettazione connessione
                client = Client(connection, address) #Creazione thread per nuovo client
                client.start()
    except KeyboardInterrupt:
         server.close()

if __name__ == '__main__':
    main()