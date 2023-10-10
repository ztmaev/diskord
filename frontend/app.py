import json
import os

from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash, send_file

app = Flask(__name__)
app.secret_key = "MaeV"

upload_dir = "uploads"

deletion_requests = []

users = ['maev', 'ian']
accounts = ['maev@maev.site', 'admin@maev.site']
notifs = []
notif_id = 0


def convert_size(size_in_bytes):
    # Define the conversion factors
    GB = 1024 * 1024 * 1024
    MB = 1024 * 1024
    KB = 1024

    if size_in_bytes >= GB:
        size = size_in_bytes / GB
        size_unit = "GB"
    elif size_in_bytes >= MB:
        size = size_in_bytes / MB
        size_unit = "MB"
    elif size_in_bytes >= KB:
        size = size_in_bytes / KB
        size_unit = "KB"
    else:
        size = size_in_bytes
        size_unit = "Bytes"

    return f"{size:.2f} {size_unit}"


def filelist(directory_path='uploads'):
    files_data = []

    # Check if the directory exists
    if not os.path.exists(directory_path):
        return json.dumps({"error": "Directory does not exist"})

    # Iterate over the files in the directory
    num = 0
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            # Get file size in bytes
            size_bytes = os.path.getsize(file_path)

            # Convert bytes to kilobytes (KB)
            size = convert_size(size_bytes)

            # Create a dictionary for each file
            file_info = {
                "filename": filename,
                "size": size,
                "date": f"10:05 {num}/08/23",
                "id": (num + 1),  # You can fill in the URL if needed
            }
            files_data.append(file_info)
            num = num + 1

    # Convert the list of dictionaries to JSON
    json_data = json.dumps(files_data, indent=4)

    return json_data


@app.route('/')
def index():
    oauth_url = ""

    files_2 = json.loads(filelist())

    return render_template("homepage.html", oauth_url=oauth_url, files=files_2)


@app.route('/setpassword', methods=['POST'])
def setpassword():
    data = request.get_json()
    password = data.get('bufferPass', '')

    if not password:
        return jsonify({'message': 'Please enter a password.'}), 400
    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400

    return jsonify({'message': 'Password set successfully.'}), 200


@app.route('/updatepassword', methods=['POST'])
def updatepassword():
    data = request.get_json()
    password = data.get('bufferPass', '')

    if not password:
        return jsonify({'message': 'Please enter a password.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400

    return jsonify({'message': 'Password changed successfully.'}), 200


@app.route('/update_username', methods=['POST'])
def update_username():
    return jsonify({'message': 'Log in again with discord to update your username.'}), 200


@app.route('/linkedaccounts', methods=['POST'])
def linkedaccounts():
    return jsonify(accounts), 200

@app.route('/update_filename', methods=['POST'])
def update_filename():
    data = request.get_json()
    filename = data.get('fileName', '')
    print(filename)
    return jsonify({'message': 'Filename updated successfully.'}), 200


@app.route('/service-worker.js')
def service_worker():
    return send_file('static/service-worker.js')


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/uploads')
def uploads():
    return render_template('uploads.html')


# Account deletion
@app.route('/delete_account', methods=['POST'])
def delete_account():
    deletion_requests.append(session['username'])
    return jsonify(
        {'message': 'Your account will be deleted in 30 days, log in during that period to stop the deletion.'}), 200


@app.route('/cancel_deletion', methods=['POST'])
def cancel_deletion():
    # deletion_requests.pop(session['username'])
    session['deletion'] = False
    return jsonify(
        {'message': 'Account deletion canceled'}), 200


@app.route('/account')
def account():
    account_info = {
        "storage_size": "73.48 GB",
        "files_number": 18730
    }

    return render_template("account.html", account_info=account_info)


@app.route('/linkemail', methods=['POST'])
def linkemail():
    data = request.get_json()
    verification_code = data.get('tfaCode', '')
    # print(verification_code)

    # fetch email and code from db

    return jsonify(
        {'message': 'Email linked successfully'}), 200

@app.route('/unlinkemail', methods=['POST'])
def unlinkemail():
    data = request.get_json()
    email = data.get('email', '')
    accounts.pop(email)
    return jsonify(
        {'message': 'Email unlinked successfully'}), 200

@app.route('/requestemailcode', methods=['POST'])
def requestemailcode():
    # generate code send it to email and save it to db
    data = request.get_json()
    email = data.get('newEmail', '')
    if len(accounts) >= 3:
        return jsonify(
            {'message': 'Maximum number of accounts connected.'}), 400

    if email in accounts:
        return jsonify(
            {'message': 'Email already linked to your account.'}), 400
    else:
        accounts.append(email)
        return jsonify(
            {'message': 'Code has been sent to your email.'}), 200


@app.route('/ac1')  # Test
def ac1():
    return render_template('account-dashboard.html')


@app.route('/files')
def files():
    files = json.loads(filelist())

    return jsonify(files)


@app.route('/view/<path:id>')
def view(id):
    print(id)
    file_info = {
        "filename": "Archive.rar",
        "filesize": "1.73 GB",
        "date_uploaded": "8:56 am | 15th June 23",
        "filetype_icon": "logo.png",
        "json": {
            "chunks_number": "14",
            "chunks_size": "20",
            "files": {
                "1": "",
                "2": ""

            }

        }
    }

    return render_template("file-view.html", file_info=file_info)


@app.route('/download')
def download():
    file_info = {
        "filename": "Archive.rar",
        "filesize": "1.73 GB",
        "date_uploaded": "8:56 am | 15th June 23",
        "filetype_icon": "logo.png",
        "json": {
            "chunks_number": "14",
            "chunks_size": "20",
            "files": {
                "1": "",
                "2": ""

            }

        }
    }
    return render_template("download.html", file_info=file_info)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Get the JSON data sent from the client

    username = data.get('username', '')
    password = data.get('password', '')

    # Server-side validation and authentication logic
    if not username or not password:
        return jsonify({'message': 'Please enter your username and password or use Discord login.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400

    if len(password) > 16:
        return jsonify({'message': 'Password should be less than 16 characters.'}), 400

    if username not in users:
        return jsonify({'message': 'Invalid username or password.'}), 300

    session['username'] = username

    print(deletion_requests)

    if session['username'] in deletion_requests:
        session['deletion'] = True
        flash('success_Your account is pending deletion, cancel it on the accounts page.')
        return jsonify({'message': 'Login successful'}), 200
    else:
        flash(f"success_Hello {username}")
        return jsonify({'message': 'Login successful'}), 200


@app.route('/oauth')
def oauth():
    flash("success_Oauth Successful")
    session["username"] = "oauth"
    session["s_account"] = True

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash("success_Logged out")
    return redirect(url_for('index'))


# Notifications
notifications = [
    {"id": 1, "message": "Notification edit test 79."},
    {"id": 2, "message": "Notification 2"},
    {"id": 3, "message": "Notification with url", "url": "https://maev.site"}
]


def update_notif(action, id=None):
    if action == "add":
        if id is None:
            notifications.append({"id": 3, "message": "new notif"})
        else:
            number_of_notifs = int(id)
            try:
                id_gen = notifications[-1]["id"] + 1
            except:
                id_gen = 0

            for i in range(number_of_notifs):
                notifications.append({"id": id_gen, "message": f"new notif {id_gen}"})
                id_gen += 1

    elif action == "remove":
        notif_id = int(id)
        for notif in notifications:
            if notif["id"] == notif_id:
                notifications.remove(notif)
                break


@app.route('/notifications')
def get_notifications():
    return jsonify(notifications)


@app.route('/addnotif')
def add_notification():
    update_notif("add")
    return redirect(url_for('index'))


@app.route('/addnotif/<int:number>')
def add_notification_id(number):
    update_notif("add", number)
    return redirect(url_for('index'))


@app.route('/removenotif')
def remove_notification():
    notification_id = request.args.get('id')
    update_notif("remove", notification_id)
    return jsonify({'message': 'removed notif successfully'}), 200


@app.route('/clearnotifs')
def clearnotifs():
    notifications.clear()
    return jsonify({'message': 'cleared notifs successfully'}), 200


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files[]')

    # Check if files were uploaded
    if not uploaded_files:
        return jsonify({'error': 'No files were uploaded'}), 400

    for file in uploaded_files:
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({'message': 'Upload successful'}), 200


# info pages
# Invite-bot
@app.route('/invitebot')
def invitebot():
    link = 'www.google.com'
    return render_template('info-pages/invite-bot.html', discord_bot_invite = link)

@app.route('/join_community')
def join_community():
    community_link = "www.google.com"
    return render_template('info-pages/join-community.html', discord_community_join = community_link)

@app.route('/get_help')
def get_help():
    return render_template('info-pages/account-file-recovery.html')


@app.route('/self_recovery')
def self_recovery():
    return render_template('info-pages/account-file-recovery.html')
    # TODO: here



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
