from ast import Sub
from flask import Flask, redirect, render_template, request, session, url_for
# Formクラス及び使用するフィールドをインポート
from wtforms import Form, BooleanField, IntegerField, PasswordField, StringField, SubmitField, TextAreaField
# 使用するvalidatorをインポート
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange

import os


app = Flask(__name__)

# セッションで使用するシークレットキーを設定。本来はランダムな文字列が望ましい
app.config['SECRET_KEY'] = os.urandom(24)

# 名前の登録用クラスを定義。入力した項目に対して検証を行う。
class Registration(Form):
    name = StringField('名前: ', validators=[DataRequired()])
    submit = SubmitField('登録')

# POSTかつバリデーションエラーがない場合は、セッションに入力内容を格納してregistered.htmlを表示
@app.route('/',methods=['GET', 'POST'])
def index():
    form = Registration(request.form)
    if request.method == 'POST' and form.validate():
        session['name'] = form.name.data
        return redirect(url_for('registered'))
    return render_template('register.html', form=form)

@app.route('/registered')
def registered():
    return render_template('registered.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)