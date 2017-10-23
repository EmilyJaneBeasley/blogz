from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:sidney@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        if not user:
            flash('User name does not exist. Create account.')
            return render_template('login.html')
        else: 
            flash('Password incorrect')
            return render_template('login.html')
    return render_template('/login.html')
    
        
        
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3:
            flash('User name must be longer than 3 characters')
            return redirect('/signup') 

        if len(password) < 3:
            flash('Password must be longer than 3 characters')
            return redirect('/signup')       
        
        if password != verify:
            flash('Passwords do not match')
            return redirect('/signup')

        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('User name is already taken')
            return redirect('/signup')

        if len(username) > 3 and len(password) > 3 and password == verify and username_db_count == 0:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost',methods=["POST", "GET"])
def new_blog():

    return render_template('newpost.html')

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        return render_template('single_entry.html',blog=blog)
    if request.args.get('user'):
        user_id = request.args.get('user')
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', blogs=blogs)
    if request.method =='POST':
        blog_title = request.form['blog_title']
        blog = request.form['blog']
        owner = User.query.filter_by(username=session['username']).first()
        if not blog_title:
            flash('Please enter a title')
            return render_template('newpost.html')
        if not blog:
            flash('Please enter a blog')
            return render_template('newpost.html')
        else:
            new_blog = Blog(blog_title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
    
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', blogs=blogs, users=users)
       
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()