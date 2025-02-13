from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def hello():
    response = jsonify({
        'response': 'Hello, World!',
        'status': 200
    })
    return response

@app.route('/repeat', methods=['GET'])
def repeat():
    # Get the "input" parameter from the GET request
    user_input = request.args.get("input", "No input provided")  # Default if not found
    response = {
        "body": user_input,
        "status": 200
    }
    return jsonify(response), 200 

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = jsonify({
        "body": "OK",
        "status": 200
    })
    return response

@app.route('/hang')
def hang():
    while True:
        time.sleep(1)

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)
