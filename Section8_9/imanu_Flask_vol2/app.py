from cgi import print_arguments
from cmath import log
from email.policy import default
from syslog import LOG_INFO
from tabnanny import check

from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap

from datetime import datetime
import pytz
import os

# ユーザ登録時にPWをハッシュ化、ログイン時に入力したPWが登録したハッシュ値と同じハッシュ値かをチェック
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# DBを生成するパスを環境変数に定義
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # このパスの意味は？
# ログイン情報を暗号化するための鍵情報を環境変数に定義
app.config['SECRET_KEY'] = os.urandom(24)
# このpythonスクリプト（app.py）の中で、上記で生成したDBに対して操作をするためのオブジェクト
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

# ログインに関連する機能を持っているクラスをインスタンス化
login_manager = LoginManager()
# 今回のアプリ(app.py)とログイン機能を紐づける
login_manager.init_app(app)


# 以下のクラスとDBのテーブルを紐づけるイメージ
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

# ログイン機能を実装するためのクラス(ログインするためには、ユーザ情報が必要だから、ユーザ情報を保持したDBを作成すると同時に、そのDBにログイン機能を付加する)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12), unique=True)

# ログインした際のユーザのセッション情報などを・・・(必須の機能)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
@login_required # トップ画面には、ログインしているユーザ以外はアクセスできなくなる、ようにするためのデコレータ
def index():
    if request.method == 'GET':
        # DBへ書き込まれているすべてのデータを取得できる(リスト形式)
        posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
@login_required # 新規投稿は、ログインしているユーザ以外はアクセスできなくなる、ようにするためのデコレータ
def create():
    # HTTPリクエストがPOSTの場合、create.html内で定義している'name'の中身（これはweb上で、フォームで送信した(POSTした)タイトルとその内容）を取得する
    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')

        # DBファイルへ書き込みたいデータ（上記で取得したデータ）を定義する
        post = Post(title=title, body=body)

        # DBファイルへ実際に追加する
        db.session.add(post)

        # コミットして保存
        db.session.commit()

        # DBへ書き込めたらトップページに戻る
        return redirect('/')
    else:
        return render_template('create.html')

    
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required # 編集は、ログインしているユーザ以外はアクセスできなくなる、ようにするためのデコレータ
def update(id):
    # 編集したい記事のidを指定することで、DBファイルからその記事を取ってくる
    post = Post.query.get(id)

    # HTTPリクエストがGETの場合、つまり編集したい記事をとってきたい時
    if request.method == "GET":
        return render_template('update.html', post=post)
    else: # 記事を編集する時（つまりPOSTする時）
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required # 削除は、ログインしているユーザ以外はアクセスできなくなる、ようにするためのデコレータ
def delete(id):
    # 編集したい記事のidを指定することで、DBファイルからその記事を取ってくる
    post = Post.query.get(id)

    # 削除ボタンが押されたら、記事が消えるようにしたいから
    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # HTTPリクエストがPOSTの場合、create.html内で定義している'name'の中身（これはweb上で、フォームで送信した(POSTした)タイトルとその内容）を取得する
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # DBファイルへ書き込みたいデータ（上記で取得したデータ）を定義する
        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        # DBファイルのUserテーブルへ実際に追加する
        db.session.add(user)

        # コミットして保存
        db.session.commit()

        # DBへ書き込めたらログイン画面に戻る
        return redirect('/login')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 例外処理を実装してみよう！！！（usernameとpasswdがなかったら・・・みたいな処理が書かれていないから）
    # HTTPリクエストがPOSTの場合、create.html内で定義している'name'の中身（これはweb上で、フォームで送信した(POSTした)タイトルとその内容）を取得する
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # Userテーブル内にあるusernameとformに入力されたusernameが一致するかをチェック
        user = User.query.filter_by(username=username).first() # DBのUserテーブル内にあるusername=formで入力したusername
        # 次にpasswordが正しいかをチェック
        if check_password_hash(user.password, password): # DBのUserテーブルに定義されたPW, formで入力したPW
            # 入力したuser情報でlogin
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required # logout画面には、ログインしているユーザ以外はアクセスできなくなる、ようにするためのデコレータ
def logout():
    logout_user()
    return redirect('/login')
     

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


"""
DBファイルを新規で作る時のみ、pythonの対話モードで
from app import db
db.create_all()
とする
"""