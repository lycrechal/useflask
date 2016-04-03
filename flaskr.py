# all the imports
import os
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from contextlib import closing

#create our little application
app=Flask(__name__)
#config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='rechal',
    PASSWORD='p0o9i8u7'
    ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    rv=sqlite3.connect(app.config['DATABASE'])
    rv.row_factory=sqlite3.Row
    return rv
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
@app.cli.command('initdb') 
def initdb_command(): 
    """Creates the database tables.""" 
    init_db() 
    print('Initialized the database.') 

@app.before_request
def before_request():
    g.db=connect_db()
@app.teardown_request
def teardown_request(exception):
    db=getattr(g,'db',None)
    if db is not None:
        db.close()
    g.db.close()
@app.route('/')
def first_page():
    
    cur=g.db.execute('select title,text from entries order by id desc')
    entries=[dict(title=row[0],text=row[1])for row in cur.fetchall()]
    return render_template('layout.html',entries=entries)
@app.route('/show')
def show_entries():
    
    cur=g.db.execute('select title,text from entries order by id desc')
    entries=[dict(title=row[0],text=row[1])for row in cur.fetchall()]
    return render_template('show_entries.html',entries=entries)
@app.route('/add',methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title,text) values(?,?)',[request.form['title'],request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
@app.route('/delete',methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries (title,text) values(?,?)',[request.form['title'],request.form['text']])
    g.db.commit()
    flash('A entry was successfully delete')
    return redirect(url_for('show_entries')) 
@app.route('/login',methods=['GET','POST'])
def login():
    error=None
    if request.method=='POST':
        if request.form['username']!=app.config['USERNAME']:
            error='Invalid username'
        elif request.form['password']!=app.config['PASSWORD']:
            error='Invalid password'
        else:
            session['logged_in']=True
            flash('You were logged_in')
            return redirect(url_for('show_entries'))
    return render_template('login.html',error=error)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('first_page'))
if __name__=='__main__':
    app.run(host='120.27.119.86')