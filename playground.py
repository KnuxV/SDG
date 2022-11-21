import pandas as pd
import os
from pathlib import Path

from tqdm import tqdm

root = "data/raw/raw_sdg"
lst_df = []
# SDG
for sdg in tqdm(os.listdir(root)):
    print(sdg)
    sdgpath = os.path.join(root, sdg)
    # Target
    for target in os.listdir(sdgpath):
        targetpath = os.path.join(sdgpath, target)
        print(target)
        for file in os.listdir(targetpath):
            filepath = os.path.join(targetpath, file)
