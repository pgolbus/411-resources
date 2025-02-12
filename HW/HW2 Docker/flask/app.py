from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    response = jsonify(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response


@app.route('/status')
def status():
   return jsonify({
    'status': 'OK',
     'message': 'Service is running'
    })

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', debug=True)
