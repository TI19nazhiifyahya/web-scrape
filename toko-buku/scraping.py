import requests,mysql.connector
from flask import request
from bs4 import BeautifulSoup
#from flask import Flask

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
    price_final = 'IDR ' + "{:,.2f}".format(price_idr)

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

#app = Flask(__name__)
book = scrape_gplay_books('https://play.google.com/store/books/details/Inori_I_m_in_Love_with_the_Villainess_Light_Novel?id=QVgsEAAAQBAJ')
# print(book)
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('INSERT INTO buku (cover,title,description,author,publisher,publication_date,genres,language,pages,compatibility,price,rating,total_rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(book['Cover'],book['Title'],book['Description'],book['Author'],book['Publisher'],book['Publication Date'],book['Genres'],book['Language'],book['Pages'],book['Compatibility'],book['Price'],book['Rating'],book['Total Rating']))
conn.commit()
conn.close()


'''
app.config['MONGODB_SETTINGS'] = {
    'db': 'your_database',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class Book(db.Document):
    Cover = db.StringField()
    Title = db.StringField()
    Description = db.StringField()
    Author = db.StringField()
    Publisher = db.StringField()
    Publication_date = db.StringField()
    Genres = db.StringField()
    Language = db.StringField()
    Pages = db.StringField()
    Compatibility = db.StringField()
    Price = db.StringField()
    Rating = db.StringField()
    Total_rating = db.StringField()
'''