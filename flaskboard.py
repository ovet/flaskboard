"""
flaskboard

A bare essential BBS in Flask
"""

__author__ = 'Rich Moore(eng.richardmoore@gmail.com)'

from flask import Flask, flash, request, abort, render_template, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/posts.db'
# Change before deploy, dont want anyone to know my luggage combination
app.config['SECRET_KEY'] = '12345'
db = SQLAlchemy(app)

# Define SQLAlchemy Models
class Thread(db.Model):
  """
  Thread - The first post of a thread

  Columns :
    id - Primary key
    author - (50)Character string
    title - (100)Character string
    body - Message text
    date - Datetime object, defaults to current time
  """

  id = db.Column(db.Integer, primary_key=True)
  author = db.Column(db.String(50))
  title = db.Column(db.String(100))
  body = db.Column(db.Text)
  date = db.Column(db.DateTime)

  def __init__(self, author, title, body):
    self.author = author
    self.title = title
    self.body = body
    self.date = datetime.utcnow()

  def __repr__(self):
    return '<Thread Title %r>' % self.title

class Post(db.Model):
  """
  Post - The any post that comes after the original

  Columns :
    id - Primary key
    author - (50)Character string
    body - Message text
    thread_id - Foriegn key, Many-to-One relationship
    thread - References the Thread model
    date - Datetime object, defaults to current time
  """

  id = db.Column(db.Integer, primary_key=True)
  author = db.Column(db.String(50))
  body = db.Column(db.Text)
  thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
  thread = db.relationship('Thread',
        backref=db.backref('posts', lazy='dynamic'))
  date = db.Column(db.DateTime)

  def __init__(self, author, body, thread):
    self.author = author
    self.body = body
    self.thread = thread
    self.date = datetime.utcnow()

  def __repr__(self):
    return '<Reply to %r>' % self.thread.title

@app.route('/')
def home():
  """Display the newest 20 threads"""
  threads = Thread.query.order_by(Thread.date.desc()).limit(20).all()
  return render_template('home.html', threads=threads)

@app.route('/new', methods=['POST'])
def add_thread():
  """Proccess adding a new thread and redirect to home()"""
  if request.method == 'POST':
    if request.form['name'] and request.form['title'] and request.form['body']:
      newThread = Thread(request.form['name'], request.form['title'],
                         request.form['body'])
      db.session.add(newThread)
      db.session.commit()
      flash('Message Posted')
  else:
    flash('Required field(s) missing')

  return redirect(url_for('home'))

@app.route('/thread/<int:id>')
def show_thread(id):
  """Display all posts in a thread"""
  currentThread = Thread.query.filter_by(id=id).first()
  return render_template('thread.html', currentThread=currentThread)

@app.route('/thread/<int:id>/new', methods=['POST'])
def add_response(id):
  """Proccess adding a new post to a thread and redirect to show_thread(thread_id)"""
  if request.method == 'POST':
    if request.form['name'] and request.form['body']:
      currentThread = Thread.query.filter_by(id=id).first()
      newPost = Post(request.form['name'], request.form['body'],
                     currentThread)
      db.session.add(newPost)
      db.session.commit()
      flash('Response Posted')
  else:
    flash('Required field(s) missing')
  return redirect(url_for('show_thread',id=id))


if __name__ == '__main__':
  db.create_all()
  app.debug = True
  app.run(host = '0.0.0.0')
