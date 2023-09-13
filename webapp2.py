import json
import os
import sqlite3
import subprocess
import threading
import time
import uuid

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from zenora import APIClient

from config import token, client_secret, redirect_uri, oauth_url
from file_management import merge_files

client = APIClient(token, client_secret=client_secret)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/media'
secret = "maevisgod"
app.secret_key = secret

upload_dir = "temp/files/media"
webhook_file = "flask_webhook_bridge.py"

db_name = 'test.db'
admin_ids = ["1135978748689256468"]


def get_db():
    db = mysql.connector.connect(
        host="arc.maev.site",
        user="maev",
        passwd="Alph4",
        port="3306",
        database="test"
    )
    return db


def generate_temp_uuid():
    return str(uuid.uuid4())[:18]


def execute_command(command):
    # print(command)
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


def save_user(user):
    is_new = False
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username text, user_id integer, discriminator integer, avatar_url text, bot integer, locale text, email text, bio text, has_mfa integer, verified integer)''')
    conn.commit()
    conn.close()

    # check if user exists
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user["user_id"],))
    result = c.fetchone()
    conn.close()
    if result:
        # update user
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            "UPDATE users SET username=?, discriminator=?, avatar_url=?, bot=?, locale=?, email=?, bio=?, has_mfa=?, verified=? WHERE user_id=?",
            (
                user["username"], user["discriminator"], user["avatar_url"], user["bot"], user["locale"],
                user["email"], user["bio"], user["has_mfa"], user["verified"], user["user_id"]))
        conn.commit()
        conn.close()

        return is_new
    else:
        # save user
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (
                      user["username"], user["user_id"], user["discriminator"], user["avatar_url"], user["bot"],
                      user["locale"],
                      user["email"], user["bio"], user["has_mfa"], user["verified"]))
        conn.commit()
        conn.close()

        is_new = True
        return is_new


def get_user_id():
    user_id = session.get("user_id")
    if user_id:
        return str(user_id)
    else:
        return None


@app.route("/")
def index():
    user_id = get_user_id()
    if user_id:
        # user uploads
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM files WHERE owner_id=?", (user_id,))
            result = c.fetchall()
            conn.close()

            uploads = []
            for entry in result:
                upload = {
                    "file_id": entry[0],
                    "file_name": entry[1]
                }
                uploads.append(upload)
        except Exception as e:
            uploads = []
    else:
        uploads = []

    return render_template("index.html", oauth_url=oauth_url, uploads=uploads)


@app.route("/oauth/callback")
def callback():
    code = request.args.get("code")
    access_token = client.oauth.get_access_token(code, redirect_uri).access_token

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()

    # parse_user
    username = current_user.username
    user_id = current_user.id
    discriminator = current_user.discriminator
    avatar_url = current_user.avatar_url
    bot = current_user.is_bot
    locale = current_user.locale
    email = current_user.email
    bio = current_user.bio
    has_mfa = current_user.has_mfa_enabled
    verified = current_user.is_verified

    # session
    # create json and save to db
    user = {
        "username": username,
        "user_id": user_id,
        "discriminator": discriminator,
        "avatar_url": avatar_url,
        "bot": bot,
        "locale": locale,
        "email": email,
        "bio": bio,
        "has_mfa": has_mfa,
        "verified": verified
    }

    is_new_user = save_user(user)

    session["username"] = username
    session["user_id"] = user_id
    session["avatar_url"] = avatar_url

    # admin_status
    if user_id in admin_ids:
        session["admin"] = True
    else:
        session["admin"] = False

    if is_new_user:
        flash("success_Welcome to diskord " + username + "!")
    else:
        flash("success_Logged in successfully as " + username)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("success_Logged out")
    return redirect(url_for("index"))


@app.route('/upload', methods=['POST'])
def upload():
    if "user_id" not in session:
        flash("error_Log in to upload files")
        return redirect(url_for("index"))

    owner_id = get_user_id()
    verify_directories_exist()
    if request.method == 'POST':
        try:
            files = request.files.getlist('files[]')
        except Exception as e:
            files = []

        if files:
            for file in files:
                if file:
                    filename = file.filename
                    temp_uuid = generate_temp_uuid()
                    uuid_filename = temp_uuid + "_" + filename
                    file.save(os.path.join(upload_dir, uuid_filename))

                    # Execute
                    command = ["python3", webhook_file, uuid_filename, temp_uuid, "file", owner_id]
                    thread = threading.Thread(target=execute_command, args=(command,))
                    thread.start()
                    time.sleep(1)

            flash('success_Files uploaded successfully')
            return redirect(url_for('index'))

        else:
            # download from url
            url = request.form['url']
            if url:
                filename = url
                temp_uuid = generate_temp_uuid()

                # execute
                command = ["python3", webhook_file, filename, temp_uuid, "url", owner_id]

                # execute
                thread = threading.Thread(target=execute_command, args=(command,))
                thread.start()

                flash('success_Url sent successfully')
                return redirect(url_for('index'))

        flash('error_No file uploaded')
        return redirect(url_for('index'))

    flash('error_No file uploaded')
    return redirect(url_for('index'))


# url
@app.route('/url/<path:url>')
def url(url):
    if "user_id" not in session:
        flash("error_Log in to view this page")
        return redirect(url_for("index"))

    owner_id = get_user_id()
    verify_directories_exist()
    filename = url
    temp_uuid = generate_temp_uuid()

    # execute
    command = ["python3", webhook_file, filename, temp_uuid, "url", owner_id]
    # execute
    # subprocess.run(command)
    thread = threading.Thread(target=execute_command, args=(command,))
    thread.start()

    # master(url, temp_uuid, is_url=True)
    return redirect(url_for('index'))


# return uploads
# /uploads/list
@app.route('/uploads')
def uploads_list():
    if "user_id" not in session:
        flash("error_Log in to view this page.")
        return redirect(url_for("index"))

    user_id = get_user_id()
    if user_id in admin_ids:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM files")
        result = c.fetchall()
        conn.close()

        uploads = []
        for entry in result:
            upload = {
                "file_id": entry[0],
                "file_name": entry[1]
            }
            uploads.append(upload)

        return render_template('uploads.html', uploads=uploads)

    # user uploads
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE owner_id=?", (user_id,))
    result = c.fetchall()
    conn.close()

    uploads = []
    for entry in result:
        upload = {
            "file_id": entry[0],
            "file_name": entry[1]
        }
        uploads.append(upload)

    return render_template('uploads.html', uploads=uploads)


# return upload json
# /uploads/<filename>
@app.route('/uploads/<file_id>')
def uploads(file_id):
    if "user_id" not in session:
        flash("error_Log in to view this page.")
        return redirect(url_for("index"))

    user_id = get_user_id()
    if user_id in admin_ids:
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM files WHERE file_id=?", (file_id,))
            result = c.fetchall()
            conn.close()

            uploads = []
            for entry in result:
                upload = {
                    "file_id": entry[0],
                    "file_name": entry[1],
                    "file_size": entry[2],
                    "chunks_number": entry[3],
                    "chunk_size": entry[4],
                    "file_type": entry[5],
                    "filetype_icon_url": entry[6],
                    "owner_id": entry[7],
                    "files": json.loads(entry[8])
                }
                uploads.append(upload)

            if len(uploads) == 1:
                return jsonify(uploads[0])
            else:
                flash("error_File not found")
                return redirect(url_for("index"))

        except Exception as e:
            return "File not found"

    else:
        # confirm user owns file
        # fetch file from db
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM files WHERE file_id=?", (file_id,))
        result = c.fetchone()
        conn.close()

        if result:
            # check if user owns file
            if str(result[7]) == user_id:
                # user owns file
                upload = {
                    "file_id": result[0],
                    "file_name": result[1],
                    "file_size": result[2],
                    "chunks_number": result[3],
                    "chunk_size": result[4],
                    "file_type": result[5],
                    "filetype_icon_url": result[6],
                    "files": json.loads(result[8])
                }
                # "owner_id": result[7],
                return jsonify(upload)
            else:
                flash("error_You don't own this file.")
                return redirect(url_for("index"))


# delete upload
# /uploads/delete/<file_id>
@app.route('/uploads/delete/<file_id>')
def uploads_delete(file_id):
    if "user_id" not in session:
        flash("error_Log in to view this page.")
        return redirect(url_for("index"))

    user_id = get_user_id()
    if user_id in admin_ids:
        # delete the file from db
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("DELETE FROM files WHERE file_id=?", (file_id,))
        conn.commit()
        conn.close()
        flash("success_File deleted.")
        return redirect(url_for("index"))
    else:
        # check if user owns file
        # fetch file from db
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM files WHERE file_id=?", (file_id,))
        result = c.fetchone()
        conn.close()

        if result:
            # check if user owns file
            if str(result[7]) == user_id:
                # user owns file
                # delete the file from db
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute("DELETE FROM files WHERE file_id=?", (file_id,))
                conn.commit()
                conn.close()
                flash("success_File deleted.")
                return redirect(url_for("index"))
            else:
                flash("error_You don't own this file.")
                return redirect(url_for("index"))


# download
@app.route('/download/<file_id>')
def download(file_id):
    if "user_id" not in session:
        flash("error_Log in to view this page.")
        return redirect(url_for("index"))

    # fetch file from db and create json
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE file_id=?", (file_id,))
    result = c.fetchone()
    conn.close()

    if result:
        # parse
        file_id = result[0]
        file_name = result[1]
        file_size = result[2]
        chunks_number = result[3]
        chunk_size = result[4]
        file_type = result[5]
        filetype_icon_url = result[6]
        owner_id = result[7]
        files = json.loads(result[8])

        # create json
        file_info_json = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "chunks_number": chunks_number,
            "chunk_size": chunk_size,
            "file_type": file_type,
            "filetype_icon_url": filetype_icon_url,
            "owner_id": owner_id,
            "files": json.loads(result[8])
        }
    else:
        flash("error_File not found")
        return redirect(url_for("index"))

    # check if user owns file or is admin
    user_id = get_user_id()
    if user_id in admin_ids or user_id == str(owner_id):
        # flash(f"success_Prepairing your file. Please wait...")
        # merge files
        file_path = merge_files(file_info_json)
        # print(file_path)

        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            flash("error_File not found")
            return redirect(url_for("index"))

        # threading.Thread(target=merge_files, args=(file_info_json,)).start()
        # return redirect(url_for("index"))
    else:
        flash("error_You don't own this file.")
        return redirect(url_for("index"))


# error
@app.errorhandler(404)
def page_not_found(e):
    return """
        <h1>404</h1>
        <p>The resource could not be found.</p>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

# TODO: add file deletion
# TODO: add notifications
# TODO: optimise merging and download
# TODO: load balancing
# TODO: switch to mysql
