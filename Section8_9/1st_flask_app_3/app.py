from flask import Flask, redirect, render_template, request, session, url_for
# Formクラス及び使用するフィールドをインポート
from wtforms import Form, BooleanField, IntegerField, PasswordField, StringField, SubmitField, TextAreaField
# 使用するvalidatorをインポート
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange

import os
import pickle
# from flask_sqlalchemy import SQLAlchemy
import sqlite3
import numpy as np

# ローカルからHshingVectorizerをインポート
from vectorizer import vect

app = Flask(__name__)

### 分類機の準備 ###
# 分類機をでシリアライズ（読み込む）
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir, 'pkl_objects', 'classifier.pkl'), 'rb'))

# DBとアプリ(app.py)を紐づける
# db = SQLAlchemy(app)

# セッションで使用するシークレットキーを設定。本来はランダムな文字列が望ましい
app.config['SECRET_KEY'] = os.urandom(24)

# 入力したレビューを受け取って、そのレビューに対する予測をし、結果を返す
def classify(document):
    label = {0: 'negative', 1: 'positive'}
    X = vect.transform([document])
    y = clf.predict(X)[0]
    proba = clf.predict_proba(X).max()
    return label[y], proba

# モデルを更新する
def train(document, y):
    X = vect.transform([document])
    clf.partial_fit(X, y)


# DBへ書き込む
def sqlite_entry(path, document, y):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("INSERT INTO review_db (review, sentiment, date) VALUES (?, ?, DATETIME('now'))",
     (document, y))
    conn.commit()
    conn.close()


### Flask側の機能 ###
# 名前の登録用クラスを定義。入力した項目に対して検証を行う。
class ReviewForm(Form):
    moviereview = TextAreaField('Write Your Review: ', validators=[DataRequired(), Length(min=15)])
    submit = SubmitField('送信')

# POSTかつバリデーションエラーがない場合は、セッションにレビュー内容を格納してresults.htmlを表示
@app.route('/',methods=['GET', 'POST'])
def index():
    form = ReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        session['moviereview'] = form.moviereview.data
        y, proba = classify(session['moviereview'])
        return redirect('results.html', content=session['moviereview'], prediction=y, probability=round(proba*100, 2))
    return render_template('reviewform.html', form=form)

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/feedback', methods=['POST'])
def feedback():
    form = ReviewForm(request.form)
    session['feedback_button'] = form.feedback_button.data
    session['review'] = form.review.data
    session['prediction'] = form.prediction.data

    inv_label = {'negative': 0, 'positive': 1}
    y = inv_label[session['prediction']]
    if session['feedback_button'] == 'Incorrect':
        y = int(not(y))
    
    train(session['review'], y)
    sqlite_entry(db, session['review'], y)
    return render_template('feedback.html')






if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)