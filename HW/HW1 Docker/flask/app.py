import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return {"response": "Hello, World!", "status": 200}

@app.route('/repeat', methods=['GET'])
def repeat():
    input_value = request.args.get('input', default='No input provided')  # Improved default message
    return {
        "body": input_value,
        "status": 200
    }, 200

@app.route('/healthcheck', methods=['GET'])  # Optional health check route
def healthcheck():
    return  {
  "body": "OK",
  "status": 200
    }, 200

@app.route('/hang', methods=['GET'])
def hang():
    while True:
        pass  # Infinite loop


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Ensure this is set to the correct port
    app.run(host='0.0.0.0', port=port,  threaded=False)