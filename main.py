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
    

    def __init__(self, title='', body=''):
        self.title = title
        self.body = body

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, user_name='', password=''):
        self.user_name = user_name
        self.password = password

@app.route("/login", methods=['GET', 'POST'])
def login():
    

    if request.method == 'POST':
        password = request.form['password']
        user_name = request.form['user_name']
        user = User.query.filter_by(user_name=user_name).first()
        
        if user and user.password == password:
            session['user_name'] = user_name
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
        user_name = request.form['user_name']
        password = request.form['password']
        verify = request.form['verify']

        if len(user_name) < 3:
            flash('User name must be longer than 3 characters')
            return redirect('/signup') 

        if len(password) < 3:
            flash('Password must be longer than 3 characters')
            return redirect('/signup')       
        
        if password != verify:
            flash('Passwords do not match')
            return redirect('/signup')

        user_name_db_count = User.query.filter_by(user_name=user_name).count()
        if user_name_db_count > 0:
            flash('User name is already taken')
            return redirect('/signup')


        user = User(user_name=user_name, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.user_name
        return redirect("/newpost")
    else:
        return render_template('signup.html')



@app.route('/blog', methods=['POST','GET'])
def index():
    if request.args:
        blog_id=request.args.get("id")
        blog=Blog.query.get(blog_id)

        return render_template('single_entry.html',blog=blog)

    else:
        blogs=Blog.query.all()
        return render_template('blog.html', blogs=blogs)



@app.route('/newpost',methods=["POST", "GET"])
def add_blog():
    if request.method=="GET":
        return render_template('newpost.html')

    title_error=''
    body_error=''

    if request.method=="POST":
        blog_title=request.form['title']
        blog_body=request.form['body']
        


    if not title_error and not body_error:
        new_blog=Blog(blog_title,blog_body)
        db.session.add(new_blog)
        db.session.commit()
        query_param_url = "/blog?id=" + str(new_blog.id)

        return redirect(query_param_url)

    if blog_body == '':
        blog_title = request.form['title']
        return render_template('newpost.html', blog_title=blog_title)

    if blog_title == '':
        blog_body = request.form['body']
        return render_template('newpost.html', blog_body=blog_body)



    else:

        return render_template('newpost.html', title_error=title_error, body_error=body_error,blog_title=blog_title,blog_body=blog_body)

if __name__ == '__main__':
    app.run()