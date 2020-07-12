from flask import Flask, request, jsonify
import psycopg2
import dbconf
import re

app = Flask(__name__)


@app.route('/')  # main url address
def main():
    return 'Hello world in "/" directory '


@app.route('/api', methods=['GET'])  # api url address with something information
def api_get():
    return '<h1>This is my own API</h1>'


@app.route('/api/image/resize', methods=['POST'])  # url address for loading image for resize
def upload_image():
    identificator = insert()
    return jsonify(identificator)


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


def insert():
    status = ("success", "processing", "failed")

    conn = dbconf.connection_db()  # connection string for connect to DB

    curs = conn.cursor()
    query_insert = f"INSERT INTO status (status) VALUES ('{status[1]}') "
    curs.execute(query_insert)

    conn.commit()
    query_last_value = "SELECT id FROM status ORDER BY id DESC LIMIT 1"
    curs.execute(query_last_value)
    last_value = curs.fetchone()

    conn.close()
    last_value = re.sub("\D", "", str(last_value))
    return last_value
