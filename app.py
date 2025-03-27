from flask import Flask
import requests
from scraping.newsCollector import news_collect
from db.retrival import get_breaking_news
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)
scheduler = BackgroundScheduler()
@app.route('/')
def hello_world():
   return 'Hello World'

@app.get('/news_collecter')
def news_collector():
    response = get_breaking_news()
    
    return response

if __name__ == '__main__':
   scheduler.add_job(news_collect, 'cron', day='*', month='*', year='*', hour='*', minute='0')
   scheduler.start()
   app.run(debug = True)