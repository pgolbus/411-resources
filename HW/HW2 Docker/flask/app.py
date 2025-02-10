from flask import Flask, make_response,jsonify, request
import os


app = Flask(__name__)

@app.route('/repeat', methods=['GET'])

def repeat():
    user_input = request.args.get('input', '')  # Get the 'input' parameter or use an empty string if missing
    return jsonify({"body": user_input, "status": 200})


def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
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

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    osVar = os.getenv("PORT", 5002)
    app.run(host='0.0.0.0',port=osVar, debug=True)
