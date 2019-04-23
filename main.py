from flask import Flask, request, redirect, render_template,flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'supersecretkey'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)         
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body
        
@app.route('/')
def index():

    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():

    if(request.method == 'GET' and request.args.get('id')):
        blogPost = Blog.query.filter_by(id=request.args.get('id')).first()
        return render_template('entry.html', title=blogPost.title, body=blogPost.body)
    else:
        return render_template('blog.html', title="Build A Blog", posts=Blog.query.filter_by().all())



@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    if (request.method == 'POST'):
        title = request.form['title']
        body = request.form['body']
        if(not title and not body):
            flash('Please Enter a Title and Body')
            return render_template('newpost.html')
        if(not title):
            flash('Please Enter a Title')
            return render_template('newpost.html')
        if(not body):
            flash('Please Enter Post Body')
            return render_template('newpost.html')
        blogpost = Blog(title=title, body=body)
        db.session.add(blogpost)
        db.session.commit()
        return redirect('/blog?id=' + str(blogpost.id))
    else:
        return render_template('newpost.html')

if  __name__ == "__main__":
    app.run()
              
        



    




