"""
After extrapolating the total number of publications for each NUTS_2 regions, we can compute their specialization index
for each SDG, SDG categories and DT.
"""
import concurrent.futures.process
import itertools

import pandas as pd
from collections import Counter, defaultdict
import multiprocessing
import time
from tqdm import tqdm

start = time.perf_counter()

# Loading dataframes
df_sdg = pd.read_csv("data/dataframes/SDG/SDG_georef_more10_moreNUTS.csv", sep=",")
df_sdg_dt = df_sdg[df_sdg['DST']]
df_sdg = df_sdg.to_dict('records')
df_dt = pd.read_csv("data/dataframes/digital/digital_georef_more10_moreNUTS.csv", sep=",").to_dict('records')

df_sdg_dt = df_sdg_dt.to_dict('records')
lst_dt = ['AI', 'big_data', 'IOT', 'computing_infrastructure', 'blockchain', 'robotics',
          'additive_manufacturing']

lst_sdg = ["SDG" + str(i) for i in range(1, 18)]
lst_cat = ["Environment", "Society", "Economy"]
lst_dt_shortened = ['AI', 'robotics', 'IOT']

lst_cat_dt = ['Environment-AI', 'Environment-robotics', 'Environment-IOT',
              'Society-AI', 'Society-robotics', 'Society-IOT',
              'Economy-AI', 'Economy-robotics', 'Economy-IOT']
df_nuts = pd.read_excel("data/nuts_2/all_publications_NUTS_WOS_extrapolation.xlsx", index_col=0)
lst_nuts_2 = list(df_nuts.index.to_list())

dic_nuts = {nuts: Counter() for nuts in lst_nuts_2}
dic_nuts_sdg = dic_nuts.copy()
dic_nuts_dt = dic_nuts.copy()
dic_nuts_sdg_dt = dic_nuts.copy()


def f_sdg():
    # SDG dataframe
    for row in tqdm(df_sdg):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue

        for sdg in lst_sdg:
            if row[sdg]:
                dic_nuts_sdg[nuts_2][sdg] += 1
        for cat in lst_cat:
            if row[cat]:
                dic_nuts_sdg[nuts_2][cat] += 1


def f_dt():
    # DT dataframe

    for row in tqdm(df_dt):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue
        for dt in lst_dt:
            if row[dt]:
                dic_nuts_dt[nuts_2][dt] += 1


def f_sdg_dt():
    # Intersection
    for row in tqdm(df_sdg_dt):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue
        for cat, dt in itertools.product(lst_cat, lst_dt_shortened):
            if row[cat] and row[dt]:
                dic_nuts_sdg_dt[nuts_2][str(cat) + "-" + str(dt)] += 1


p1 = multiprocessing.Process(target=f_sdg)
p2 = multiprocessing.Process(target=f_dt)
p3 = multiprocessing.Process(target=f_sdg_dt)
p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()

dic_nuts = {nuts2: dic_nuts_sdg[nuts2] + dic_nuts_dt[nuts2] + dic_nuts_sdg_dt[nuts2] for nuts2 in dic_nuts}
df_counter = pd.DataFrame.from_dict(dic_nuts, orient='index')
df_counter.to_pickle("data/nuts_2/df_counter.pkl")
df_nuts.join(df_counter)

# df_nuts.to_excel("data/nuts_2/full_data_on_nuts_2.xlsx")

finish = time.perf_counter()

print(round(finish - start, 2))
