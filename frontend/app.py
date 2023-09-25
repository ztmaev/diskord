from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
import os

app = Flask(__name__)
app.secret_key = "MaeV"

users = ['maev', 'ian']
notifs = []
notif_id = 0


@app.route('/')
def index():
    oauth_url = ""
    files = [
        {"filename": "Img.txt", "size": "21.8 kb", "url": ""},
        {"filename": "maev.zip", "size": "179 mb", "url": ""},
        {"filename": "windows_10.iso", "size": "4.8 gb", "url": ""},
        {"filename": "Stash_bk_7_23.rar", "size": "7.61 gb", "url": ""}
    ]

    return render_template("homepage.html", oauth_url=oauth_url, files=files)


@app.route('/download')
def download():
    return render_template("download.html")


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

    flash(f"success_Hello {username}")

    return jsonify({'message': 'Login successful'}), 200


@app.route('/oauth')
def oauth():
    flash("success_Oauth Successful")
    session["username"] = "oauth"
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


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files[]')
    print(uploaded_files)

    # Check if files were uploaded
    if not uploaded_files:
        return jsonify({'error': 'No files were uploaded'}), 400

    for file in uploaded_files:
        if file.filename == '':
            continue  # Skip empty file inputs

        # Save the file to the UPLOAD_FOLDER
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return jsonify({'message': 'Upload successful'}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
