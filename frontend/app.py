import datetime
import json
import os
import shutil
import subprocess
import threading
import time
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, \
    make_response
from werkzeug.utils import secure_filename, send_file
from zenora import APIClient

from config import token, client_secret, redirect_uri, oauth_url, admin_ids, get_db
from files import process_upload_files, convert_file_size, file_download_merge, check_dirs
from user_notifs import handle_notif, generate_2fa_code, send_verification_email, confirm_verification_code, \
    unlink_email, send_tfa_email

client = APIClient(token, client_secret=client_secret)
app = Flask(__name__)

uploads_dir = 'files/media'
app.config['UPLOAD_FOLDER'] = 'files/media'
secret = "maevisgod"
app.secret_key = secret
app.permanent_session_lifetime = datetime.timedelta(minutes=120)
check_dirs()

upload_dir = "files/media"
webhook_file = "flask_webhook_bridge.py"


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

            user_id = user["user_id"]
            username = user["username"]
            notif_action = "add"
            notif_type = "account"
            notif_url = "/account"
            message = f"Welcome to discord {username}"

            # add user to notif
            handle_notif(user_id, username, notif_action, message, notif_type, notif_url)

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
    db = get_db()
    cursor = db.cursor()

    try:
        # Fetch data from the 'files' table with the user's ID
        cursor.execute("SELECT * FROM files WHERE owner_id = %s and is_deleted = FALSE", (str(session["user_id"]),))
        files_data = []
        for file in cursor:
            file_data = {
                "id": file[2],
                "filename": file[1],
                "file_type": file[3],
                "size": file[5],
                "size_simple": file[6],
                "date": file[17],
                "date_updated": file[18]
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
    # account_info = {
    #     "storage_size": "73.48 GB",
    #     "files_number": 18730
    # }

    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    conn = get_db()
    cursor = conn.cursor()
    # fetch account info from files table
    cursor.execute("SELECT COUNT(id) FROM files WHERE owner_id = %s", (str(session["user_id"]),))
    files_number = cursor.fetchone()
    if files_number is None or files_number[0] is None:
        files_number = 0
    else:
        files_number = files_number[0]
    cursor.execute("SELECT SUM(file_size) FROM files WHERE owner_id = %s", (str(session["user_id"]),))
    storage_size = cursor.fetchone()
    if storage_size is None or storage_size[0] is None:
        storage_size = 0
    else:
        storage_size = storage_size[0]
    storage_size = convert_file_size(storage_size)

    # check if user has 2fa and number of emails linked
    cursor.execute("SELECT emails FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    emails = cursor.fetchone()
    if emails is None or emails[0] is None or emails[0].strip() == "":
        emails = 0
    else:
        emails = len(emails[0].split(","))
    cursor.execute("SELECT has_2fa FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    has_2fa = cursor.fetchone()
    if has_2fa is None or has_2fa[0] is None:
        tfa_enabled = False
    elif has_2fa[0] == 1 or has_2fa[0] == "1":
        tfa_enabled = True
    else:
        tfa_enabled = False

    account_info = {
        "storage_size": storage_size,
        "files_number": files_number,
        "tfa_enabled": tfa_enabled,
        "emails": emails
    }

    print(account_info)

    return render_template("account.html", account_info=account_info)


@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return jsonify({'message': 'You are already logged in.'}), 400

    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    tfa_code = data.get('tfaCode', '')
    # print(username, password, tfa_code)

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

    # check if user has 2fa enabled
    cursor.execute("SELECT has_2fa FROM users WHERE username = %s", (username.lower(),))
    has_2fa = cursor.fetchone()
    if has_2fa is None or has_2fa[0] is None:
        tfa_enabled = False
    elif has_2fa[0] == 1 or has_2fa[0] == "1":
        tfa_enabled = True
    else:
        tfa_enabled = False

    if tfa_enabled and (tfa_code is None or tfa_code.strip() == ""):
        # fetch users info
        cursor.execute("SELECT emails, discord_id from users WHERE username = %s", (username.lower(),))
        result = cursor.fetchone()
        # send email with 2fa code
        tfa_code = generate_2fa_code()
        emails = [item.strip() for item in result[0].split(",")]
        username = username.lower()
        user_id = result[1]
        # print(emails, username, user_id, tfa_code)
        for email in emails:
            check = send_tfa_email(tfa_code, email, username, user_id)
            if check:
                # check if 2fa code already exists in db
                cursor.execute("SELECT tfa_code FROM 2fa_login WHERE username = %s", (username.lower(),))
                result = cursor.fetchone()
                if result is not None and result[0] is not None and result[0].strip() != "":
                    # update 2fa code in db
                    cursor.execute("""
                        UPDATE 2fa_login
                        SET tfa_code = %s, date_created = NOW()
                        WHERE username = %s
                    """, (tfa_code, username.lower()))
                    conn.commit()
                else:
                    # add 2fa code to db
                    cursor.execute("""
                        INSERT INTO 2fa_login (username, discord_id, tfa_code, date_created) VALUES (%s, %s, %s, NOW())
                    """, (username, user_id, tfa_code))
                    conn.commit()

        return jsonify({'message': 'Please enter the 2FA code sent to your linked email.'}), 201

    elif tfa_enabled and tfa_code is not None and tfa_code.strip() != "":
        # check if 2fa code is correct
        cursor.execute("SELECT tfa_code FROM 2fa_login WHERE username = %s", (username.lower(),))
        result = cursor.fetchone()
        tfa_code_db = result[0]
        if tfa_code_db != tfa_code:
            return jsonify({'message': 'Incorrect 2FA code.'}), 400
        else:
            # delete 2fa code from db
            cursor.execute("DELETE FROM 2fa_login WHERE username = %s", (username.lower(),))
            conn.commit()

            # get user info from db
            cursor.execute(
                "SELECT discord_id, avatar, await_username_update, await_deletion, deleted FROM users WHERE username = %s",
                (username.lower(),))
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

            flash("success_Logged in as " + username)
            return jsonify({'message': 'Logged in successfully.'}), 200
    else:
        # get user info from db
        cursor.execute(
            "SELECT discord_id, avatar, await_username_update, await_deletion, deleted FROM users WHERE username = %s",
            (username.lower(),))
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

        flash("success_Logged in successfully as " + username)
        return jsonify({'message': 'Logged in successfully.'}), 200


@app.route('/oauth/callback')
def oauth():
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
    # print(password)
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


@app.route('/requestemailcode', methods=['POST'])
def requestemailcode():
    data = request.get_json()
    email = data.get('newEmail', '')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emails FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    emails = cursor.fetchone()
    if emails is None or emails[0] is None or emails[0].strip() == "":
        accounts = []
    else:
        accounts = emails[0].split(",")
    cursor.close()

    if len(accounts) >= 3:
        return jsonify({'message': 'Maximum number of accounts connected.'}), 400

    if email in accounts:
        return jsonify({'message': 'Email already linked to your account.'}), 400

    tfacode = generate_2fa_code()

    check = send_verification_email(tfacode, email, session["username"], session["user_id"])

    if check:
        return jsonify({'message': 'Code has been sent to your email.'}), 200


    else:
        return jsonify({'message': 'Failed to send code to your email.'}), 400


@app.route('/linkemail', methods=['POST'])
def linkemail():
    data = request.get_json()
    verification_code = data.get('tfaCode', '')

    check = confirm_verification_code(verification_code, session["user_id"])

    if check:
        return jsonify({'message': 'Email linked successfully'}), 200
    else:
        return jsonify({'message': 'Failed to link email'}), 400

    # TODO: error handling, linking, get email and code from db(email_verification)


@app.route('/linkedaccounts', methods=['POST'])
def linkedaccounts():
    # fetch linked accounts from db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emails FROM users WHERE discord_id = %s", (str(session["user_id"]),))
    emails = cursor.fetchone()
    if emails is None or emails[0] is None or emails[0].strip() == "":
        accounts = []
    else:
        accounts = emails[0].split(",")
    cursor.close()
    return jsonify(accounts), 200
    # TODO: fetch email accounts, format: ['maev@maev.site', 'admin@maev.site']


@app.route('/unlinkemail', methods=['POST'])
def unlinkemail():
    data = request.get_json()
    email = data.get('email', '')
    check = unlink_email(email, session["user_id"])
    if check:
        return jsonify({'message': 'Email unlinked successfully'}), 200
    else:
        return jsonify({'message': 'Failed to unlink email'}), 400
    # TODO: error handling, unlinking


@app.route('/enable2fa', methods=['POST'])
def enable2fa():
    # update has_2fa to true in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET has_2fa = TRUE
        WHERE discord_id = %s
    """, (str(session["user_id"]),))
    conn.commit()
    cursor.close()
    return jsonify({'message': '2FA enabled successfully.'}), 200


@app.route('/disable2fa', methods=['POST'])
def disable2fa():
    # update has_2fa to false in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET has_2fa = FALSE
        WHERE discord_id = %s
    """, (str(session["user_id"]),))
    conn.commit()
    cursor.close()
    return jsonify({'message': '2FA disabled successfully.'}), 200


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

    return jsonify(
        {'message': 'Your account will be deleted in 30 days, log in during that period to stop the deletion.'}), 200


@app.route('/cancel_deletion', methods=['POST'])
def cancel_deletion():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
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


# folders
@app.route('/api/folders')
def folders():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # fetch folders from db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE is_root = TRUE AND owner_id = %s", (str(session["user_id"]),))
    folders = []
    for folder in cursor:
        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "dir_id": folder[2],
            "date_created": folder[6],
            "date_updated": folder[7]
        }
        folders.append(folder_data)
    cursor.close()

    # print("folders: ", folders)
    return jsonify(folders), 200


@app.route('/api/folder/<path:id>')
def folder(id):
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # fetch dirs inside dir
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND parent_dir_id = %s", (str(session["user_id"]), id))
    folders = []
    for folder in cursor:
        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "dir_id": folder[2],
            "date_created": folder[6],
            "date_updated": folder[7]
        }
        folders.append(folder_data)
    cursor.close()

    # fetch files inside dir
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND dir_id = %s AND is_deleted = FALSE",
                   (str(session["user_id"]), id))
    files = []
    for file in cursor:
        file_data = {
            "id": file[2],
            "filename": file[1],
            "file_type": file[3],
            "size": file[5],
            "size_simple": file[6],
            "date": file[17],
            "date_updated": file[18]
        }
        files.append(file_data)
    cursor.close()

    folder_info = {
        "folders": folders,
        "files": files
    }

    print(folder_info)

    return jsonify(folder_info), 200


@app.route('/api/create_folder', methods=['POST'])
def create_folder():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # create folder in db
    data = request.get_json()
    folder_name = data.get('folderName', '')
    is_root = data.get('isRoot', False)
    parent_id = data.get('parentId', None)
    conn = get_db()
    cursor = conn.cursor()
    if is_root:
        # check if folder already exists in root
        cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_name = %s AND is_root = TRUE",
                       (str(session["user_id"]), folder_name))
        folder = cursor.fetchone()
        print(folder)

        if folder is None or folder == "":
            cursor.execute("""
                INSERT INTO file_dirs (dir_name, owner_id, dir_id, is_root, date_created, date_updated)
                VALUES (%s, %s, %s, TRUE, NOW(), NOW())
            """, (folder_name, str(session["user_id"]), (generate_temp_uuid())))
            conn.commit()

        else:
            return jsonify("Folder already exists in the current path (/)."), 400


    else:
        # check if folder already exists in parent dir
        cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_name = %s AND parent_dir_id = %s",
                       (str(session["user_id"]), folder_name, parent_id))
        folder = cursor.fetchone()
        print(folder)

        if folder is None or folder == "":
            cursor.execute("""
                INSERT INTO file_dirs (dir_name, owner_id, dir_id, parent_dir_id, is_root, date_created, date_updated)
                VALUES (%s, %s, %s, %s, FALSE, NOW(), NOW())
            """, (folder_name, str(session["user_id"]), (generate_temp_uuid()), parent_id))
            conn.commit()

        else:
            return jsonify("Folder already exists in the current path."), 400

    conn.commit()
    cursor.close()

    return jsonify("success_Folder created successfully."), 200


@app.route('/api/delete_folder', methods=['POST'])
def delete_folder():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # delete folder in db
    data = request.get_json()
    folder_id = data.get('folderId', '')
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), folder_id))
        folder = cursor.fetchone()
        print(folder)
        if folder is None or folder == "":
            return jsonify("Folder not found."), 400
        else:
            cursor.execute("DELETE FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), folder_id))
            conn.commit()
            return jsonify("success_Folder deleted successfully."), 200
    except Exception as e:
        print(e)
        return jsonify("Folder not found."), 400

@app.route('/api/rename_folder', methods=['POST'])
def rename_folder():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # rename folder in db
    data = request.get_json()
    folder_id = data.get('folderId', '')
    new_name = data.get('newName', '')

    print(folder_id, new_name)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), folder_id))
    folder = cursor.fetchone()

    if folder is None or folder == "":
        return jsonify("Folder not found."), 400

    parent_dir_id = folder[4]
    print(parent_dir_id)

    # check if folder already exists in same parent dir
    conn = get_db()
    cursor = conn.cursor()
    if parent_dir_id is None or parent_dir_id == "":
        cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_name = %s AND is_root = TRUE",
                          (str(session["user_id"]), new_name))
    else:
        cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_name = %s AND parent_dir_id = %s",
                          (str(session["user_id"]), new_name, folder[2]))
    folder = cursor.fetchone()

    if folder is None or folder == "":
        cursor.execute("UPDATE file_dirs SET dir_name = %s WHERE owner_id = %s AND dir_id = %s", (new_name, str(session["user_id"]), folder_id))
        conn.commit()
        return jsonify("success_Folder renamed successfully."), 200

    else:
        return jsonify("Folder already exists in the current path."), 400

def is_child_foldercheck(folder_id, new_parent_id):
    # get parent dir id of folder
    print(folder_id, new_parent_id)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), folder_id))
    folder = cursor.fetchone()
    print(folder)
    parent_dir_id = folder[4]
    # continously check if parent dir id is equal to new parent id until parent dir id is null
    while True:
        if parent_dir_id is None or parent_dir_id == "":
            return False
        elif parent_dir_id == new_parent_id:
            return True
        else:
            cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), parent_dir_id))
            folder = cursor.fetchone()
            parent_dir_id = folder[4]
# /api/copy_file
@app.route('/api/copy_file', methods=['POST'])
def copy_file():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # Get file info
    data = request.get_json()
    file_id = data.get('fileId', '')
    new_parent_id = data.get('parentDirId', '')
    print(file_id, new_parent_id)

    # Copy file and rename if file already exists
    conn = get_db()
    cursor = conn.cursor()

    # Check if the file to be copied exists
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_id = %s", (str(session["user_id"]), file_id))
    source_file = cursor.fetchone()

    if source_file is None:
        return jsonify("File not found."), 400

    # Check if the file already exists in the new parent directory
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_name = %s AND dir_id = %s",
                   (str(session["user_id"]), source_file[1], new_parent_id))
    existing_file = cursor.fetchone()

    if existing_file is None:
        # Copy the file
        new_file_id = generate_temp_uuid()
        dir_id = new_parent_id
        print("ID:",dir_id)
        try:
            cursor.execute("""
                INSERT INTO files (file_name, file_id, file_type, file_type_icon_url, file_size, file_size_simple, chunks_number, chunks_size, files_directory, owner_id, thread_id, thread_url, dir_id, is_deleted, permalink, direct_url, date_created, date_updated)
                SELECT file_name, %s, file_type, file_type_icon_url, file_size, file_size_simple, chunks_number, chunks_size, files_directory, owner_id, thread_id, thread_url, %s, is_deleted, permalink, direct_url, NOW(), NOW()
                FROM files
                WHERE file_id = %s
            """, (new_file_id, dir_id, file_id))




        except Exception as e:
            print(e)
            return jsonify("File not found."), 400
        conn.commit()
        return jsonify("success_File copied successfully."), 200
    else:
        # Rename the file
        cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_name LIKE %s AND dir_id = %s",
                       (str(session["user_id"]), source_file[1] + " (copy%)", new_parent_id))
        duplicate_file = cursor.fetchone()

        if duplicate_file is None:
            # Rename file to "filename (copy)"
            cursor.execute("UPDATE files SET file_name = %s WHERE owner_id = %s AND file_id = %s",
                           (source_file[1] + " (copy)", str(session["user_id"]), file_id))
        else:
            # Rename file to "filename (copy x)"
            cursor.execute("UPDATE files SET file_name = %s WHERE owner_id = %s AND file_id = %s",
                           (source_file[1] + " (copy " + str(duplicate_file[1]) + ")", str(session["user_id"]), file_id))

        conn.commit()
        return jsonify("success_File copied successfully."), 200

# /api/move_file
@app.route('/api/move_file', methods=['POST'])
def move_file():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # Get file info
    data = request.get_json()
    file_id = data.get('fileId', '')
    new_parent_id = data.get('parentDirId', '')
    print(file_id, new_parent_id)

    # Check if the file to be moved exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_id = %s", (str(session["user_id"]), file_id))
    source_file = cursor.fetchone()

    if source_file is None:
        return jsonify("File not found."), 400

    # Check if the file already exists in the new parent directory
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_name = %s AND dir_id = %s",
                   (str(session["user_id"]), source_file[1], new_parent_id))
    existing_file = cursor.fetchone()

    if existing_file is None:
        # Move the file
        cursor.execute("UPDATE files SET dir_id = %s WHERE owner_id = %s AND file_id = %s",
                       (new_parent_id, str(session["user_id"]), file_id))
        conn.commit()
        return jsonify("success_File moved successfully."), 200
    else:
        return jsonify("File already exists in the current path."), 400


# /api/move_folder
@app.route('/api/move_folder', methods=['POST'])
def move_folder():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    # get folder info
    data = request.get_json()
    folder_id = data.get('folderId', '')
    new_parent_id = data.get('newParentId', '')
    print(folder_id, new_parent_id)

    # check if folders exists and if new parent is not a child of folder
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), folder_id))
    folder = cursor.fetchone()

    is_child_folder = is_child_foldercheck(folder_id, new_parent_id)
    print(is_child_folder)

    if folder is None or folder == "":
        return jsonify("Folder not found."), 400
    else:
        # check if new parent is not a child of folder
        if folder_id == new_parent_id:
            return jsonify("Cannot move folder to itself."), 400

        if is_child_folder:
            return jsonify("Cannot move folder to its child."), 400
        else:
            # update parent dir id in db and set is_root to false
            cursor.execute("UPDATE file_dirs SET parent_dir_id = %s, is_root = %s WHERE owner_id = %s AND dir_id = %s", (new_parent_id, 0, str(session["user_id"]), folder_id))
            conn.commit()
            return jsonify("success_Folder moved successfully."), 200


def getdirchildren(dir_id):
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND parent_dir_id = %s", (str(session["user_id"]), dir_id))
    folders = []
    for folder in cursor:
        if dirhaschildren(folder[2]):
            children = getdirchildren(folder[2])
        else:
            children = []
        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "dir_id": folder[2],
            "children": children
        }
        folders.append(folder_data)

    return folders

def dirhaschildren(dir_id):
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND parent_dir_id = %s", (str(session["user_id"]), dir_id))
    folder = cursor.fetchone()
    if folder is None or folder == "":
        return False
    else:
        return True



@app.route('/api/dir_structure')
def dir_structure():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # fetch root folders from db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE is_root = TRUE AND owner_id = %s", (str(session["user_id"]),))
    folders = []
    for folder in cursor:
        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "dir_id": folder[2]
        }
        folders.append(folder_data)
    cursor.close()

    # continously fetch children of folders until no more children
    while True:
        for folder in folders:
            if dirhaschildren(folder["dir_id"]):
                folder["children"] = getdirchildren(folder["dir_id"])
            else:
                folder["children"] = []
        break

    print("folders: ", folders)
    return jsonify(folders), 200

@app.route('/api/recents')
def recents():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # fetch last 10 files from db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND is_deleted = FALSE ORDER BY date_updated DESC LIMIT 5",
                   (str(session["user_id"]),))
    files = []
    for file in cursor:
        file_data = {
            "id": file[2],
            "filename": file[1],
            "file_type": file[3],
            "size": file[5],
            "size_simple": file[6],
            "date": file[17],
            "date_updated": file[18]
        }
        files.append(file_data)
    cursor.close()

    # print("files: ", files)
    return jsonify(files), 200


# Files
@app.route('/files')
def files():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    files = json.loads(filelist())

    # print("files: ", files)

    return jsonify(files)


@app.route('/api/details/folder/<path:id>')
def folder_details(id):
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND dir_id = %s", (str(session["user_id"]), id))
    folder_info = cursor.fetchone()

    #close


    if folder_info is None:
        return jsonify("error_Folder not found."), 400

    # fetch files in folder
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM files WHERE owner_id = %s AND dir_id = %s AND is_deleted = FALSE",
                   (str(session["user_id"]), id))
    except Exception as e:
        print(e)

    files = []
    size = 0
    filenumber = 0
    for file in cursor:
        file_data = {
            "id": file[2],
            "filename": file[1],
            "file_type": file[3],
            "size": file[5],
            "size_simple": file[6],
            "date": file[17],
            "date_updated": file[18]
        }
        files.append(file_data)
        size += file[5]
        filenumber += 1

    # fetch folders in folder
    cursor = db.cursor()
    cursor.execute("SELECT * FROM file_dirs WHERE owner_id = %s AND parent_dir_id = %s", (str(session["user_id"]), id))
    folders = []
    dirnumber = 0
    for folder in cursor:
        folder_data = {
            "id": folder[0],
            "name": folder[1],
            "dir_id": folder[2],
            "date_created": folder[6],
            "date_updated": folder[7]
        }
        folders.append(folder_data)
        dirnumber += 1

    folder_info = {
        "id": folder_info[3],
        "name": folder_info[2],
        "description": folder_info[4],
        "dir_id": folder_info[1],
        "file_number": filenumber,
        "dir_number": dirnumber,
        "folders": folders,
        "size": size,
        "date": folder_info[6],
        "date_updated": folder_info[7]
    }

    # print(folder_info)

    return jsonify(folder_info), 200


@app.route('/api/details/file/<path:id>')
def file_details(id):
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM files WHERE owner_id = %s AND file_id = %s", (str(session["user_id"]), id))
    file_info = cursor.fetchone()
    if file_info is None:
        return jsonify("error_File not found."), 400
    file_info = {
        "id": file_info[2],
        "filename": file_info[1],
        "file_type": file_info[3],
        "description": file_info[9],
        "size": file_info[5],
        "size_simple": file_info[6],
        "date": file_info[17],
        "date_updated": file_info[18]
    }

    # print(file_info)

    return jsonify(file_info), 200


@app.route('/view/<path:id>', methods=['GET'])
def view(id):
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM files WHERE file_id = %s", (id,))
    file_info = cursor.fetchone()
    if file_info is None:
        flash("error_File not found.")
        return redirect(url_for('index'))
    file_index_id = file_info[0]

    # fetch subfiles and their urls
    cursor = db.cursor()
    cursor.execute("SELECT * FROM subfiles WHERE main_file_id = %s", (file_index_id,))
    subfiles = []
    for subfile in cursor:
        subfile_data = {
            "id": subfile[0],
            "chunk_file_id": subfile[2],
            "file_name": subfile[3],
            "url": subfile[4],
            "date_created": subfile[5]
        }
        subfiles.append(subfile_data)

    file_info = {
        "id": file_info[2],
        "filename": file_info[1],
        "file_type": file_info[4],
        "size": file_info[5],
        "size_simple": file_info[6],
        "date": file_info[15],
        "date_updated": file_info[16],
        "subfiles": subfiles
    }
    return render_template("file-view.html", file_info=file_info)


@app.route('/update_filename', methods=['POST'])
def update_filename():
    data = request.get_json()
    filename = data.get('fileName', '')
    file_id = data.get('fileID', '')
    if not filename:
        return jsonify({'message': 'Please enter a filename.'}), 400
    if not file_id:
        return jsonify({'message': 'No file ID provided.'}), 400
    # update filename in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE files
        SET file_name = %s
        WHERE file_id = %s
    """, (filename, file_id))
    conn.commit()
    cursor.close()
    return jsonify({'message': 'Filename updated successfully.'}), 200
    # TODO: Handle file rename and errors


@app.route("/stats", methods=['POST'])
def stats():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))

    # get stats from db
    id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    # fetch file_size and count files from files table where owner_id = id
    cursor.execute("SELECT SUM(file_size), COUNT(id) FROM files WHERE owner_id = %s AND is_deleted = FALSE", (id,))
    stats = cursor.fetchone()

    if stats is None:
        file_number = 0
        file_size = 0
    else:
        if stats[0] is None or stats[0] == "":
            file_size = 0
        else:
            file_size = convert_file_size(stats[0])
        if stats[1] is None or stats[1] == "":
            file_number = 0
        else:
            file_number = stats[1]

    user_stats = {
        "file_number": file_number,
        "file_size": file_size
    }

    return jsonify(user_stats), 200


@app.route('/delete_file', methods=['POST'])
def delete_file():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    data = request.get_json()
    fileid = data.get('deleteFileID', '')
    if not fileid:
        return jsonify({'message': 'No file ID provided.'}), 400
    # update filename in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE files
        SET is_deleted = TRUE
        WHERE file_id = %s
    """, (fileid,))
    conn.commit()
    cursor.close()
    return jsonify({'message': 'File deleted successfully.'}), 200


@app.route('/uploads_old')
def uploads_old():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    return render_template('uploads.html')


@app.route('/uploads')
def uploads():
    if 'username' not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    return render_template('uploads_1.html')


@app.route('/upload_alternate', methods=['POST'])
def upload_alternate():
    if "username" not in session:
        return 'Please log in to start uploading.', 400
    file = request.files['file']
    save_path = os.path.join(upload_dir, secure_filename(file.filename))
    current_chunk = int(request.form['dzchunkindex'])
    if os.path.exists(save_path) and current_chunk == 0:
        return make_response(('File already exists', 400))
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except Exception as e:
        print('Could not write to file')
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))
    total_chunks = int(request.form['dztotalchunkcount'])
    if current_chunk + 1 == total_chunks:
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            print(f"File {file.filename} was completed, "
                  f"but has a size mismatch."
                  f"Was {os.path.getsize(save_path)} but we"
                  f" expected {request.form['dztotalfilesize']} ")
            return make_response(('Size mismatch', 500))
        else:
            # print(f'File {file.filename} has been uploaded successfully')
            temp_uuid = generate_temp_uuid()
            filename = temp_uuid + '_' + file.filename
            # rename file
            os.rename(save_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Use the function reference without invoking it
            thread = threading.Thread(target=process_upload_files,
                                      args=([filename], session["user_id"], session["username"]))
            thread.start()

            return make_response(('Uploaded all chunks', 200))
    else:
        # print(f'Chunk {current_chunk + 1} of {total_chunks} 'f'for file {file.filename} complete')
        pass
    return make_response(("Chunk upload successful", 200))


@app.route('/upload', methods=['POST'])
def upload():
    if "username" not in session:
        return jsonify({'message': 'Please log in to start uploading.'}), 400

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

    # Use the function reference without invoking it
    thread = threading.Thread(target=process_upload_files,
                              args=(files_await_upload, session["user_id"], session["username"]))
    thread.start()
    # process_upload_files(files_await_upload, session["user_id"], session["username"])

    return jsonify({'message': 'Upload successful'}), 200


@app.route('/download/<path:file_id>', methods=['GET', 'POST'])
def download(file_id):
    if "username" not in session:
        flash("error_Please log in first.")
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM files WHERE file_id = %s", (file_id,))
    file_info = cursor.fetchone()
    if file_info is None:
        flash("error_File not found.")
        return redirect(url_for('index'))
    file_index_id = file_info[0]

    # fetch subfiles and their urls
    cursor = db.cursor()
    cursor.execute("SELECT * FROM subfiles WHERE main_file_id = %s", (file_index_id,))
    subfiles = []
    for subfile in cursor:
        subfile_data = {
            "id": subfile[0],
            "chunk_file_id": subfile[2],
            "file_name": subfile[3],
            "url": subfile[4],
            "date_created": subfile[5]
        }
        subfiles.append(subfile_data)

    file_info = {
        "id": file_info[2],
        "filename": file_info[1],
        "file_type": file_info[4],
        "size": file_info[5],
        "size_simple": file_info[6],
        "date": file_info[15],
        "date_updated": file_info[16],
        "subfiles": json.dumps(subfiles),
        "chunks_number": file_info[7]
    }

    threading.Thread(target=file_download_merge, args=(file_info,)).start()

    # file_download_merge(file_info)

    if request.method == 'GET':
        return render_template('download.html', file_info=file_info)
    elif request.method == 'POST':
        # download the files
        print("Downloading files...")


# download and progress tracking
@app.route('/download_progress', methods=['POST'])
def download_progress():
    # check if stat
    data = request.get_json()
    file_id = data.get('fileID', '')
    if not file_id:
        return jsonify({'message': 'No file ID provided.'}), 400
    status_file = f"files/merge_output/{file_id}/status.txt"
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = f.read()
        return jsonify({'message': status}), 200
    else:
        time.sleep(3)
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status = f.read()
            return jsonify({'message': status}), 200
        else:
            return jsonify({'message': 'File not found.'}), 400


@app.route('/download_file/<path:file_id>', methods=['GET'])
def download_file(file_id):
    if "username" not in session:
        return jsonify({'message': 'Please log in to start downloading.'}), 400
    if not file_id:
        return 'No file ID provided.', 400

    # Fetch filename from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT file_name FROM files WHERE file_id = %s", (file_id,))
    filename = cursor.fetchone()

    if filename is None or filename[0] is None or filename[0].strip() == "":
        return 'File not found', 404

    filename = filename[0]

    # Construct the file path
    file_path = os.path.join("files/merge_output", str(file_id), filename)

    if not os.path.exists(file_path):
        return 'File not found', 404

    try:
        # Send the file as an attachment
        # return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)
        return send_file(file_path, environ=request.environ, as_attachment=True)
    except Exception as e:

        # Handle any other potential errors, such as I/O errors
        app.logger.error(f"Error while serving the file: {str(e)}")
        return jsonify({'message': 'An error occurred while serving the file.'}), 500


@app.route('/download_file_complete', methods=['POST'])
def download_file_complete():
    data = request.get_json()
    file_id = data.get('fileID', '')
    if "username" not in session:
        return jsonify({'message': 'Please log in to start downloading.'}), 400
    if not file_id:
        return jsonify({'message': 'No file ID provided.'}), 400
    # check if file exists in merge_output
    # fetch filename from db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT file_name FROM files WHERE file_id = %s", (file_id,))
    filename = cursor.fetchone()
    if filename is None or filename[0] is None or filename[0].strip() == "":
        return jsonify({'message': 'File not found.'}), 400
    filename = filename[0]
    # check if file exists
    if not os.path.exists(f"files/merge_output/{file_id}/{filename}"):
        print("File not found")
        return jsonify({'message': 'File not found.'}), 400
    # delete file and dir
    shutil.rmtree(f"files/merge_output/{file_id}")
    return jsonify({'message': 'File deleted successfully.'}), 200


# Notifications
@app.route('/notifications')
def get_notifications():
    if 'username' not in session:
        notifications = [{
            "id": 0,
            "message": "Please log in to view your notifications.",
            "is_seen": False,
            "type": "system",
            "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        return jsonify(notifications)

    # fetch notifications from db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notifications WHERE user_discord_id = %s and is_seen = FALSE",
                   (str(session["user_id"]),))
    notifications = []

    for notification in cursor:
        if notification[4] is None:
            notification_data = {
                "id": notification[0],
                "message": notification[3],
                "is_seen": notification[5],
                "type": notification[6],
                "date_created": notification[7]

            }
        else:
            notification_data = {
                "id": notification[0],
                "message": notification[3],
                "url": notification[4],
                "is_seen": notification[5],
                "type": notification[6],
                "date_created": notification[7]
            }
        notifications.append(notification_data)
    cursor.close()
    notifications = notifications[::-1]

    return jsonify(notifications)


@app.route('/removenotif')
def remove_notification():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    notification_id = request.args.get('id')
    if not notification_id:
        return jsonify({'message': 'No notification ID provided.'}), 400

    check = handle_notif(session["user_id"], session["username"], "remove", "", "", notif_id=notification_id)
    if check:
        return jsonify({'message': 'Notification removed successfully.'}), 200
    else:
        return jsonify({'message': 'Failed to remove notification.'}), 400


@app.route('/clearnotifs')
def clearnotifs():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 400
    check = handle_notif(session["user_id"], session["username"], "remove_all", "", "")
    if check:
        return jsonify({'message': 'Notifications cleared successfully.'}), 200
    else:
        return jsonify({'message': 'Failed to clear notifications.'}), 400


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


# TODO: offline route/ service worker

if __name__ == "__main__":
    app.run(debug=True, port=4321, host="0.0.0.0")
