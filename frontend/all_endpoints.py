import os
import subprocess
import uuid
import json
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from zenora import APIClient

from config import token, client_secret, redirect_uri, oauth_url
from files import process_upload_files

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
        database="Alpha1"
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
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Check if the user already exists in the 'users' table
        cursor.execute("SELECT id FROM users WHERE discord_id = %s", (str(user["user_id"]),))
        existing_user_id = cursor.fetchone()

        if existing_user_id:
            # User already exists, update their information
            cursor.execute("""
                UPDATE users
                SET username = %s, avatar = %s, emails = %s, date_updated = NOW()
                WHERE discord_id = %s
            """, (user["username"], user["avatar_url"], user["email"], str(user["user_id"])))

            # Update data in 'discord_info' table
            cursor.execute("""
                UPDATE discord_info
                SET username = %s, discriminator = %s, avatar_url = %s, is_bot = %s, locale = %s,
                email = %s, bio = %s, has_mfa = %s, verified = %s, date_updated = NOW()
                WHERE discord_id = %s
            """, (
                user["username"], user["discriminator"], user["avatar_url"], user["bot"], user["locale"],
                user["email"], user["bio"], user["has_mfa"], user["verified"], str(user["user_id"])))

            return False
        else:
            # User does not exist, insert new data into both tables
            cursor.execute("""
                INSERT INTO users (username, discord_id, avatar, emails, date_created, date_updated)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (user["username"], str(user["user_id"]), user["avatar_url"], user["email"]))

            cursor.execute("""
                INSERT INTO discord_info (username, discriminator, discord_id, avatar_url, is_bot, locale, email, bio, has_mfa, verified, date_created, date_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                user["username"], user["discriminator"], str(user["user_id"]), user["avatar_url"], user["bot"],
                user["locale"], user["email"], user["bio"], user["has_mfa"], user["verified"]))

        # Commit the changes to the database
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        # If an error occurs, rollback the transaction
        conn.rollback()
        print("Error saving user:", str(e))
        return False

def filelist():
    print(123)
    db = get_db()
    cursor = db.cursor()

    try:
        # Fetch data from the 'files' table with the user's ID
        cursor.execute("SELECT * FROM files WHERE owner_id = %s", (str(session["user_id"]),))
        files_data = []
        for file in cursor:
            file_data = {
                "id": file[2],
                "filename": file[1],
                "file_type": file[4],
                "size": file[6],
                "size_simple": file[7],
                "date": file[15],
                "date_updated": file[16]
            }
            files_data.append(file_data)
        cursor.close()
        json_data = json.dumps(files_data, indent=4)
        return json_data
    except Exception as e:
        print("Error fetching files:", str(e))
        return False


@app.route('/')
def index():
    return render_template("homepage.html", oauth_url=oauth_url)


# Account
@app.route('/account')
def account():
    account_info = {
        "storage_size": "73.48 GB",
        "files_number": 18730
    }
    return render_template("account.html", account_info=account_info)



@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return jsonify({'message': 'You are already logged in.'}), 400

    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    # Server-side validation and authentication logic
    if not username or not password:
        return jsonify({'message': 'Please enter your username and password or use Discord login.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400

    if len(password) > 16:
        return jsonify({'message': 'Password should be less than 16 characters.'}), 400

    if 'username' in session:
        return jsonify({'message': 'You are already logged in.'}), 400

    # check if user exists in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username.lower(),))
    password_db = cursor.fetchone()
    if password_db is None or password_db[0] is None or password_db[0].strip() == "":
        return jsonify({'message': 'Incorrect username or password.'}), 400

    if password_db[0] != password:
        return jsonify({'message': 'Incorrect username or password.'}), 400

    # get user info from db
    cursor.execute("SELECT discord_id, avatar, await_username_update, await_deletion, deleted FROM users WHERE username = %s", (username.lower(),))
    user_info = cursor.fetchone()
    user_id = user_info[0]
    avatar_url = user_info[1]
    # create session
    session["username"] = username.lower()
    session["user_id"] = user_id
    session["avatar_url"] = avatar_url
    session["password"] = True

    # admin_status
    if user_id in admin_ids:
        session["admin"] = True
    else:
        session["admin"] = False

    # check if user is awaiting username update
    await_username_update = user_info[2]
    if await_username_update:
        flash("success_Your account is awaiting username update. Log in with discord to update.")
    # check if user is awaiting deletion
    await_deletion = user_info[3]
    if await_deletion:
        flash("success_Your account is awaiting deletion. Cancel it on your account's page.")
        session["await_deletion"] = True

    # check if user is deleted
    deleted = user_info[4]
    if deleted:
        flash("Your account has been deleted.")
        session["deleted"] = True

    flash("success_Logged in successfully as " + username)
    return jsonify({'message': 'Logged in successfully.'}), 200



@app.route('/oauth/callback')
def oauth():
    code = request.args.get("code")
    print(code)
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
    # check if user has password set, check password in db using discord id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE discord_id = %s", (str(user_id),))
    password = cursor.fetchone()
    # create session
    if password is not None and password[0] is not None and password[0].strip() != "":
        session["password"] = True
    else:
        session["password"] = False
    session["username"] = username.lower()
    session["user_id"] = user_id
    session["avatar_url"] = avatar_url

    # check if user is awaiting username update
    cursor.execute("SELECT await_username_update FROM users WHERE discord_id = %s", (str(user_id),))
    await_username_update = cursor.fetchone()
    if await_username_update:
        await_username_update = await_username_update[0]
        # change await_username_update to false in db
        cursor.execute("""
            UPDATE users
            SET await_username_update = FALSE
            WHERE discord_id = %s
        """, (str(user_id),))
        conn.commit()
    else:
        await_username_update = False

    # check if user is awaiting deletion
    cursor.execute("SELECT await_deletion FROM users WHERE discord_id = %s", (str(user_id),))
    await_deletion = cursor.fetchone()
    if await_deletion:
        await_deletion = await_deletion[0]
    else:
        await_deletion = False

    # check if user is deleted
    cursor.execute("SELECT deleted FROM users WHERE discord_id = %s", (str(user_id),))
    deleted = cursor.fetchone()
    if deleted:
        deleted = deleted[0]
    else:
        deleted = False


    # admin_status
    if user_id in admin_ids:
        session["admin"] = True
    else:
        session["admin"] = False

    # check if new user
    if is_new_user:
        flash("success_Welcome to diskord " + username + "!")
    elif await_username_update:
        flash(f"success_Username updated to {username}.")
    elif await_deletion:
        flash("success_Your account is awaiting deletion. Cancel it on your account's page.")
        session["await_deletion"] = True
    else:
        flash("success_Logged in successfully as " + username)
    return redirect(url_for("index"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/setpassword', methods=['POST'])
def setpassword():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400

    # check if user has password set, check password in db using discord id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    password = cursor.fetchone()
    print(password)
    if password is not None and password[0] is not None and password[0].strip() != "":
        return jsonify({'message': 'You already have a password set.'}), 400

    data = request.get_json()
    password = data.get('bufferPass', '')
    if not password:
        return jsonify({'message': 'Please enter a password.'}), 400
    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400

    if len(password) > 16:
        return jsonify({'message': 'Password should be less than 16 characters.'}), 400

    cursor.execute("""
        UPDATE users
        SET password = %s
        WHERE discord_id = %s
    """, (password, str(session["user_id"])))
    conn.commit()
    cursor.close()
    session["password"] = True

    return jsonify({'message': 'Password set successfully.'}), 200
    # TODO: error handling and password setting


@app.route('/updatepassword', methods=['POST'])
def updatepassword():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    # check if user has password set, check password in db using discord id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    password = cursor.fetchone()
    if password is None or password[0] is None or password[0].strip() == "":
        return jsonify({'message': 'You do not have a password set.'}), 400

    data = request.get_json()
    password = data.get('bufferPass', '')
    if not password:
        return jsonify({'message': 'Please enter a password.'}), 400
    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters.'}), 400
    # set password
    cursor.execute("""
        UPDATE users
        SET password = %s
        WHERE discord_id = %s
    """, (password, str(session["user_id"])))
    conn.commit()
    cursor.close()
    return jsonify({'message': 'Password changed successfully.'}), 200


@app.route('/update_username', methods=['POST'])
def update_username():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    # set await_username_update to true in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET await_username_update = TRUE
        WHERE discord_id = %s
    """, (str(session["user_id"]),))
    conn.commit()
    cursor.close()

    return jsonify({'message': 'Log in again with discord to update your username.'}), 200


"""

@app.route('/requestemailcode', methods=['POST'])
def requestemailcode():
    data = request.get_json()
    email = data.get('newEmail', '')
    accounts=...
    if len(accounts) >= 3:
        return jsonify({'message': 'Maximum number of accounts connected.'}), 400

    if email in accounts:
        return jsonify({'message': 'Email already linked to your account.'}), 400
    else:
        accounts.append(email)
        return jsonify({'message': 'Code has been sent to your email.'}), 200
        # TODO: generate code send it to email and save it to db

    
@app.route('/linkemail', methods=['POST'])
def linkemail():
    data = request.get_json()
    verification_code = data.get('tfaCode', '')
    return jsonify({'message': 'Email linked successfully'}), 200
    # TODO: error handling, linking, get email and code from db(email_verification)

@app.route('/unlinkemail', methods=['POST'])
def unlinkemail():
    return jsonify({'message': 'Email unlinked successfully'}), 200
    # TODO: error handling, unlinking

@app.route('/linkedaccounts', methods=['POST'])
def linkedaccounts():
    return jsonify(accounts), 200
    # TODO: fetch email accounts, format: ['maev@maev.site', 'admin@maev.site']
    
"""

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    # set await_deletion to true in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET await_deletion = TRUE
        WHERE discord_id = %s
    """, (str(session["user_id"]),))
    conn.commit()
    cursor.close()
    session["await_deletion"] = True

    return jsonify({'message': 'Your account will be deleted in 30 days, log in during that period to stop the deletion.'}), 200


@app.route('/cancel_deletion', methods=['POST'])
def cancel_deletion():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    # set await_deletion to false in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET await_deletion = FALSE
        WHERE discord_id = %s
    """, (str(session["user_id"]),))
    conn.commit()
    cursor.close()
    session["await_deletion"] = False
    return jsonify({'message': 'Account deletion canceled'}), 200




# Files
@app.route('/files')
def files():
   if 'username' not in session:
       flash("error_Please log in first.")
       return redirect(url_for('index'))

   files = json.loads(filelist())

   return jsonify(files)


"""
@app.route('/view/<path:id>')
def view(id):
   return render_template("file-view.html", file_info=file_info)
   # TODO: fetch file info for item using the id


@app.route('/update_filename', methods=['POST'])
def update_filename():   
   data = request.get_json()
   filename = data.get('fileName', '')
   return jsonify({'message': 'Filename updated successfully.'}), 200
   # TODO: Handle file rename and errors
   
"""
@app.route('/uploads')
def uploads():
    return render_template('uploads.html')

@app.route('/upload', methods=['POST'])
def upload():
    files_await_upload = []
    uploaded_files = request.files.getlist('files[]')
        # Check if files were uploaded
    if not uploaded_files:
        return jsonify({'error': 'No files were uploaded'}), 400

    for file in uploaded_files:
        temp_uuid = generate_temp_uuid()
        if file:
            filename = temp_uuid + '_' + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            files_await_upload.append(filename)
    # execute
    process_upload_files(files_await_upload, session["user_id"])
    #
    return jsonify({'message': 'Upload successful'}), 200

"""

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
    # TODO: Save the files correctly
    

@app.route('/download')
def download():
    # TODO: Process file and send download





# Notifications
@app.route('/notifications')
def get_notifications():
    # TODO: return a list of notifications for the user


@app.route('/removenotif')
def remove_notification():
    notification_id = request.args.get('id')
    # TODO: Mark notification as marked using id


@app.route('/clearnotifs')
def clearnotifs():
    # TODO: Mark all notifications as seen

# Others
@app.route('/offline')
def offline():

@app.route('/service-worker.js')
def service_worker():
    return send_file('static/service-worker.js')
    # TODO : service worker checking and sending

"""


@app.route('/invitebot')
def invitebot():
    link = ""
    return render_template('info-pages/invite-bot.html', discord_bot_invite=link)
    # TODO : Add url


@app.route('/join_community')
def join_community():
    community_link = ""
    return render_template('info-pages/join-community.html', discord_community_join=community_link)
    # TODO : Add url


@app.route('/get_help')
def get_help():
    return render_template('info-pages/account-file-recovery.html')
    # TODO : help logic


@app.route('/self_recovery')
def self_recovery():
    return render_template('info-pages/account-file-recovery.html')
    # TODO: self recovery logic


if __name__ == "__main__":
    app.run(debug=True, port=8800, host="0.0.0.0")
