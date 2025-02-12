from flask import Flask, jsonify, request

app = Flask(__name__)

#  Existing default route
@app.route('/')
def hello():
    return jsonify({"response": "Hello, World!", "status": 200})

#  Route with GET Parameter (e.g., /greet?name=Ken)
@app.route('/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Guest')
    return jsonify({"message": f"Hello, {name}!"})

#  Expose additional status endpoint
@app.route('/status')
def status():
    return jsonify({"status": "OK", "message": "Service is running"})

#  Health Check Endpoint (for Docker health checks)
@app.route('/health')
def health():
    return jsonify({"health": "good"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))  # Default to 5001 instead of 5000
    app.run(host="0.0.0.0", port=port, debug=True)


