import requests, mysql.connector
from flask import Flask, render_template, request, url_for, flash, redirect
from requests.api import get
from werkzeug.exceptions import abort
from bs4 import BeautifulSoup

def get_db_connection():
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

def scrape_gplay_books(url):
    res = requests.get(url)
    doc = BeautifulSoup(res.text, 'html.parser')

    cvr_tag = doc.find('img', 'T75of h1kAub')
    cvr = cvr_tag['srcset'].replace(' 2x', '')

    title_tag = doc.select('h1[itemprop="name"] span')
    title = title_tag[0].getText()

    desc_tag = doc.select('#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > c-wiz:nth-child(1) > div.JHTxhe.IQ1z0d > div.W4P4ne > div.PHBdkd > div.DWPxHb')
    desc = desc_tag[0].getText()

    author_tag = doc.select('span[itemprop="author"] a[class="hrTbp R8zArc"]')
    author = author_tag[0].getText()
    if len(author_tag) > 1:
        for person in author_tag[1:]:
            author+=', ' + person.getText()

    info_titles = ['Publisher', 'Published on', 'Genres', 'Language', 'Pages', 'Best for']
    info = {}

    genres = ''

    for info_title in info_titles:
        if info_title == 'Genres':
            info_title_tag = doc.find('div', text='Genres')
            siblings = info_title_tag.find_next_siblings()
            genres = siblings[0].getText()
            if len(siblings) > 1:
                for sib in siblings[1:]:
                    genres+= ' / ' + sib.getText()

        else:
            info_title_tag = doc.find(text=info_title)
            parent = info_title_tag.find_parent()
            sibling = [parent.find_next_sibling()]
            info[info_title]=sibling[0].getText()

    pub = info['Publisher']

    pub_date = info['Published on']

    lang = info['Language']

    pages = info['Pages']

    cmptblty = info['Best for']

    price_tag = doc.select('button[class="LkLjZd ScJHi HPiPcc IfEcue"] meta[itemprop="price"]')
    price = price_tag[0]['content'].replace('$', '')
    price_idr = float(price) * 14372.15
    price_final = 'IDR ' + "{:,}".format(int(price_idr)) + '.00'

    rating_tag = doc.select('div[class="BHMmbe"]')
    rating = rating_tag[0].getText()

    rev_num_tag = doc.select('span[class="EymY4b"] span')
    rev_num = rev_num_tag[1].getText()

    book_info = {
        'Cover':cvr,
        'Title':title,
        'Description':desc,
        'Author':author,
        'Publisher':pub,
        'Publication Date':pub_date,
        'Genres':genres,
        'Language':lang,
        'Pages':pages,
        'Compatibility':cmptblty,
        'Price':price_final,
        'Rating':rating,
        'Number of Reviewer':rev_num}

    return book_info

app = Flask(__name__)

@app.route('/')
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
            'price': entry[11],
            'rating': entry[12]
        }
        datas.append(record)
    conn.close()
    return render_template('home.html',datas=datas)

@app.route('/detail/<int:buku_id>')
def detail(buku_id):
    datas = get_buku(buku_id)
    return render_template('detail.html',datas=datas)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/scrape', methods=['POST'])
def scrape():
    url_list = request.form['link_textarea'].split(',')
    report_list = []
    for url in url_list:
        report = 'Scraping ' + url
        try:
            book = scrape_gplay_books(url)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO buku (cover,title,description,author,publisher,publication_date,genres,language,pages,compatibility,price,rating,total_rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(book['Cover'],book['Title'],book['Description'],book['Author'],book['Publisher'],book['Publication Date'],book['Genres'],book['Language'],book['Pages'],book['Compatibility'],book['Price'],book['Rating'],book['Number of Reviewer']))
            conn.commit()
            conn.close()
            report+= ' success\n'
        except Exception as e:
            report+= ' failed ' + repr(e) + '\n'
        
        report_list.append(report)
    return render_template('scrape_report.html', report = report_list)