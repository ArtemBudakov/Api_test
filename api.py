from flask import Flask, request, jsonify

app = Flask(__name__)

'''main url address'''


@app.route('/')
def main():
    return 'Hello world in "/" directory '


@app.route('/api', methods=['GET'])  # api url address with something information
def api_get():
    return '<h1>This is my own API</h1>'


@app.route('/api/image/resize', methods=['POST'])  # url address for loading image for resize
def get_image():
    pass


@app.route('/api/status', methods=['GET'])  # url address for asking status of resizing by identificator
def get_status():
    pass
