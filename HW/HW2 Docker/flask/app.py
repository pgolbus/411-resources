from flask import Flask, make_response
import os
from flask import request
PORT = os.getenv('PORT')
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




@app.route('/repeat',methods=['GET']) 
def repeat():
    user_input = request.args.get('input')
    return {
            "body": user_input, "status": 200
    }   

@app.route('/healthcheck') 
@app.route('/health')
def health(): 
    response = make_response(
        {
        "body": "OK",
        "status": 200
        }
    )
    return response

@app.route('/hang')
def hang():
    i = 0
    while i >= 0:
        i += 1


if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', debug=True, port=PORT)
