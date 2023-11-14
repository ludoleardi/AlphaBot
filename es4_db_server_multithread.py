import AlphaBot
import socket
import time
import RPi.GPIO as GPIO
import sqlite3 as sql
from threading import Thread, Lock

mutex = Lock()

DR = 16
DL = 19

MY_ADDRESS = ('0.0.0.0', 8000)
BUFF_SIZE = 4096

MOVING = False
i = ''

class Sensor(Thread):
    def __init__(self, connection, address, robot):
        Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.DL = DL
        self.DR = DR
        self.robot = robot

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(DR, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(DL, GPIO.IN, GPIO.PUD_UP)

    def run(self):
        global MOVING
        print('running...')
        self.warning = False
        while True:
            if MOVING:
                self.warning = False
                self.connection.sendall(f'{GPIO.input(self.DL)}, {GPIO.input(self.DR)}'.encode())
                time.sleep(0.5)
                if GPIO.input(self.DL) == 0 or GPIO.input(self.DL) == 0 and i != 'B':
                    self.robot.stop()
            else:
                if not self.warning:
                    self.connection.sendall(f'stop'.encode())
                    self.warning = True


def main():
    global MOVING
    global i
    piero = AlphaBot.AlphaBot()
    db = sql.connect("movements.db")
    cur = db.cursor()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = MY_ADDRESS
    s.bind(server_address)
    s.listen()
    connection, address = s.accept()
    sensor = Sensor(connection, address, piero)
    sensor.start()


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
                mutex.acquire()
                MOVING = True
                for command, t in zip(commands, times):
                    base_commands[command]()
                    time.sleep(float(t))
                    piero.stop()
                MOVING = False
                mutex.release()
            else:
                c, t = i.split(';')
                if c in base_commands:
                    mutex.acquire()
                    MOVING = True
                    base_commands[c]()
                    time.sleep(float(t))
                    piero.stop()
                    MOVING = False
                    mutex.release()
    except KeyboardInterrupt:
        db.close()
        connection.close()
        sensor.join()
        print('closing')

if __name__ == '__main__':
    main()