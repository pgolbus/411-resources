import os

from flask import Flask, make_response, request, jsonify #latter 2 imports for task 2

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

#as per step 2 instructions.."repeat" part
@app.route('/repeat')
def repeat():
    user_input = request.args.get("input", "no input") #no input msg if the input is missing
    return jsonify({"body": user_input, "status": 200})

#as per step 3 instructions.."health-healthcheck" part
@app.route('/health')
@app.route('/healthcheck') #apparently can do 2 app.routes like this
def health():
    return jsonify({"body": "OK", "status": 200})

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port = int(os.getenv("PORT", 5002)) #as per part1 instructions
    app.run(host='0.0.0.0', port=port)
