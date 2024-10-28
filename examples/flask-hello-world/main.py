from flask import Flask, jsonify, make_response

app = Flask(__name__)

@app.route('/')
def main():
    app.logger.info("Hello World!")
    response = {
        "message": "Hello World!",
        "status": "success",
    }
    return make_response(jsonify(response), 200)

@app.route('/health')
def health_check():
    app.logger.info("Health Check")
    health_status = {
        "status": "healthy",
    }
    return make_response(jsonify(health_status), 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
