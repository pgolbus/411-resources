from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify(response="Hello, World!", status=200)

@app.route('/repeat')
def repeat():
    input_value = request.args.get('input', '')
    return jsonify(body=input_value, status=200)

@app.route('/health')
@app.route('/healthcheck')
def health():
    return jsonify(body="OK", status=200)

@app.route('/hang')
def hang():
    while True:
        pass  

if __name__ == '__main__':
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=False)
