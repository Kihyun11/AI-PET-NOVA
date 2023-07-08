from flask import Flask, request
import threading
import time

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    print("check")
    data = request.json
    name = data.get('name')
    # Process the received data as needed
    print('Received data:', data)
    return 'Data received'


if __name__ == '__main__':
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)
    
    # Create and start the separate thread
    #thread = threading.Thread(target=thread_function)
    #thread.start()
