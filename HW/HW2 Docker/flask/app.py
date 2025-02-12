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
    user_input = request.args.get('input', '')

    response = make_response(
        {
            'body': user_input,
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
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)
