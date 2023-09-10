# simple page with upload form
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from flask_webhook_bridge import master
import os
import uuid
import threading
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/media'
secret = "maevisgod"
app.secret_key = secret

python_script = "flask_webhook_bridge.py"


def generate_temp_uuid():
    return str(uuid.uuid4())[:18]


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

            subprocess.call(["python", python_script, uuid_filename, temp_uuid, False])

            return redirect(url_for('index'))

        else:
            # download from url
            url = request.form['url']
            if url:
                temp_uuid = generate_temp_uuid()
                # master(url, temp_uuid, is_url=True)
                subprocess.call(["python", python_script, uuid_filename, temp_uuid, True])

                return redirect(url_for('index'))



        flash('No file uploaded')
        return redirect(url_for('index'))

    flash('No file uploaded')
    return redirect(url_for('index'))


# init
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4321)
