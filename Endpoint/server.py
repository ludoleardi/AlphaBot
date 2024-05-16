from flask import Flask, request, abort

TOKENS = ["SlkF84t7jgYmmJhgSre0", "l8766hFDR65Mk"]

app = Flask(__name__)

@app.route('/api/v1/consegna', methods=['POST'])
def consegna():
    if request.args.get('token') in TOKENS:
        print(request.json)
        return 'OK'
    else:
        print('Accesso bloccato')
        abort(404)

@app.route('/api/v1/ordine', methods=['GET'])
def ordine():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')