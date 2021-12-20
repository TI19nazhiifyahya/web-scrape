import mysql.connector

connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
)

cur = connection.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS toko_buku")
cur.execute("USE toko_buku")
cur.execute("CREATE TABLE IF NOT EXISTS buku ( id INT PRIMARY KEY AUTO_INCREMENT, cover TEXT NULL, title TEXT NOT NULL, description TEXT NOT NULL, author TEXT NOT NULL, publisher TEXT NOT NULL,publication_date TEXT NOT NULL, genres TEXT NOT NULL, language TEXT NOT NULL, pages TEXT NOT NULL, compatibility TEXT NOT NULL, price TEXT NOT NULL, rating TEXT NOT NULL, total_rating TEXT NOT NULL )")


connection.commit()
connection.close()