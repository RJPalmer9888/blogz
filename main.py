from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:KPcp5540@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(600))

    def __init__(self, title, content):
        self.title = title
        self.content = content


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    val = request.args.get("id")
    try:
        if val.isdigit() == True:
            blog = Blog.query.filter_by(id=val).first()
            return render_template('singleblog.html', blog=blog)
    except:

        return render_template('blog.html',title="Build-a-Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
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
            new_blog = Blog(blog_title, blog_content)
            db.session.add(new_blog)
            db.session.commit()
    
            return redirect('/blog')
        else:
            return render_template('newblog.html',title="Build-a-Blog", title_error=title_error, content_error=content_error, content=blog_content, name=blog_title)

    return render_template('newblog.html',title="Build-a-Blog")

    



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