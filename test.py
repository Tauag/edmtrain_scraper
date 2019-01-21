import mysql.connector

db = mysql.connector.connect(host="127.0.0.1",
                     user="root",
                     password="password",
                     database="database")

print(db)

db.close()