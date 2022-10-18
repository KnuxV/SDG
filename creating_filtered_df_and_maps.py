"""
For each SDG / cat_of_SDGs /with or without DST, we create a new folder with a dataframe/
df_mentions/ df_edges and 3 graphs
"""
import os

import pandas as pd
from utils import filter_w_sdg
from network_graph import draw_network_map, unique_actors
import time

df = pd.read_pickle("data/output/all_sdg_fixed_dst.pkl")

dic_cat = {}
for cat in ["Environment", "Society", "Economy"]:
    df_cat = df[df[cat]]
    dic_cat[cat] = df_cat

for typ in ["Continent", "World", "Europe"]:
    folder = "/home/kevin-work/PycharmProjects/SDG_DST/img/network_map/category/"
    for cat, df_cat in dic_cat.items():
        print(cat + " " + typ)
        draw_network_map(dataframe=df_cat, map_filter=typ,
                         folder=folder,
                         name=typ + " " + cat,
                         save=True, max_num_actors='max')

df_dst = df[df["DST"]]
for typ in ["Continent", "World", "Europe"]:
    folder = "/home/kevin-work/PycharmProjects/SDG_DST/img/network_map/dst/"
    for name, df_i in {"df": df, "df_dst": df_dst}.items():
        draw_network_map(dataframe=df_i, map_filter=typ,
                         folder=folder,
                         name=typ + " " + name,
                         save=True, max_num_actors='max')

"""

for i in range(1, 18):
    sdg_col = 'SDG' + str(i)
    folder = "/media/kevin-main/My Passport/SDG/img/network_map/"+sdg_col+"/"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    df_sdg = filter_w_sdg(df, [sdg_col])
    df_sdg.to_pickle(folder+sdg_col+".pkl")

    for typ in ['Continent', 'World', 'Europe']:
        draw_network_map(dataframe=df_sdg, map_filter=typ,
                         folder=folder,
                         name=sdg_col+'_'+typ,
                         save=True, max_num_actors='max')

    df_sdg_dst = filter_w_sdg(df_sdg, ['DST'])
    for typ in ['Continent', 'World', 'Europe']:
        draw_network_map(dataframe=df_sdg_dst, map_filter=typ,
                         folder=folder,
                         name=sdg_col+'_dst_'+typ,
                         save=True, max_num_actors='max')

for elem in ['Society', 'Economy', 'Environment']:
    folder = "/media/kevin-main/My Passport/SDG/img/network_map/" + elem + "/"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    df_sdg = filter_w_sdg(df, [elem])
    df_sdg.to_pickle(folder+elem+".pkl")

    for typ in ['Continent', 'World', 'Europe']:
        draw_network_map(dataframe=df_sdg, map_filter=typ,
                         folder=folder,
                         name=elem+'_'+typ,
                         save=True, max_num_actors='max')

    df_sdg_dst = filter_w_sdg(df_sdg, ['DST'])
    for typ in ['Continent', 'World', 'Europe']:
        draw_network_map(dataframe=df_sdg_dst, map_filter=typ,
                         folder=folder,
                         name=elem+'_dst_'+typ,
                         save=True, max_num_actors='max')

df_dst = filter_w_sdg(df, ['DST'])
folder = "/media/kevin-main/My Passport/SDG/img/network_map/" + "DST" + "/"
for typ in ['Continent', 'World', 'Europe']:
    draw_network_map(dataframe=df_dst, map_filter=typ,
                     folder=folder,
                     name="DST" + '_' + typ,
                     save=True, max_num_actors='max')
"""
