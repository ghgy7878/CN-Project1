import os
import sqlite3
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime


db_connection_count = 0

# Function to get a database connection.

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get all posts
def get_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts

#Function to get all logs with timestamp
def log_msg(message):
    time = datetime.now().strftime('%d-%m-%Y, %H:%M:%S')
    return app.logger.info('%(time)s, %(message)s' %{"time": time, "message": message})

def log_error_msg(message):
    time = datetime.now().strftime('%d-%m-%Y, %H:%M:%S')
    return app.logger.error('%(time)s, %(message)s' %{"time": time, "message": message})

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


#Healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(response=json.dumps({"result":"OK - healthy"}),status=200,mimetype='application/json')
    return response

#Metrics endpoint
@app.route("/metrics")
def metrics():
    all_posts = get_posts()

    response = app.response_class(response=json.dumps({"db_connection_count": db_connection_count,"post_count": len(all_posts)}),status=200,mimetype='application/json')

    return response

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# if the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      log_error_msg('A non-existing article is accessed and a 404 page is returned.')
      return render_template('404.html'), 404
    else:
      title = post['title']
      log_msg('Article "%(title)s" retrieved' % {"title": title})
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    log_msg('The "About Us" page is retrieved.')
    return render_template('about.html')

# Define the Post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            
            connection.commit()
            connection.close()
            log_msg('A new article "%(title)s" is created!' % {"title": title})

            return redirect(url_for('index'))

    return render_template('create.html')

# Start the application on port 3111
if __name__ == "__main__":
   ## Stream logs to app.log file
   logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
   logging.basicConfig(filename='app.log')

   app.run(host='0.0.0.0', port='3111')
