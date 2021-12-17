import mysql.connector
from flask import Flask, render_template, request, url_for, flash, redirect

def get_db_connection():
    #conn = sqlite3.connect('database.db')
    #conn.row_factory = sqlite3.Row
    #return conn
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="toko_buku"
    )
    

    return conn

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    conn = get_db_connection()
    mycursor = conn.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM buku")
    Buku = mycursor.fetchall()
    return render_template('index.html', Buku=Buku)

@app.route('/home')
def home():
    return render_template('home.html')
