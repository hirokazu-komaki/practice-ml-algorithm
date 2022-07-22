import os
import pyprind
import pandas as pd
import os

# basepathに入っている値を、展開した映画レビューデータセットのディレクトリに置き換える
basepath = "aclImdb"
labels = {'pos': 1, 'neg': 0}
pbar = pyprind.ProgBar(50000)
df = pd.DataFrame()
for s in ('test', 'train'):
    for l in ('pos', 'neg'):
        path = os.path.join(basepath, s, l)
        for file in os.listdir(path):
            with open(os.path.join(path, file), "r", encoding="utf-8") as infile:
                txt = infile.read()
            df = df.append([[txt, labels['pos']]], ignore_index=True)
            pbar.update()