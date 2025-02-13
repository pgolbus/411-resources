from flask import Flask, make_response
import os 
import request

app = Flask(__name__)
@app.route('/')
def input():
    repeat = make repeat(
        {
            'repeat': request.args.get('input'),
            'status' = 200
                  }
    return repeat
@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

# asked chatgpt: "How do I expose a function as both /health and /healthcheck using python"
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
    app.run(host=os.getenv(), debug=True)
