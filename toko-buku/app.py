import requests, mysql.connector, csv, os, numpy
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
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

def chartBahasa():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT language, count(*) as number FROM buku GROUP BY language;')
    result = cursor.fetchall()
    dataBahasa = []
    for entry in result:
        record = [entry[0],entry[1]]
        dataBahasa.append(record)
    conn.close()
    return dataBahasa

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
    pub_date_list = pub_date.split(' ')
    pub_date_month = pub_date_list[0]
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i in range(len(month)):
        if month[i] == pub_date_month:
            pub_date_month = i+1
            break
    pub_date_day = pub_date_list[1].replace(',', '')
    pub_date_year = pub_date_list[2]
    pub_date_final = '%s-%s-%s' % (pub_date_year, pub_date_month, pub_date_day)
    

    lang = info['Language']

    pages = info['Pages']

    cmptblty = info['Best for']

    price_tag = doc.select('button[class="LkLjZd ScJHi HPiPcc IfEcue"] meta[itemprop="price"]')
    price = price_tag[0]['content'].replace('$', '')
    price_idr = float(price) * 14372.15
    price_final = int(price_idr)

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
        'Publication Date':pub_date_final,
        'Genres':genres,
        'Language':lang,
        'Pages':pages,
        'Compatibility':cmptblty,
        'Price':price_final,
        'Rating':rating,
        'Number of Reviewer':rev_num}

    return book_info

def genre_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT genres FROM buku"
    cursor.execute(query)
    result = cursor.fetchall()
    genre_list = []
    for entry in result:
        genres = entry[0].split(' / ')
        for genre in genres:
            if genre not in genre_list:
                genre_list.append(genre)
    return genre_list 

def lang_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT language FROM buku"
    cursor.execute(query)
    result = cursor.fetchall()
    lang_list = []
    for entry in result:
        langs = entry
        for lang in langs:
            if lang not in lang_list:
                lang_list.append(lang)
    return lang_list

def comp_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT compatibility FROM buku"
    cursor.execute(query)
    result = cursor.fetchall()
    comp_list = []
    for entry in result:
        comps = entry[0].split(', ')
        for comp in comps:
            if comp not in comp_list:
                comp_list.append(comp)
    return comp_list

app = Flask(__name__)
app.secret_key = 'thisIsSecret'

@app.route('/')
def one():
    return redirect(url_for('home'))

@app.route('/home/')
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
            'price': 'IDR ' + '{:,}'.format(entry[11]) + '.00',
            'rating': entry[12]
        }
        datas.append(record)
    conn.close()
    return render_template('home.html', datas=datas, genre_list = genre_list(), lang_list = lang_list(), comp_list = comp_list())

@app.route('/home/search/', methods=['POST'])
def search():
    if request.method == 'POST':
        srch_phrase = request.form['search-phrs']
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM buku WHERE title LIKE '%{srch_phrase}%' OR author LIKE '%{srch_phrase}%'"
        cursor.execute(query)
        result = cursor.fetchall()
        books = []
        for entry in result:
            record = {
                'id': entry[0],
                'cover': entry[1],
                'title': entry[2],
                'description': entry[3],
                'author': entry[4],
                'publisher': entry[5],
                'price': 'IDR ' + '{:,}'.format(entry[11]) + '.00',
                'rating': entry[12]
            }
            books.append(record)
        conn.close()
        return render_template('home.html', datas = books, genre_list = genre_list(), lang_list = lang_list(), comp_list = comp_list())

@app.route('/home/filter/', methods=['POST'])
def filter():
    if request.method == 'POST':
        genre = request.form['genre']
        lang = request.form['lang']
        comp =  request.form['comp']
        year_begin = request.form['pub-year-begin']
        year_end = request.form['pub-year-end']
        urut_harga = request.form['urut-harga']
        if genre == 'Select' and lang == 'Select' and comp == 'Select' and urut_harga == 'Select':
            return redirect(url_for('home'))
        if genre != 'Select' or lang != 'Select' or year_begin != "" or year_end != "":
            query = 'SELECT * FROM buku WHERE '
        else:
            query = 'SELECT * FROM buku '                
            
        
        if genre != 'Select':
            query+="genres LIKE '%"+genre+"%'"
        if lang != 'Select':
            if genre != 'Select':
                query+=" AND language LIKE '%"+lang+"%'"
            else:
                query+="language LIKE '%"+lang+"%'"
        if comp != 'Select':
            if genre != 'Select' or lang != 'Select':
                query+=" AND compatibility LIKE '%"+comp+"%'"
            else:
                query+="compatibility LIKE '%"+comp+"%'"
        if year_begin and year_end:
            if genre != 'Select' or lang != 'Select' or comp != 'Select':
                qy = " AND YEAR(publication_date) BETWEEN %s AND %s" % (year_begin, year_end)
                query+=qy
            else:
                qy = "YEAR(publication_date) BETWEEN %s AND %s" % (year_begin, year_end)
                query+=qy
        if urut_harga != 'Select':
            query += " ORDER BY "
        else:
            query += ""
        if urut_harga == 'termahal-termurah':
            query+='price DESC, title'
        elif urut_harga == 'termurah-termahal':
            query+='price ASC, title'
        elif urut_harga == 'terbaru-terlama':
            query+='publication_date DESC, title'
        elif urut_harga == 'terlama-terbaru':
            query+='publication_date ASC, title'
        elif urut_harga == 'rating tertinggi-terendah':
            query+='rating DESC, title'
        elif urut_harga == 'rating terendah-tertinggi':
            query+='rating ASC, title'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        books = []
        for entry in result:
            record = {
                'id': entry[0],
                'cover': entry[1],
                'title': entry[2],
                'description': entry[3],
                'author': entry[4],
                'publisher': entry[5],
                'price': 'IDR ' + '{:,}'.format(entry[11]) + '.00',
                'rating': entry[12]
            }
            books.append(record)
        return render_template('home.html', datas = books, genre_list = genre_list(), lang_list = lang_list(), comp_list = comp_list())
      

@app.route('/detail/<int:buku_id>/')
def detail(buku_id):
    datas = get_buku(buku_id)
    return render_template('detail.html',datas=datas)

@app.route('/admin/')
def admin():
    ratecount = countingrate()
    dataBahasa = chartBahasa()
    dataYear = chartYear()
    dataGenre = chartGenre()
    return render_template('admin.html', ratecount=ratecount, dataBahasa=dataBahasa, dataYear=dataYear, dataGenre=dataGenre)

@app.route('/admin/scrape/')
def scrape():
    return render_template('scrape.html')

@app.route('/admin/scrape/report/', methods=['POST'])
def scrape_run():
    url_list = request.form['link_textarea'].split(',')
    report_list = []
    for url in url_list:
        report = 'Scraping ' + url
        try:
            book = scrape_gplay_books(url)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO buku (cover,title,description,author,publisher,publication_date,genres,language,pages,compatibility,price,rating,total_rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (book['Cover'],book['Title'],book['Description'],book['Author'],book['Publisher'],book['Publication Date'],book['Genres'],book['Language'],book['Pages'],book['Compatibility'],book['Price'],book['Rating'],book['Number of Reviewer']))
            conn.commit()
            conn.close()
            report+= ' success\n'
        except Exception as e:
            report+= ' failed ' + repr(e) + '\n'
        
        report_list.append(report)
    return render_template('scrape_report.html', report = report_list)

@app.route('/admin/book_menu/', methods = ['GET', 'POST'])
def admin_book_menu():
    if request.method == 'POST':
        if 'delete_button' in request.form:
            book_title = request.form['delete_button']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM buku WHERE title=%s', (book_title,))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_book_menu'))
        elif 'import_button' in request.form:
            f = request.files['file-to-import']
            f.save('temp/' + f.filename)
            file = open('temp/' + f.filename)
            file_reader = csv.reader(file)
            file_data = list(file_reader)
            for data in file_data:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO buku (cover,title,description,author,publisher,publication_date,genres,language,pages,compatibility,price,rating,total_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12]))
                conn.commit()
                conn.close()
            file.close()
            os.remove('temp/' + f.filename)
            #flash('Import successful!', 'info')
            return redirect(url_for('admin_book_menu'))
        elif 'export_button' in request.form:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT cover,title,description,author,publisher,publication_date,genres,language,pages,compatibility,price,rating,total_rating FROM buku')
            result = cursor.fetchall()
            conn.close()

            books = []
            for entry in result:
                book_data = []
                for data in entry:
                    book_data.append(data)
                books.append(book_data)
            
            f = open('temp/export_books.csv', "w+")
            f.close()

            file = open('temp/export_books.csv', 'w', newline='')
            file_writer = csv.writer(file)
            for book_data in books:
                try:
                    file_writer.writerow(book_data)
                except:
                    continue
            file.close()
            return send_from_directory('temp', 'export_books.csv', as_attachment=True)
            

    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title, author, genres, publisher, publication_date FROM buku')
        result = cursor.fetchall()
        conn.close()
        data = []
        for entry in result:
            book = {
                'title': entry[0],
                'author': entry[1],
                'genres': entry[2],
                'publisher': entry[3],
                'publication_date': entry[4],
            }
            data.append(book)
        return render_template('admin_book_menu.html', book_data = data)

@app.route('/admin/book_menu/export_all/')
def admin_export_all_books():
    return 'export'

@app.route('/admin/book_menu/edit_book/<book_title>/', methods=['GET', 'POST'])
def admin_edit_book(book_title):
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM buku WHERE title=%s', (book_title,))
        result = cursor.fetchone()
        conn.close()
        return render_template('admin_edit_book.html', book_data = result)
    else:
        new_data = {
            'cover': request.form['cvr'],
            'title': request.form['ttl'],
            'desc': request.form['dsc'],
            'author': request.form['auth'],
            'publisher': request.form['pub'],
            'publish date': request.form['pub date'],
            'genres': request.form['gen'],
            'language': request.form['lang'],
            'pages': request.form['pg'],
            'compatibility': request.form['comp'],
            'price': request.form['prc'],
            'rating': request.form['rtg'],
            'num of review': request.form['num rev'],
        }
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM buku WHERE title=%s', (book_title,))
        book_id = str(cursor.fetchone()[0])
        cursor.execute('UPDATE buku SET cover=%s, title=%s, description=%s, author=%s, publisher=%s, publication_date=%s, genres=%s, language=%s, pages=%s, compatibility=%s, price=%s, rating=%s, total_rating=%s WHERE id=%s', (new_data['cover'], new_data['title'], new_data['desc'], new_data['author'], new_data['publisher'], new_data['publish date'], new_data['genres'], new_data['language'], new_data['pages'], new_data['compatibility'], new_data['price'], new_data['rating'], new_data['num of review'], book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_edit_book', book_title=new_data['title']))

@app.route('/admin/dashboard/')
def admin_dashboard():
    ratecount = countingrate()
    dataBahasa = chartBahasa()
    dataYear = chartYear()
    dataGenre = chartGenre()
    return render_template('admin_dashboard.html', ratecount=ratecount, dataBahasa=dataBahasa, dataYear=dataYear, dataGenre=dataGenre)

def countingrate():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rating FROM buku')
    result = cursor.fetchall()
    datarating = []
    for all in result:
        input = all[0]
        input = str(input)
        input = list(input)
        input = int(input[0])
        datarating.append(input)
    datarating = numpy.array(datarating)
    ratecount = {}
    for i in range(5):
        ratecount[i+1] = numpy.count_nonzero(datarating == i+1)
    return ratecount

def chartYear():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT EXTRACT(year FROM publication_date) AS year, COUNT(*) AS number FROM buku GROUP BY EXTRACT(year FROM publication_date);')
    result = cursor.fetchall()
    dataYear = []
    for entry in result:
        record = [entry[0],entry[1]]
        dataYear.append(record)
    conn.close()
    return dataYear

def chartGenre():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT genres FROM buku"
    cursor.execute(query)
    result = cursor.fetchall()
    genre_list = []
    for all in result:
        input = all[0].split(' / ')
        for i in input:
            genre_list.append(i)
    genre_list = list(dict.fromkeys(genre_list))
    dataGenre = {}
    for genres in genre_list:
        like = "%"+genres+"%"
        query = f"SELECT COUNT(genres) FROM buku WHERE genres LIKE '{like}'"
        cursor.execute(query)
        value = cursor.fetchone()
        value = value[0]
        dataGenre[genres]=value
    conn.close()     
    print(dataGenre)  
    return dataGenre