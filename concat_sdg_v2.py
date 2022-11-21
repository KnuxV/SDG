"""
Take raw .txt WOS file into a database with every publication annotated
"""
import csv
import glob

import pandas as pd
import os
import tqdm

from utils import c1_to_cn, trim_py

root = "data/raw_data/"

# SDG
for sdg in tqdm.tqdm(os.listdir(root)):
    sdgpath = os.path.join(root, sdg)
    # Target
    for target in os.listdir(sdgpath):
        targetpath = os.path.join(sdgpath, target)
        for file in os.listdir(targetpath):
            filepath = os.path.join(targetpath, file)
            if os.path.isfile(filepath):
                print(filepath)
                df = pd.read_csv(filepath, sep='\t', encoding='utf-8', index_col=False,
                                 on_bad_lines="skip", quoting=csv.QUOTE_NONE)

                df = df.dropna(
                    subset=['DT', 'AU', 'TI', 'LA', 'DE', 'AB', 'C1', 'PY'])
                df = c1_to_cn(df)
                df = trim_py(df, 2010, 2022)




if __name__ == '__main__':
    pass
