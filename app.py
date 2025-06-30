from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from newsapi import NewsApiClient

app = Flask(__name__)

# MySQL configuration directly in app.py
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234567'
app.config['MYSQL_DB'] = 'news_app'
newsapi = NewsApiClient(api_key='a082a29106f646848755d8fedcbdfb76')

mysql = MySQL(app) 


@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    query = ''
    recent_searches = []

    # Handle search
    if request.method == 'POST':
        query = request.form.get('keyword')
        if query:
            news = newsapi.get_everything(q=query, language='en', page_size=100)
            articles = news['articles']
            # Log the search query
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO search_logs (query) VALUES (%s)", (query,))
            mysql.connection.commit()
            cur.close()
    else:
        news = newsapi.get_top_headlines(language='en', page_size=100)
        articles = news['articles']

    # Fetch recent 5 searches
    cur = mysql.connection.cursor()
    cur.execute("SELECT query FROM search_logs ORDER BY fetched_at DESC LIMIT 5")
    recent_searches = [row[0] for row in cur.fetchall()]
    mysql.connection.commit()
    cur.close()

    return render_template('index.html', articles=articles, query=query, recent_searches=recent_searches)

if __name__ == '__main__':
    app.run(debug=True)
