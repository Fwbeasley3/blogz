from flask import Flask, request, redirect, render_template,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash
import re



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'supersecretkey'



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)         
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def get_blogs_by_user(owner):
        return Blog.query.filter_by(owner).all()

    def val_blog(title, body):
        if(not title and not body):
            return 'Please Enter A Title and Body'
        if(not title):
            return 'Please Enter A Title'
        if(not body):
            return 'Please Enter A Post Body'
        return False

   


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25),unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner' )

    def __init__(self,username,password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

def emptyField(str):    #check empty str
    if str !="":
        return True
    else:
        return False

def isLength(length):               #check length of str btw 3 and 20 chr
    if len(length) <=2 or len(length) >=21:
       return True
    else:
        return False

def passMatch(p1,p2):     
    if p1!=p2:
        return True
    else:
        return False


def valid_username(val):                                                            
    valid_username = re.compile("[a-zA-Z0-9_]+\.?[a-zA-Z0-9_]+@[a-z]+\.[a-z]+")
    if valid_username.match(val):
        return True
    else:
        return False

def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    userlist = User.query.filter_by().all()
    return render_template('index.html', userlist=userlist)

@app.route('/login', methods=['POST', 'GET'])             
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = user.username
                flash('Welcome back, '+ user.username + '!')
                return redirect('/newpost')

@app.route('/signup', methods=['POST', 'GET'])   
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
    if not emptyField(username):
        flash('Invalid input, field is empty!')
        return render_template('signup.html')
    if isLength(username):
        flash('Username must be between 3 and 20 characters')
        return render_template('signup.html')
    if " " in username:
        flash('Username must contain no spaces')
        return render_template('signup.html')
    if not valid_username(username):
        flash('Not a valid username, enter valid e-mail')
        return render_template('signup.html')
    if not emptyField(password):
        flash('Invalid input, field is emppty!')
        return render_template('signup.html')
    if isLength(password):
        flash('Password must be between 3 and 20 characters')
        return render_template('signup.html')
    if " " in password:
        flash('Password must contain no spaces')
        return render_template('signup.html')
    if passMatch(password,verify):
        flash('Passwords do not match!')
        return render_template('signup.html')
        
    username_db_count = User.query.filter_by(username=username).count()
    if username_db_count > 0:
        flash('Whoops! "' + username + '" is already taken!')
        return redirect('/signup')
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    session['user'] = user.username
    return redirect("/")
    
@app.route('/blog', methods=['GET'])
def blog():
    user = request.args.get('user')
    blog_id = request.args.get('blog')
    if(blog_id):
        blog = Blog.query.filter_by(id=blog_id).one()
        return render_template("entry.html", blog=blog)
    if(user):
        user = User.query.filter_by(id=request.args.get('user')).one()
        bloglist = Blog.query.filter_by(owner=user).all()
        return render_template("blog.html", bloglist=bloglist)
    bloglist = Blog.query.filter_by().all()
    return render_template("blog.html", bloglist=bloglist)
    
@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()          #new addition

    if (request.method == 'POST'):
        title = request.form['title']
        body = request.form['body']
        val_blog = Blog.val_blog(title,body)              #new addition
        
        if(not title and not body):
            flash('Please Enter a Title and Body')
            return render_template('newpost.html')
        if(not title):
            flash('Please Enter a Title')
            return render_template('newpost.html')
        if(not body):
            flash('Please Enter Post Body')
            return render_template('newpost.html')
        blogpost = Blog(title=title, body=body,owner = owner)
        db.session.add(blogpost)
        db.session.commit()
        return redirect('/blog?blog=' + str(blogpost.id))
        # return render_template('entry.html', blog = blogpost)
    else:
        return render_template('newpost.html')
        
    
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if  __name__ == "__main__":
    app.run()