from flask import Flask, make_response, request
import os
import time 

app = Flask(__name__)

# Step 1 #

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

# Step 2 #

@app.route('/repeat')
def repeat():
    foo = request.args.get("input", "")  
    response = make_response(
        {
            "body": foo,
            "status": 200
        }
    )
    return response

# Step 3 #

@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'response': 'OK',
            'status': 200
        }
    )
    return response

# Step 4 #

@app.route('/hang')
def hang():
    while True:
        time.sleep(1)
        
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002)) 
    app.run(host="0.0.0.0", port=port, threaded=False) 
