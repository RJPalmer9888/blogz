from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:KPcp5540@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'KPcp5540'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(600))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    users = User.query.all()
    postval = request.args.get("id")
    userval = request.args.get("user")
    
    try:
        if postval.isdigit() == True:
            blog = Blog.query.filter_by(id=postval).first()
            return render_template('singleblog.html', blog=blog, users=users)
    except:
        try:
            print(userval.isdigit())
            if userval.isdigit() == True:
                user = User.query.filter_by(id=userval).first()
                users = User.query.all()
                blogs = Blog.query.filter_by(owner_id=userval).all()
                return render_template('singleuser.html', users=users, blogs=blogs)
        except:

            return render_template('blog.html',title="Build-a-Blog", blogs=blogs, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['content']

        title_error = ''
        content_error = ''

        if blog_title == '':
            title_error = 'Title cannot be blank'
        
        if blog_content == '':
            content_error = 'Content cannot be blank'
        
        if not title_error and not content_error:
            new_blog = Blog(blog_title, blog_content, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        
        else:
            return render_template('newblog.html',title="Build-a-Blog", title_error=title_error, content_error=content_error, content=blog_content, name=blog_title)

    return render_template('newblog.html',title="Build-a-Blog")

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user: 
            if user.password == password:
                session['username'] = username
                flash("Welcome!")
                return redirect('/newpost')
            else:
                login_error = 'Password is incorrect'
                password = ''
                return render_template('login.html',title="User Login", login_error=login_error)
        else:
            login_error = 'User does not exist'
            password = ''
            return render_template('login.html',title="User Login", login_error=login_error)

    return render_template('login.html',title="User Login")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        name_error = ''
        password_error = ''
        dupe_error = ''

        if username == '':
            name_error = 'Username cannot be blank'
        else:
            if ' ' in username:
                name_error = 'Username cannot contain spaces'
            else:
                if len(username) < 3 or len(username) > 20:
                    name_error = 'Username must be between 3 and 20 characters'

        if password != password2:
            password_error = 'Passwords do not match'
            password = ''
            password2 = ''
        else:
            if password == '':
                password_error = 'Password cannot be blank'
                password = ''
                password2 = ''
            else:
                if ' ' in password:
                    password_error = 'Password cannot contain spaces'
                    password = ''
                    password2 = ''
                else:
                    if len(password) < 3 or len(password) > 20:
                        password_error = 'Password must be between 3 and 20 characters'
                        password = ''
                        password2 = ''
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            dupe_error = 'User already exists, please log in'
            password = ''
            password2 = ''

        if not name_error and not password_error and not dupe_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            
            return redirect('/newpost')

        else:
            return render_template('signup.html',title="New Blog User", name_error=name_error, password_error=password_error, dupe_error=dupe_error, username=username, password=password, password2=password2)

    return render_template('signup.html',title="New Blog User")

    
@app.route('/', methods=['POST', 'GET'])
def index():
    
    users = User.query.all()
    return render_template('index.html',title="Build-a-Blog", users=users)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.deleted = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')


if __name__ == '__main__':
    app.run()