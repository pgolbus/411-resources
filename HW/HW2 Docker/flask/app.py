import os
from flask import Flask, make_response, request

app = Flask(__name__)

port = int(os.getenv("PORT"))
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
def repeat_input():
    # Retrieve the 'input' parameter from the query string
    input_value = request.args.get('input')

    response = make_response(
        {
            'body': input_value ,
            'status': 200
        }
    )
    return response

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', debug=True)
