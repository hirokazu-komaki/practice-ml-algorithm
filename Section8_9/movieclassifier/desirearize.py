import imp
import pickle
import re
import os
from vectorizer import vect
import numpy as np

# ベクタライザのインポートと保存した分類機モデルのデシリアライズ
clf = pickle.load(open(os.path.join('pkl_objects', 'classifier.pkl'), 'rb'))

label = {0: 'negative', 1: 'positive'}
example = ["I love this movie"]
X = vect.transform(example)
print("Prediction: {}\nProbability: {:.2f}".format(label[clf.predict(X)[0]], np.max(clf.predict_proba(X))*100))