"""
Created by kevin-desktop, on the 13/02/2023
"""
import os
import re

import numpy as np
import pandas as pd
from multiprocessing import Pool
import time

reg = re.compile(r"(\[([^\[\]]+)])? (?P<adress>[^\[\];]+);?")

dic_country = {'Peoples R China': "China",
               'England': 'United Kingdom',
               'Scotland': 'United Kingdom',
               'Wales': 'United Kingdom',
               'Northen Ireland': 'United Kingdom',
               'Northern Ireland': 'United Kingdom',
               'North Ireland': 'United Kingdom',
               'U Arab Emirates': 'United Arab Emirates',
               'Bosnia & Herceg': 'Bosnia and Herzegovina',
               'Trinidad Tobago': 'Trinidad and Tobago',
               'North Macedonia': 'Macedonia',
               'Papua N Guinea': 'Papua New Guinea',
               'DEM REP CONGO': 'Congo [DRC]',
               'Rep Congo': 'Congo [DRC]',
               'BELARUS': 'Belarus',
               'Cote Ivoire': 'Cote d\'Ivoire',
               'Marshall Island': 'Marshall Islands',
               'Dominican Rep': 'Dominican Republic',
               'Turks & Caicos': 'Turks and Caicos Islands',
               'St Helena': 'Saint Helena',
               'St Kitts & Nevi': 'Saint Kitts and Nevis',
               'St Vincent': 'Saint Vincent and the Grenadines',
               'Antigua & Barbu': 'Antigua and Barbuda',
               'Cent Afr Republ': 'Central African Republic',
               'Neth Antilles': 'Netherlands Antilles',
               }


def add_country(set_names: set, set_pubs: set):
    """
    From a set of names and a set of pubs, query the
    Args:
        set_names:
        set_pubs:

    Returns: nothing

    """
    # Case where there is no name, therefore
    if len(set_names) == 0:
        return 'unknown'

    dic_country_year = {}
    # Iterating over publications
    for pub_id in set_pubs:
        py, c1 = dic_full[pub_id].values()
        # Iterating over addresses in c1_col
        for addr in re.finditer(reg, c1):
            for name in set_names:
                if name in addr.group(0):
                    c = addr.group().split(', ')[-1].replace(";", "")
                    if "USA" in c:
                        c = "United States"
                    elif c in dic_country:
                        c = dic_country[c]
                    dic_country_year[c] = py
    if len(dic_country_year) > 0:
        country = max(dic_country_year, key=dic_country_year.get)
    else:
        country = "unknown"

    return country


# Loading dataframe and turning it into a dict
df_full = pd.read_pickle("data/dataframes/full_pubs.pkl")
dic_full = df_full.set_index('UT')[['PY', 'C1']].to_dict(orient='index')


def multi_run_wrapper(args):
    return add_country(*args)


if __name__ == '__main__':
    # Working on a split of the database, all subsets are store in the folder below
    for df_path in os.listdir("data/dataframes/authors/"):
        start = time.time()
        full_path = os.path.join("data/dataframes/authors/", df_path)
        df_auth = pd.read_pickle(full_path)
        # Dataframe to dict of just names and pubs for speed
        auth = df_auth[['name', 'lst_publications']].to_dict(orient='split')
        tuple_auths = auth['data']
        print(f"{df_path} is loaded.")
        # Multiprocessing using a wrapper
        with Pool(16) as pool:
            lst_country = pool.map(multi_run_wrapper, tuple_auths)
            df_auth['CN'] = np.array(lst_country)
            full_exit_path = os.path.join("data/dataframes/authors/authors_w_cn", df_path)
            df_auth.to_pickle(full_exit_path)
