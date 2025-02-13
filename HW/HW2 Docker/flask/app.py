from flask import Flask, make_response, request, jsonify
import os

port = os.getenv('PORT')
app = Flask(__name__)

@app.route('/hang', methods=['GET'])
def hang():
    while True:
        pass

@app.route('/repeat', methods=['GET'])
def repeat():
    input = request.args.get('input')
    return jsonify(
        {
            "body": input,
            "status": 200
        }
    )

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
    app.run(host='0.0.0.0', debug=True, port=port, threaded=False)



