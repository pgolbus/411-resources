from flask import Flask, make_response, request
import os

app = Flask(__name__)

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

@app.route('/repeat', methods=['GET'])
def repeat():
    input_value = request.args.get('input', '')
    response = make_response(
        {
            'body': input_value,
            'status': 200
        }
    )
    return response

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'body': 'OK',
            'status': 200
        }
    )
    return response

@app.route('/hang')
def hang():
    while True:
        pass

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port, debug=True)