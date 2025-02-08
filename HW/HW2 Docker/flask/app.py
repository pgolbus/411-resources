from flask import Flask, make_response, request
import os

app = Flask(__name__)

port = int(os.getenv('PORT', 5002))

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

@app.route('/repeat')
def foo():
    name = request.args.get('input')
    response = make_response(
        {
            "response" : name,
            "status" : 200
        }
    )
    return response

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'body': "OK",
            'status': 200
        }
    )
    return response

@app.route('/hang')
def hang():
    i = 0
    while i < 4:
        response = make_response(
        {
            'body': "OK",
            'status': 200
        }
    )
    return response

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', port=5002, debug=False)
