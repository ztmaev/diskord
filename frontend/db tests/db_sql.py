import mysql.connector

database_name = "Alpha1"


db_config = {
    "host": "arc.maev.site",  # Update with your MySQL server host
    "user": "maev",  # Update with your MySQL username
    "password": "Alph4",  # Update with your MySQL password
    "port": "3306"
}

# Connect to MySQL server
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Check database list
cursor.execute("SHOW DATABASES")
database_exists = False
for database in cursor:
    if database[0] == database_name:
        database_exists = True
        print(f"Database '{database_name}' exists")
        break

if not database_exists:
    # Create the 'test' database
    cursor.execute(f"CREATE DATABASE {database_name}")
    print(f"Created {database_name}")

# Switch to the 'test' database
cursor.execute(f"USE {database_name}")

# Check tables.
cursor.execute("SHOW TABLES")
table_users_exists = False
table_files_exists = False
table_notifications_exists = False
table_discord_info_exists = False
table_2fa_exists = False
table_subfiles_exists = False

for table in cursor:
    if table[0] == "users":
        table_users_exists = True
        print(f"Table 'users' exists")
    if table[0] == "files":
        table_files_exists = True
        print(f"Table 'files' exists")
    if table[0] == "subfiles":
        table_subfiles_exists = True
        print(f"Table 'subfiles' exists")
    if table[0] == "notifications":
        table_notifications_exists = True
        print(f"Table 'notifications' exists")
    if table[0] == "discord_info":
        table_discord_info_exists = True
        print(f"Table 'discord_info' exists")
    if table[0] == "2fa":
        table_2fa_exists = True
        print(f"Table '2fa' exists")

# Users
if not table_users_exists:
    cursor.execute("""
        CREATE TABLE users (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            password VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            discord_id BIGINT NOT NULL,
            avatar VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            emails VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            await_username_update BOOLEAN NOT NULL DEFAULT FALSE,
            await_deletion BOOLEAN NOT NULL DEFAULT FALSE,
            deleted BOOLEAN NOT NULL DEFAULT FALSE,
            date_created VARCHAR(255) NOT NULL,
            date_updated VARCHAR(255) NOT NULL
        )
    """)
    print("Created 'users' table")

# Discord Info
if not table_discord_info_exists:
    cursor.execute("""
        CREATE TABLE discord_info (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            discriminator VARCHAR(255) NOT NULL,
            discord_id BIGINT NOT NULL,
            avatar_url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            is_bot BOOLEAN DEFAULT FALSE,
            locale VARCHAR(255),
            email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            bio VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            has_mfa BOOLEAN DEFAULT FALSE,
            verified BOOLEAN DEFAULT FALSE,
            date_created VARCHAR(255) NOT NULL,
            date_updated VARCHAR(255) NOT NULL
        )
    """)
    print("Created 'discord_info' table")

# Notifications
if not table_notifications_exists:
    cursor.execute("""
        CREATE TABLE notifications (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            user_discord_id BIGINT NOT NULL,
            message VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            message_url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            is_seen BOOLEAN NOT NULL DEFAULT FALSE,
            date_created VARCHAR(255) NOT NULL,
            date_seen VARCHAR(255) NOT NULL
        )
    """)
    print("Created 'notifications' table")

# Files
if not table_files_exists:
    cursor.execute("""
        CREATE TABLE files (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            file_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            file_type VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            file_type_icon_url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            file_size BIGINT NOT NULL,
            file_size_simple VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            chunks_number BIGINT NOT NULL,
            chunks_size BIGINT NOT NULL,
            files_directory VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            owner_id BIGINT,
            thread_id BIGINT,
            thread_url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            permalink VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            date_created VARCHAR(255) NOT NULL,
            date_updated VARCHAR(255) NOT NULL
        )
    """)
    print("Created 'files' table")

# Subfiles
if not table_subfiles_exists:
    cursor.execute("""
        CREATE TABLE subfiles (
            id INT PRIMARY KEY AUTO_INCREMENT PRIMARY KEY,
            main_file_id INT NOT NULL,
            chunk_file_id INT NOT NULL,
            file_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            file_url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            date_created VARCHAR(255) NOT NULL
        )
    """)
    print("Created 'subfiles' table")

# 2FA
if not table_2fa_exists:
    cursor.execute("""
        CREATE TABLE `2fa` (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            discord_id BIGINT NOT NULL,
            `2fa_code` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
            email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
        )
    """)
    print("Created '2fa' table")


# Close the cursor and connection
cursor.close()
conn.close()
