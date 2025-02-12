import os
from flask import Flask, request, make_response

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
    response = make_response(
        {
        'body': request.args.get('input', default='', type=str),
        'status': 200
        }
    )
    return response

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'response': 'OK',
            'status': 200
        }
    )
    return response

@app.route('/hang')
def hang():
    while True:
        continue 
    return "error"


if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port = int(os.getenv("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
