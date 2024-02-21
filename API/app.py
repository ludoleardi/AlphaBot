from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import AlphaBot

app = Flask(__name__)

DR = 16
DL = 19
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DR, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(DL, GPIO.IN, GPIO.PUD_UP)

@app.route('/api/v1/resources/sensors/left', methods=['GET'])
def api_left():
    return jsonify(GPIO.input(DL))

@app.route('/api/v1/resources/sensors/right', methods=['GET'])
def api_right():
    return jsonify(GPIO.input(DR))

@app.route('/api/v1/resources/sensors', methods=['GET'])
def api():
    return jsonify(GPIO.input(DL), GPIO.input(DR))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')