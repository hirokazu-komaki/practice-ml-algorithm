from email.policy import default
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


app = Flask(__name__)
# DBを生成するパスを定義
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # このパスの意味は？
# このpythonスクリプト（app.py）の中で、上記で生成したDBに対して操作をするためのオブジェクト
db = SQLAlchemy(app)


# 以下のクラスとDBのテーブルを紐づけるイメージ
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # DBへ書き込まれているすべてのデータを取得できる(リスト形式)
        posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
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
def delete(id):
    # 編集したい記事のidを指定することで、DBファイルからその記事を取ってくる
    post = Post.query.get(id)

    # 削除ボタンが押されたら、記事が消えるようにしたいから
    db.session.delete(post)
    db.session.commit()
    return redirect('/')
    

     

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


"""
DBファイルを新規で作る時のみ、pythonの対話モードで
from app import db
db.create_all()
とする
"""