import AlphaBot
import socket
import time
import RPi.GPIO as GPIO

piero = AlphaBot.AlphaBot()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("0.0.0.0", 8000)
s.bind(server_address)

s.listen()
connection, address = s.accept()

dict = {'F': piero.forward, 'B': piero.backward, 'L': piero.left, 'R':piero.right}
while True:
    try:
        text_received = connection.recv(4096).decode('utf-8')
        print(text_received)
        if text_received != '' and text_received in dict:
            dict[text_received]()
            time.sleep(1)
            piero.stop()
    except KeyboardInterrupt:
        s.close()
        GPIO.cleanup()
        connection.close()