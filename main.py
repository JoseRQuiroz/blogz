from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY'] = True
db = SQLAlchemy(app)
app.secret_key = "VoTe4PeDr2020"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)




@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("single_user.html", page_title=user.username + "'s Posts!", user_blogs=user_blogs)

    single_post = request.args.get("id")
    if single_post:
        blog = Blog.query.get(single_post)
        return render_template("viewblogpost.html", blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', page_title="All Blog Posts!", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        title_entry = request.form['title']
        body_entry = request.form['body']

        title_error = ''
        body_error = ''

        if len(title_entry) == 0:
            title_error = "🚨You Need A Title"
        if len(body_entry) == 0:
            body_error = "🚨Content Needed"

        if title_error or body_error:
            return render_template('newpost.html', titlebase="New Entry", title_error=title_error,
                                   body_error=body_error, title=title_entry, body_name=body_entry)

        else:
            if len(title_entry) and len(body_entry) > 0:
                owner = User.query.filter_by(username=session['username']).first()
                new_entry = Blog(title_entry, body_entry, owner)
                db.session.add(new_entry)
                db.session.commit()
                return redirect("/blog?id=" + str(new_entry.id))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    verify_error = ''
    username_error = ''
    password_error = ''

    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3 or len(username) > 20:
            username_error = "🚨 Username Is Not Valid"

        if len(password) < 3 or len(password) > 20:
            password_error = "🚨 Password Is Not Valid"

        if password != verify:
            verify_error = "🚨 Passwords Don't Match"

        if username_error != '' or password_error != '' or verify_error != '':
            return render_template('signup.html', username=username, username_error=username_error,
                                   password_error=password_error, verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "🚨 Duplicate Username PLease Select A Differnet Name"
            return render_template('signup.html', username_error=username_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/newpost')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "🚨Username Does Not Exist. Click Above to Regiser"
            return render_template('login.html', username_error=username_error)

    else:
        return render_template('login.html')




if __name__ == '__main__':
    app.run()