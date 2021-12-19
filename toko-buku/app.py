import mysql.connector
from flask import Flask, render_template, request, url_for, flash, redirect
from requests.api import get
from werkzeug.exceptions import abort

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

def get_buku(buku_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buku WHERE id = %s', (buku_id,))
    entry = cursor.fetchone()
    datas = {
        'id': entry[0],
            'cover': entry[1],
            'title': entry[2],
            'description': entry[3],
            'author': entry[4],
            'publisher': entry[5],
            'date': entry[6],
    }
    conn.close()
    if datas is None:
        abort(404)
    return datas

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buku')
    result = cursor.fetchall()
    datas = []
    for entry in result:
        record = {
            'id': entry[0],
            'cover': entry[1],
            'title': entry[2],
            'description': entry[3],
            'author': entry[4],
            'publisher': entry[5],
        }
        datas.append(record)
    conn.close()
    return render_template('home.html',datas=datas)

@app.route('/detail/<int:buku_id>')
def detail(buku_id):
    datas = get_buku(buku_id)
    return render_template('detail.html',datas=datas)
