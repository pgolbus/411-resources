from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return {
        "response": "Hello, World!",
        "status": 200
    }

@app.route('/repeat')
def repeat():
    input_param = request.args.get('input', '')
    return {
        "body": input_param,
        "status": 200
    }

@app.route('/health')
@app.route('/healthcheck')
def health():
    return {
        "body": "OK",
        "status": 200
    }

@app.route('/hang')
def hang():
    while True:
        pass

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, threaded=False)
