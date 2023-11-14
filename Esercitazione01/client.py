import socket

SERVER_ADDRESS = ('127.0.0.1', 8000)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Apertura socket client
    client.connect(SERVER_ADDRESS) #Connessione al server
    print(client.recv(4096).decode()) #Messaggio di conferma della connessione
    
    msg = ''
    while msg != 'exit':
        msg = input('Insert command: ')
        client.sendall(msg.encode())
        response = client.recv(4096).decode() #Risposta del server
        print(response)

    client.sendall(msg.encode()) #Invio messaggio di chiusura
    client.close()

if __name__ == '__main__':
    main()