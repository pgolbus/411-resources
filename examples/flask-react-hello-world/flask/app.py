from flask import Flask, jsonify, make_response
from flask import request
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)  # This will allow the React front-end to communicate with the Flask back-end

@app.route('/repeat', methods=['GET'])
def hello_world():
    user_input = request.args.get("input", "No input provided")
    return make_response(jsonify({"body": user_input, "status": 200}), 200)

@app.route('/health', methods=['GET'])
@app.route('/healthcheck', methods=['GET'])

def health():
    return make_response(jsonify({"body": "OK", "status": 200}), 200)

@app.route('/hang', methods=['GET'])
def hang():
    while True:
        pass
    
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=False) 
