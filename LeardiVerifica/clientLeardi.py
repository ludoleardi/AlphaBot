import socket
import datetime
import random
from time import sleep

SERVER_ADDRESS = ('127.0.0.1', 8000)
DLY = 15 #tempo tra un messaggio e l'altro

TEST_VALUES = [] #Lista valori per test
for i in range (0, 100):
    TEST_VALUES.append(random.random() * 10) #generazione valori per test

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Apertura socket client
    client.connect(SERVER_ADDRESS) #Connessione al server
    id = input('Inerisci ID stazione: ')
    client.sendall(id.encode()) #invio l'ID della stazione al server
    fiume, localita = client.recv(4096).decode().split(';') #il server mi restituisce fiume e localita
    print(fiume, localita)

    sirena = False #output sirena

    while True:
        livello = random.choice(TEST_VALUES) #scelgo valore casuale dalla lista, sarebbe lettura da sensore
        client.sendall(f'{id};{livello};{str(datetime.datetime.now())}'.encode()) #invio id, livello e timestamp secondo struttura
        msg = client.recv(4096).decode() #ricevo la risposta dal server
        if msg == 'OK': #il server ha ricevuto il dato e non ci sono pericoli
            sirena = False #spengo la sirena nel caso fosse accesa
            print(f'Sirena: {sirena}')
        elif msg == 'IMM':
            sirena = False #spengo la sirena nel caso fosse accesa
            print('Pericolo imminente')
            print(f'Sirena: {sirena}')
        elif msg == 'WAR':
            sirena = True #Attivo la sirena
            print('Pericolo in corso!')
            print(f'Sirena: {sirena}')
        sleep(DLY)

if __name__ == '__main__':
    main()