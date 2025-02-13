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

@app.route('/health')
@app.route('/healthcheck')
def healthcheck():
    response = make_response(
        {
            'response': 'OK',
            'status': 200
        }
    )
    return response

@app.route('/repeat', methods=['GET'])
def repeat():
    user_input = request.args.get("input", "no input")
    response = make_response(
        {
            'response':user_input,
            'status':200
        }
    )
    return response

@app.route('/hang', methods=['GET'])
def hang():
    x = 0
    while x>=0:
        x+=1
    response = make_response(
        {
            'response':"Failed, this won't be reached though",
            'status':500
        }
    )
    return response

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    port_run = int(os.getenv('PORT', default=5001))
    app.run(host="0.0.0.0", port=port_run, debug = True, threaded=False)
