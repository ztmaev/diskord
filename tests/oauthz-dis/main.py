import json
import os
import sqlite3
import subprocess
import threading
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from zenora import APIClient

from config import token, client_secret, redirect_uri, oauth_url

client = APIClient(token, client_secret=client_secret)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/media'
secret = "maevisgod"
app.secret_key = secret

upload_dir = "temp/files/media"
webhook_file = "flask_webhook_bridge.py"

db_name = 'test.db'
admin_ids = ["maev"]


def generate_temp_uuid():
    return str(uuid.uuid4())[:18]


def execute_command(command):
    print(command)
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
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username text, user_id integer, discriminator integer, avatar_url text, bot integer, locale text, email text, bio text, has_mfa integer, verified integer)''')
    conn.commit()
    conn.close()
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


def get_user_id():
    user_id = session.get("user_id")
    if user_id:
        return user_id
    else:
        return None


@app.route("/")
def index():
    return render_template("index.html", oauth_url=oauth_url)


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

    save_user(user)

    session["username"] = username
    session["user_id"] = user_id
    session["avatar_url"] = avatar_url

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route('/upload', methods=['POST'])
def upload():
    if "user_id" not in session:
        flash("Log in to upload files")
        return redirect(url_for("index"))

    owner_id = get_user_id()
    verify_directories_exist()
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

            # execute
            command = ["python3", webhook_file, uuid_filename, temp_uuid, "file", owner_id]
            # execute
            thread = threading.Thread(target=execute_command, args=(command,))
            thread.start()

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

                # master(url, temp_uuid, is_url=True)
                return redirect(url_for('index'))

        flash('No file uploaded')
        return redirect(url_for('index'))

    flash('No file uploaded')
    return redirect(url_for('index'))


# url
@app.route('/url/<path:url>')
def url(url):
    if "user_id" not in session:
        flash("Log in to view this page")
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
@app.route('/list')
def uploads_list(key):
    if "user_id" not in session:
        flash("Log in to view this page.")
        return redirect(url_for("index"))

    user_id = get_user_id()
    if user_id not in admin_ids:
        flash("You are not allowed to view this page")
        return redirect(url_for("index"))
    else:
        uploads = os.listdir("db_dir")
        if len(uploads) == 0:
            return "No uploads"
        else:
            return render_template('uploads.html', uploads=uploads)


# return upload json
# /uploads/<filename>
@app.route('/uploads/<filename>')
def uploads(filename):
    if "user_id" not in session:
        flash("Log in to view this page.")
        return redirect(url_for("index"))

    try:
        with open(f"db_dir/{filename}", "r") as f:
            content = json.load(f)
        return jsonify(content)
    except Exception as e:
        return "File not found"


# error
@app.errorhandler(404)
def page_not_found(e):
    return """
        <h1>404</h1>
        <p>The resource could not be found.</p>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
