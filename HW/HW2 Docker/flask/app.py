from flask import Flask, request, jsonify

# Define the Flask app instance
app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'response': 'Hello, World!',
        'status': 200
    })

@app.route('/add', methods=['GET'])
def add():
    a = request.args.get('a', type=int)  # Extract 'a' as an integer
    b = request.args.get('b', type=int)  # Extract 'b' as an integer
    if a is None or b is None:  # Validate inputs
        return jsonify({'error': 'Invalid parameters'}), 400
    return jsonify({'result': a + b}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

