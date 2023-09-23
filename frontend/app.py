from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash

app = Flask(__name__)
app.secret_key = "MaeV"

users = ['maev', 'ian']


@app.route('/')
def index():
    oauth_url = ""
    return render_template("homepage.html", oauth_url=oauth_url)


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
    {"id": 1, "message": "Notification edit test."},
    {"id": 2, "message": "Notification 2"},
]

@app.route('/notifications')
def get_notifications():
    return jsonify(notifications)



if __name__ == "__main__":
    app.run(debug=True)
