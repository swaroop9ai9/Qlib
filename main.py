from flask import Flask, redirect, render_template, request, session, url_for, jsonify,flash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import base64
import pytesseract
import io

app = Flask(__name__)       #Initialze flask constructor
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": '',
    "MAIL_PASSWORD": ''
}
app.config.update(mail_settings)
mail = Mail(app)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qlib.sqlite3'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = True

# Models
db = SQLAlchemy(app)
class Post(db.Model):
    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    name = db.Column(db.String(100))
    category = db.Column(db.String(300))
    content = db.Column(db.String(1000))


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    lstatus = db.Column(db.Boolean, default=False, nullable=False)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

db.create_all()
# Index

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')


# Login
def sum(a,b):
    return a+b 


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        # Getting Data
        result = request.form
        password = result["pass"]
        session['email'] = result['email']
        user = User.query.filter_by(email=result["email"]).first()
        if (user is not None) and (user.password_hash == str(result["pass"])):
            person = User.query.filter_by(email=result["email"]).first()
            session['username'] = person.username
            person.lstatus = True
            db.session.commit()
            return render_template("welcome.html", name = person.username)
        else:
            flash("User does not exist, please signup!")
            return render_template("signup.html")

    elif request.method == "GET":
        return render_template("login.html")

@app.route('/logout',methods=['GET','POST'])
def logout():
    person = User.query.filter_by(email=session.get('email',None)).first()
    person.lstatus = False
    db.session.commit()
    return render_template('index.html')





@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == "POST":
        try:
            result = request.form
            user = User(email=result["email"],username=result["name"],password_hash=result["pass"],lstatus=False)
            db.session.add(user)
            db.session.commit()
            with app.app_context():
                msg = Message(subject="Welcome to Qlib,",sender=app.config.get("MAIL_USERNAME"),recipients= [result["email"]],body=''' Welcome to Qlib, Hope you have a great learning experience. \n Nulluis in Verba \n -From Qlib Team''')
            mail.send(msg)
            return flash("Welcome to Qlib")
        except:
            return jsonify("Gotcha, You have already registered with US!")
        return render_template('login.html')
    elif request.method == "GET":
        return render_template("signup.html")


# Posts

@app.route('/indexPosts',methods=['GET','POST'])
def indexPosts():
    if request.method == "GET":
        return render_template('indexPosts.html')

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == "GET":
        posts = Post.query.filter(Post.title.contains(request.args.get('keySearch'))).order_by(Post.title).all()

    return render_template('display.html',posts = posts)

@app.route('/addPost',methods=['GET','POST'])
def addPost():
    if request.method == "GET":
        return render_template('indexPosts.html')
    if request.method == "POST":
        post = Post(title=request.form['title'],name=request.form['name'],category=request.form['category'],content=request.form['content'])
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('indexPosts'))

@app.route('/scan',methods=['GET','POST'])
def scan():
    if request.method == "GET":
        return render_template('scan.html')


@app.route('/capture',methods=['GET','POST'])
def capture():
    if request.method == "POST":
        image = request.form['file']
        imgstring = image.split('base64,')[-1].strip()
        pic = io.StringIO()
        image_string = io.BytesIO(base64.b64decode(imgstring))
        image = Image.open(image_string)

        # Overlay on white background, see http://stackoverflow.com/a/7911663/1703216
        bg = Image.new("RGB", image.size, (255,255,255))
        bg.paste(image,image)
        bg.save('pic.png')
        print(pytesseract.image_to_string(bg))
        return render_template('welcome.html')

@app.route('/welcome',methods=['GET','POST'])
def welcome():
    if request.method == "POST":
        return render_template("welcome.html", name = session.get('username'))


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True,host='127.0.0.1',port=int(os.environ.get('PORT', 4172)))
    app.run()
