# simple page with upload form
import os
import subprocess
import threading
import uuid
import json

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/media'
secret = "maevisgod"
app.secret_key = secret


def generate_temp_uuid():
    return str(uuid.uuid4())[:18]


def execute_command(command):
    subprocess.run(command)


def verify_directories_exist():
    if not os.path.exists("temp/files/media"):
        os.makedirs("temp/files/media")

    if not os.path.exists("temp/files/out_split"):
        os.makedirs("temp/files/out_split")

    if not os.path.exists("temp/files/out_merged"):
        os.makedirs("temp/files/out_merged")

    if not os.path.exists("temp/metadata"):
        os.makedirs("temp/metadata")


# page
@app.route('/')
def index():
    return render_template('index.html')


# upload
@app.route('/upload', methods=['POST'])
def upload():
    verify_directories_exist()
    upload_dir = "temp/files/media"
    if request.method == 'POST':
        try:
            file = request.files['file']
        except Exception as e:
            file = None
        if file:
            filename = file.filename
            temp_uuid = generate_temp_uuid()
            uuid_filename = temp_uuid + "_" + filename
            file.save(os.path.join(upload_dir, uuid_filename))
            # print('File successfully uploaded')

            # master(uuid_filename, temp_uuid, is_url=False)
            # run master in thread
            # threading.Thread(target=master, args=(uuid_filename, temp_uuid, False)).start()

            file = "flask_webhook_bridge.py"

            # execute
            command = ["python3", file, uuid_filename, temp_uuid, "file"]
            # execute
            subprocess.run(command)

            return redirect(url_for('index'))

        else:
            # download from url
            url = request.form['url']
            if url:
                filename = url
                temp_uuid = generate_temp_uuid()
                uuid_filename = temp_uuid + "_" + filename
                file = "flask_webhook_bridge.py"

                # execute
                command = ["python3", file, filename, temp_uuid, "url"]
                # execute
                # subprocess.run(command)
                thread = threading.Thread(target=execute_command, args=(command,))
                thread.start()

                # master(url, temp_uuid, is_url=True)
                return redirect(url_for('index'))

        flash('No file uploaded')
        return redirect(url_for('index'))

    flash('No file uploaded')
    return redirect(url_for('index'))

# return uploads
# /uploads/list
@app.route('/uploads/list')
def uploads_list():
    uploads = os.listdir("db_dir")
    return render_template('uploads.html', uploads=uploads)

# return upload json
# /uploads/<filename>
@app.route('/uploads/<filename>')
def uploads(filename):
    with open(f"db_dir/{filename}", "r") as f:
        content = json.load(f)
    return jsonify(content)

# init
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4321)
