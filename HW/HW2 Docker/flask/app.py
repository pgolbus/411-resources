from flask import Flask, make_response, request
import os 

app = Flask(__name__)
port = int(os.getenv("PORT", 5002))

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
    input = request.args.get('input', '')
    response = make_response ({
        'body': input,
        'status': 200

    })
    return response

@app.route('/health')
@app.route('/healthcheck')
def hello1():
    response = make_response(
        {
            'response': 'OK',
            'status': 200
        }
    )
    return response

@app.route('/hang')
def hangfunction():
    while True:
        continue

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    
    app.run(host='0.0.0.0', port=5002, threaded=False)
