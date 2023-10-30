import random

import requests

from config import get_db


def handle_notif(user_id, username, notif_action, notif_message, type, url=None, notif_id=None):
    if notif_action == "add":
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO notifications (user_discord_id, username, message, message_url, type, date_created) VALUES (%s, %s, %s, %s, %s, NOW())",
            (user_id, username, notif_message, url, type)
        )
        db.commit()
        db.close()
    elif notif_action == "remove":
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
            UPDATE notifications SET
                    is_seen = TRUE,
                    date_seen = NOW()
                WHERE
                    id = %s
            """, (notif_id,)
                           )
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(e)
            return False
    elif notif_action == "remove_all":
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
            UPDATE notifications SET
                    is_seen = TRUE,
                    date_seen = NOW()
                WHERE
                    user_discord_id = %s
            """, (user_id,)
                           )

            db.commit()
            db.close()
            return True
        except Exception as e:
            return False
    else:
        return False


def generate_2fa_code():
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    code = ""
    for i in range(5):
        code += random.choice(characters)
    return code


def email_template(tfa_code):
    return f"""
                <!DOCTYPE html>
        <html>
        <head>
            <title>2fa Code</title>
        </head>
        <body>
            <div style="text-align: center; font-family: monospace, sans-serif; background-color: #202225; color: #ccc; padding: 20px;border: 1px solid #737373; border-radius: 5px">
                <h1 style="color: #ccc;">Two Factor Authentication</h1>
                <p style="color: #ccc;">Use the following code to link this email to your account:</p>
                <div style="background-color: #2f3136; padding: 20px; border: 1px solid #737373; border-radius: 5px;">
                    <h2 style="color: #;">Your 2FA Code:</h2>
                    <h3 style="color: #00b972; font-size: 32px;">{tfa_code}</h3>
                </div>
                <p style="color: #ccc;">This code will expire 1 hour, please use it promptly.</p>
                <p style="color: #ccc; ">If you didn't request this code, please disregard this email.</p>
                <p style="color: #ccc; ">&copy; 2023 Diskord</p>
            </div>
        </body>
        </html>
    """

def login_email_template(tfa_code):
    return f"""
                <!DOCTYPE html>
        <html>
        <head>
            <title>2fa Code</title>
        </head>
        <body>
            <div style="text-align: center; font-family: monospace, sans-serif; background-color: #202225; color: #ccc; padding: 20px;border: 1px solid #737373; border-radius: 5px">
                <h1 style="color: #ccc;">Two Factor Authentication</h1>
                <p style="color: #ccc;">Use the following code to verify the login:</p>
                <div style="background-color: #2f3136; padding: 20px; border: 1px solid #737373; border-radius: 5px;">
                    <h2 style="color: #;">Your 2FA Code:</h2>
                    <h3 style="color: #00b972; font-size: 32px;">{tfa_code}</h3>
                </div>
                <p style="color: #ccc;">This code will expire 1 hour, please use it promptly.</p>
                <p style="color: #ccc; ">If you didn't request this code, please disregard this email.</p>
                <p style="color: #ccc; ">&copy; 2023 Diskord</p>
            </div>
        </body>
        </html>
    """


def send_verification_email(tfa_code, email, username, user_id):
    url = "https://freemail.maev.site"
    payload = {
        "api_key": "guest",
        "sender_name": "Diskord",
        "subject": "Verification Code",
        "message": email_template(tfa_code),
        "message_type": "html",
        "footer": "",
        "receiver_email": email
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            check = save_2fa_info(username, user_id, tfa_code, email)
            if check:
                return True
        else:
            return False
    except Exception as e:
        return False

def send_tfa_email(tfa_code, email, username, user_id):
        url = "https://freemail.maev.site"
        payload = {
            "api_key": "guest",
            "sender_name": "Diskord",
            "subject": "Login Verification Code",
            "message": login_email_template(tfa_code),
            "message_type": "html",
            "footer": "",
            "receiver_email": email
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                check = save_2fa_info(username, user_id, tfa_code, email)
                if check:
                    return True
            else:
                return False
        except Exception as e:
            return False

def save_2fa_info(username, user_id, tfa_code, email):
    try:
        # clear old codes if any
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
            DELETE FROM 2fa WHERE discord_id = %s
            """, (user_id,))
            db.commit()
        except Exception as e:
            pass

        cursor.execute("""
        INSERT INTO 2fa (username, discord_id, tfa_code, email, date_created) VALUES (%s, %s, %s, %s, NOW())
        """, (username, user_id, tfa_code, email))
        db.commit()
        db.close()
        return True
    except Exception as e:
        return False


def confirm_verification_code(tfa_code, user_id):
    print(tfa_code)
    try:
        # check if user has a code and if it matches
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
        SELECT * FROM 2fa WHERE discord_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            if result[3] == tfa_code:
                email_to_add = result[4]
                # add the email to the user's emails
                # fetch user's emails
                cursor.execute("""
                SELECT emails FROM users WHERE discord_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                emails = result[0]
                if emails == None:
                    emails = email_to_add
                else:
                    emails = f"{emails},{email_to_add}"
                # update user's emails
                cursor.execute("""
                UPDATE users SET emails = %s WHERE discord_id = %s
                """, (emails, user_id))
                db.commit()

                # delete code
                cursor.execute("""
                DELETE FROM 2fa WHERE discord_id = %s
                """, (user_id,))
                db.commit()
                db.close()

                # fetch username
                db = get_db()
                cursor = db.cursor()
                cursor.execute("""
                SELECT username FROM users WHERE discord_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                username = result[0]

                # add notif
                handle_notif(user_id, username, "add", f"Successfully linked {email_to_add}", "account")

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False


def unlink_email(email, user_id):
    try:
        # fetch user's emails
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
        SELECT emails FROM users WHERE discord_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        emails = result[0]
        emails = emails.split(",")
        emails.remove(email)
        emails = ",".join(emails)
        # update user's emails
        cursor.execute("""
        UPDATE users SET emails = %s WHERE discord_id = %s
        """, (emails, user_id))
        db.commit()
        db.close()

        # add notif
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
        SELECT username FROM users WHERE discord_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        username = result[0]
        handle_notif(user_id, username, "add", f"Successfully unlinked {email}", "account")


        return True
    except Exception as e:
        print(e)
        return False
