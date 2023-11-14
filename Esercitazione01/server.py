import socket
import sqlite3 as sql
from threading import Thread, Lock

DB_PATH = 'file.db'
SERVER_ADDRESS = ('0.0.0.0', 8000)

COMMANDS = ['?', 'LEN', 'LOC', 'LOCLIST'] #Comandi eseguibili dal server

class Client(Thread):
    def __init__(self, connection: socket.socket, address):
        Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.connection.sendall(f'Succesfully connected to {SERVER_ADDRESS}'.encode())

    def run(self):
        msg = ''
        while True:
            msg = self.connection.recv(4096).decode() #Messaggio ricevuto dal client

            if msg == 'exit':
                break

            print(msg)

            try: #Il messagio ricevuto potrebbe essere nel formato sbagliato
                command, params = msg.split(';')

                if command not in COMMANDS:
                    self.connection.sendall('Command not found!'.encode()) #Comando non esistente
                
                #chiedere al server se un certo nome file è presente
                elif command == '?':
                    db = sql.connect(DB_PATH) #Apertura db
                    cur = db.cursor()
                    resp = cur.execute(f'SELECT * FROM files WHERE nome = "{params}"').fetchall() #Esecuzione query
                    db.close() #Chiusura db
                    print(resp)
                    if resp != []: #File non trovato
                        self.connection.sendall('File exists'.encode()) 
                    else:
                        self.connection.sendall('File not found'.encode())

                #chiedere al server il numero di frammenti di un file a partire dal suo nome file
                elif command == 'LEN':
                    db = sql.connect(DB_PATH) #Apertura db
                    cur = db.cursor()
                    resp = cur.execute(f'SELECT tot_frammenti FROM files WHERE nome = "{params}"').fetchall() #Esecuzione query
                    db.close()
                    print(resp)
                    if resp != []: #File trovato
                        self.connection.sendall(f'{resp[0][0]} fragments found'.encode()) #Restituisco il numero di frammenti
                    else:
                        self.connection.sendall('File not found'.encode())

                #chiedere al server l’IP dell’host che ospita un frammento a partire nome file e dal numero del frammento
                elif command == 'LOC':
                    file_name, frag_num = params.split(':') #Divido nome del file e numero del frammento
                    db = sql.connect(DB_PATH) #Apertura db
                    cur = db.cursor()
                    resp = cur.execute(f'SELECT FR.host FROM frammenti FR, files FI WHERE FR.id_file = FI.id_file AND FI.nome = "{file_name}" AND FR.n_frammento = {frag_num}').fetchall() #Esecuzione query
                    db.close()
                    print(resp)
                    if resp != []: #File trovato
                        self.connection.sendall(f'{resp[0][0]}'.encode()) #Restituisco l'IP
                    else:
                        self.connection.sendall('File not found'.encode())

                #chiedere al server tutti gli IP degli host sui quali sono salvati i frammenti di un file a partire dal nome file
                elif command == 'LOCLIST':
                    db = sql.connect(DB_PATH) #Apertura db
                    cur = db.cursor()
                    resp = cur.execute(f'SELECT FR.host FROM frammenti FR, files FI WHERE FR.id_file = FI.id_file AND FI.nome = "{params}"').fetchall() #Esecuzione query
                    db.close()
                    print(resp)
                    if resp != []: #File trovato
                        self.connection.sendall(f'{resp}'.encode()) #Restituisco la lista di IP
                    else:
                        self.connection.sendall('File not found'.encode())

            except:
                self.connection.sendall('Command format incorrect!'.encode())
        
        self.connection.close() #Chiusura connessione

def main():
    thread_list = [] #Lista utilizzata per tenere traccia di tutti i thread aperti
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Server TCP
    server.bind(SERVER_ADDRESS) #Assegnazione IP e porta a socket
    server.listen()
    
    try:
        while True:
            connection, address = server.accept() #Accettazione connessione
            client = Client(connection, address) #Creazione thread per nuovo client
            thread_list.append(client) #Aggiungo il thread del nuovo client alla lista
            print(f'{address} connected. \nCurrent threads: \n{thread_list}')
            client.start() #Avvio il thread del nuovo client
    except KeyboardInterrupt:
        for thread in thread_list: #Chiusura di tutti i thread
            thread.join()
        print('closing')

if __name__ == '__main__':
    main()