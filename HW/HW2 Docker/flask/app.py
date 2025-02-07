# HW2:
import os

# get port value from Dockerfile
port = os.getenv('PORT')

from flask import Flask, make_response, request

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



@app.route('/repeat',methods=['GET']) # 2) Add a route that uses a get parameter

def repeat():
    input = request.args.get('input')
    return {
            "body": input,
            "status": 200
    }   

@app.route('/health') # 1) Add a route that returns a health check
@app.route('/healthcheck') # same shit should be
def health(): # Copy-pasta the hello function and create a new one called health
    response = make_response(
        {
        "body": "OK",
        "status": 200
        }
    )
    return response

@app.route('/hang')
def hang():
    while True:
        pass # infinite loop

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)

    # make this port the environment variable PORT
    app.run(host='0.0.0.0', port = port, debug=False,threaded = False)
