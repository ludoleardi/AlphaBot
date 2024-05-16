import requests
from flask import jsonify

TOKEN = "SlkF84t7jgYmmJhgSre0"

data = {'codice':   '1234',
    'partenza': 'Bari',
    'arrivo':  'Pizzo Calabro'}

r = requests.post('http://localhost:5000/api/v1/consegna?token='+TOKEN, json=data)

print(r)