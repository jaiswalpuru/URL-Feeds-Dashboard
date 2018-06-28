#importing packages
from flask import Flask,redirect,url_for,request,render_template
import sqlite3 as sql
from flask_dance.contrib.twitter import make_twitter_blueprint,twitter

#To store the username of the current user authorizing the request of feeds
usernames=[]

app=Flask(__name__)

app.config['SECRET_KEY']='thisissupposedtobesecret'

twitter_blueprint=make_twitter_blueprint(api_key='OL2rJmAPPjJzJXIJOEfGKt4n1',
api_secret='8jcdIqQQE9Nq89vZ6J3I0XhIdTJ0GHiSkWPo7eQ9e3l4IRA2sK')

app.register_blueprint(twitter_blueprint,url_prefix='/twitter_login')

#defining default route
@app.route('/')
def home():
    if(twitter.authorized):
        return redirect(url_for('twitter_login'))
    else:
        return render_template('home.html')

#defining route to twitter login
@app.route('/twitter',methods=['GET','POST'])
def twitter_login():
    if(request.method=='POST'):
        if not twitter.authorized:
            usernames.clear()
            nm=request.form['ID']
            usernames.append(nm)
            return redirect(url_for('twitter.login'))
    else:
        account_info=twitter.get('statuses/home_timeline.json')
        if account_info.ok:
            account_info_json=account_info.json()
        url_links={}
        for tweets in account_info_json:
            video_links=list(tweets['entities']['urls'])
            if(len(video_links)!=0):
                url_links[tweets['created_at']]=tweets['entities']['urls'][0]['expanded_url']
        url_links_dates=list(url_links.keys())
        url_links_urls=list(url_links.values())
        #connecting to database database.db
        with sql.connect("database.db")as con:
            cur=con.cursor()
            for i in range(0,len(url_links_urls)):
                cur.execute("INSERT OR IGNORE INTO FEEDS(ID,timeStamps,url_links)VALUES(?,?,?)",(usernames[0],url_links_dates[i],url_links_urls[i]))
            con.commit()
            return render_template("dashboard.html")
            con.close()

#defining route to dashboard
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    #connecting to database to fetch all the feeds on home_timeline
    con=sql.connect("database.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    nm=usernames[0]
    cur.execute("select * from FEEDS")
    rows=cur.fetchall();
    return render_template("list.html",rows=rows,nm=nm)

if __name__ == '__main__':
    app.run(debug=True)
