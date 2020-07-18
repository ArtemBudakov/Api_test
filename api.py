from flask import Flask, request, jsonify
from PIL import Image
import dbconf
import re
import threading

app = Flask(__name__)


@app.route('/', methods=['GET'])  # main url address
def main():
    return 'Hello world in "/" directory '


@app.route('/api', methods=['GET'])  # api url address with something information
def api_get():
    return '<h1>This is my own API</h1>'


@app.route('/api/image/resize', methods=['POST'])  # url address for loading image for resize
def get_image():
    if 'height' not in request.args or (int(request.args['height']) < 1) or (int(request.args['height']) > 9999):
        return "Error: write height for resize between 1 and 9999"
    elif 'width' not in request.args or (int(request.args['width']) < 1) or (int(request.args['width']) > 9999):
        return "Error: write width for resize between 1 and 9999"

    height, width = int(request.args['height']), int(request.args['width'])

    file = request.files['image']
    img = Image.open(file.stream)
    if (img.format is 'JPEG') or (img.format is 'PNG'):
        fmt = img.format
        ins = CRUD()
        identificator = ins.insert()
        path = f'pictures/original_{identificator}.{fmt}'
        img.save(path)
        HandlerImages(identificator=identificator, path=path, height=height, width=width, fmt=fmt)
        return identificator
    return f'You mast use PNG or JPEG formats. Your format is {img.format} !'

    # return jsonify({'msg': 'success', 'size': [img.width, img.height]})


@app.route('/api/status', methods=['GET'])  # url address for asking status of resizing by identificator
def get_status():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    conn = dbconf.connection_db()  # connection string for connect to DB

    curs = conn.cursor()
    query_status = f"SELECT status FROM status WHERE id = {id}"
    curs.execute(query_status)
    status_value = curs.fetchone()

    conn.close()

    if status_value is None:
        return "Error: the entered identifier does not exist"
    status_value = re.sub("[\W\d_]", "", str(status_value))
    return jsonify(status_value)


class CRUD(object):

    def __init__(self, identificator=None, path=None):
        self.status = ("success", "processing", "failed")
        self.identificator = identificator
        self.path = path

    def insert(self):
        conn = dbconf.connection_db()  # connection string for connect to DB

        curs = conn.cursor()
        query_insert = f"INSERT INTO status (status) VALUES ('{self.status[1]}') "
        curs.execute(query_insert)

        conn.commit()
        query_last_value = "SELECT id FROM status ORDER BY id DESC LIMIT 1"
        curs.execute(query_last_value)
        last_value = curs.fetchone()

        conn.close()
        last_value = re.sub("\D", "", str(last_value))
        return last_value

    def update(self):
        identificator = self.identificator
        path = self.path
        conn = dbconf.connection_db()  # connection string for connect to DB

        curs = conn.cursor()
        query_insert = f"UPDATE status SET status = '{self.status[0]}', path = '{path}' WHERE id = {identificator} "
        curs.execute(query_insert)

        conn.commit()
        conn.close()


class HandlerImages(object):
    """ Threading class
    The resize() method will be started and it will run in the background.
    """

    def __init__(self, identificator, path, height, width, fmt):
        self.identificator = identificator
        self.path = path
        self.height = height
        self.width = width
        self.fmt = fmt

        thread = threading.Thread(target=self.resize, args=())
        thread.daemon = False  # Daemonize thread (executing after application was finish)
        thread.start()  # Start the execution

    def resize(self):
        identificator = self.identificator
        path = self.path
        height = self.height
        width = self.width
        fmt = self.fmt

        image = Image.open(path)
        img_resized = image.resize((height, width))
        path_resized = f'pictures/resized_{identificator}.{fmt}'
        img_resized.save(f'{path_resized}')
        up = CRUD(identificator, path_resized)
        up.update()


