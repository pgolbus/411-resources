from flask import Flask, make_response, request
from flask import Flask, make_response
import time
import os  # Import the os module

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
    user_input = request.args.get("input", "No input provided")  # Default if no param
    response = make_response(
        {
            "body": user_input,
            "status": 200
        }
    )
    return response

@app.route('/health')
@app.route('/healthcheck')
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
    while True:
        time.sleep(1)  

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=False)  