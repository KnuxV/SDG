"""
Created by kevin-desktop, on the 13/02/2023
"""
import os
import re

import numpy as np
import pandas as pd
import tqdm
from tqdm.notebook import trange, tqdm
from tqdm import tqdm
import multiprocessing
from multiprocessing import Pool
import time


def add_most_cited_pub(set_pubs) -> tuple[str, int, int]:
    """
    From a set of publications (WOS ID), query the full_pubs dataframe to look for the most cited publications within
    that set.
    Args:
        set_pubs (list(set)):

    Returns:
        the title, year and number of citations of that most cited publication
    """
    set_pubs = set_pubs[0]
    most_cited_pub_title = ""
    most_cited_pub_tot_citation, most_cited_pub_year = -1, -1
    for pub_id in set_pubs:
        py, tc, ti = dic_full[pub_id].values()
        if tc > most_cited_pub_tot_citation:
            most_cited_pub_tot_citation = tc
            most_cited_pub_title = ti
            most_cited_pub_year = py
    return most_cited_pub_title, most_cited_pub_year, most_cited_pub_tot_citation


df_full = pd.read_pickle("data/dataframes/full_pubs.pkl")
# df_full to dict
dic_full = df_full.set_index('UT')[['PY', 'TC', 'TI']].to_dict(orient='index')

if __name__ == '__main__':
    start = time.time()

    # load dataframes // They are split in a folder
    input_path = "data/dataframes/authors/authors_w_cn/"
    for df_path in os.listdir(input_path):
        full_path = os.path.join(input_path, df_path)
        df_auth = pd.read_pickle(full_path)
        # Dataframe to dic, using the only column we need (lst_publications)
        auth = df_auth[['lst_publications']].to_dict(orient='split')
        tuple_auths = auth['data']

        # Multiprocessing
        with Pool(8) as pool:
            # Mapping fonction to input dataframe
            results = pool.map(add_most_cited_pub, tuple_auths)
            # Creating 3 new columns
            ti, py, tc = zip(*results)
            df_auth['TI'], df_auth['PY'], df_auth['TC'] = np.array(ti), np.array(py), np.array(tc)
            # Saving to a new folder
            full_exit_path = os.path.join("data/dataframes/authors/authors_w_cn_title", df_path)
            df_auth.to_pickle(full_exit_path)

        end = time.time()
        print(end - start)



