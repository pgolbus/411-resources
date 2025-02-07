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


@app.route('/repeat')
def repeat_input():
    user_input = request.args.get('input', 'No input provided')
    response = make_response(
        {
            'body': user_input,
            'status': 200
        }
    )
    return response


if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0',port=5000, debug=True)
 #