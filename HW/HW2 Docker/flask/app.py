import os

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

@app.route('/repeat', methods=['GET'])
def repeat():
    input_val = request.args.get("input", "No input")
    response = make_response(
        {
            "body": input_val,
            "status": 200
        }
    )
    return response

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    if __name__ == '__main__':
        port = int(os.getenv("PORT", 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
