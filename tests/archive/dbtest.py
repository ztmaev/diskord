# test connection to database
import mysql.connector

username = "maev"
password = "Alph4"
host = "arc.maev.site"
port = "3306"

db = mysql.connector.connect(
    host=host,
    user=username,
    passwd=password,
    port=port
)

list_of_databases = db.cursor()
list_of_databases.execute("SHOW DATABASES")

db_list = []
for x in list_of_databases:
    db_list.append(x[0])

print(db_list)

