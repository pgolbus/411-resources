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

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    osVar = os.getenv("PORT", default=None)
    app.run(host='0.0.0.0',port=osVar, debug=True)
