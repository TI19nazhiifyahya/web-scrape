import mysql.connector

connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
)

cur = connection.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS toko_buku")
cur.execute("USE toko_buku")
cur.execute("CREATE TABLE IF NOT EXISTS buku ( id INT PRIMARY KEY AUTO_INCREMENT, cover TEXT NULL, title TEXT NOT NULL, description TEXT NOT NULL, author TEXT NOT NULL, publisher TEXT NOT NULL,publication_date DATE NOT NULL, genres TEXT NOT NULL, language TEXT NOT NULL, pages TEXT NOT NULL, compatibility TEXT NOT NULL, price INT NOT NULL, rating TEXT NOT NULL, total_rating TEXT NOT NULL, status VARCHAR(10) NOT NULL DEFAULT 'visible' )")
cur.execute("CREATE TABLE IF NOT EXISTS user ( id INT PRIMARY KEY AUTO_INCREMENT, nama TEXT NULL, username TEXT NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_timestamp TIMESTAMP)")


connection.commit()
connection.close()