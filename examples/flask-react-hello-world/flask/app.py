from flask import Flask, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will allow the React front-end to communicate with the Flask back-end

@app.route('/')
def hello_world():
    return make_response(jsonify({"message": "Hello, World!"}), 200)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
