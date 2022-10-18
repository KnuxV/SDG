"""
22 Sep 2022
After extrapolating the total number of publications for each NUTS_2 regions, we can compute their specialization index
for each SDG, SDG categories and DT.
"""
import itertools
import pickle
from collections import Counter

import pandas as pd
from tqdm import tqdm

lst_dt = ['AI', 'big_data', 'IOT', 'computing_infrastructure', 'blockchain', 'robotics',
          'additive_manufacturing']

lst_sdg = ["SDG" + str(i) for i in range(1, 18)]
lst_cat = ["Environment", "Society", "Economy"]
lst_dt_shortened = ['AI', 'robotics', 'IOT']

lst_cat_dt = ['Environment-AI', 'Environment-robotics', 'Environment-IOT',
              'Society-AI', 'Society-robotics', 'Society-IOT',
              'Economy-AI', 'Economy-robotics', 'Economy-IOT']


def extrapolation_total_pubs_on_nuts():
    """
    generate an excel file with all the NUTS2 regions
    :return:
    """
    df_dt = pd.read_csv("data/dataframes/digital/digital_georef_more10_moreNUTS.csv",
                        sep=",", index_col=0)
    df_sdg = pd.read_csv("data/dataframes/SDG/SDG_georef_more10_moreNUTS.csv",
                         sep=",", index_col=0)

    df_nuts = df_dt[['AU', 'NUTS_0', "NUTS_2"]].groupby(['NUTS_2', 'NUTS_0']).count()
    df_nuts_0 = df_dt[['AFF_IN_PAPER', 'NUTS_0']].groupby(['NUTS_0'], as_index=False).count()
    df_nuts = df_nuts.reset_index()
    df_nuts = df_nuts.merge(df_nuts_0, on='NUTS_0')
    df_nuts = df_nuts.rename(columns={'AU': 'total_nuts2_dt', 'AFF_IN_PAPER': 'total_nuts0_dt'})

    df_nuts_sdg = df_sdg[['AU', 'NUTS_0', "NUTS_2"]].groupby(['NUTS_2', 'NUTS_0']).count()
    df_nuts_0_sdg = df_sdg[['AFF_IN_PAPER', 'NUTS_0']].groupby(['NUTS_0'], as_index=False).count()
    df_nuts_sdg = df_nuts_sdg.reset_index()
    df_nuts_sdg = df_nuts_sdg.merge(df_nuts_0_sdg, on='NUTS_0')
    df_nuts_sdg = df_nuts_sdg.rename(columns={'AU': 'total_nuts2_sdg', 'AFF_IN_PAPER': 'total_nuts0_sdg'})

    df_nuts = df_nuts.set_index(['NUTS_2', 'NUTS_0']).join(df_nuts_sdg.set_index(['NUTS_2', 'NUTS_0']))
    df_nuts.reset_index(inplace=True)
    df_full = pd.read_excel("data/total_number_pubs_2010_2022.xlsx", index_col=0, header=1)
    tot_country = df_full.loc['TOT', :].to_dict()
    df_nuts.loc[:, "total_country"] = df_nuts['NUTS_0'].map(tot_country)
    df_nuts.loc[:, "total_nuts2"] = \
        round(df_nuts.loc[:, "total_country"] * (df_nuts.loc[:, "total_nuts2_dt"] + df_nuts.loc[:, "total_nuts2_sdg"]) / \
        (df_nuts.loc[:, "total_nuts0_dt"] + df_nuts.loc[:, "total_nuts0_sdg"]),3)

    df_nuts.to_excel("data/nuts_2/nuts2_all_pubs.xlsx")


def count_publications_per_nuts():
    """
    create and update full_data_on_nuts_2.xlsx counting publications
    for each category of SDG, SDGcat and DT
    Returns
    -------

    """
    # Loading dataframes
    df_sdg = pd.read_csv("data/dataframes/SDG/SDG_georef_more10_moreNUTS.csv", sep=",")
    df_dt = pd.read_csv("data/dataframes/digital/digital_georef_more10_moreNUTS.csv", sep=",")
    df_sdg_dt = df_sdg[df_sdg['DST']]
    df_nuts = pd.read_excel("data/nuts_2/nuts2_all_pubs.xlsx", index_col=0)
    df_nuts = df_nuts.dropna().set_index("NUTS_2")
    lst_nuts_2 = list(df_nuts.index.to_list())
    dic_nuts = {nuts: Counter() for nuts in lst_nuts_2}

    # SDG dataframe
    for ind, row in tqdm(df_sdg.iterrows(), total=df_sdg.shape[0]):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue

        for sdg in lst_sdg:
            if row[sdg]:
                dic_nuts[nuts_2][sdg] += 1
        for cat in lst_cat:
            if row[cat]:
                dic_nuts[nuts_2][cat] += 1

    # DT dataframe
    for ind, row in tqdm(df_dt.iterrows(), total=df_dt.shape[0]):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue
        for dt in lst_dt:
            if row[dt]:
                dic_nuts[nuts_2][dt] += 1

    # Intersection
    for ind, row in tqdm(df_sdg_dt.iterrows(), total=df_sdg_dt.shape[0]):
        nuts_2 = row['NUTS_2']
        if nuts_2 not in lst_nuts_2:
            continue
        for cat, dt in itertools.product(lst_cat, lst_dt_shortened):
            if row[cat] and row[dt]:
                dic_nuts[nuts_2][str(cat) + "-" + str(dt)] += 1

    df_counter = pd.DataFrame.from_dict(dic_nuts, orient='index')
    df_counter.to_pickle("data/nuts_2/df_counter.pkl")
    df_nuts = df_nuts.join(df_counter)

    df_nuts.to_excel("data/nuts_2/full_data_on_nuts_2.xlsx")


def count_world_publication():
    """
    create and update full_data.xlsx which adds one more row to
    full_data_on_nuts.xlsx. That column is the world row counting
    all publication for each category of sdg, dt and sdgcat.
    :return:
    """
    world = Counter()
    world['total_country'] = 24920687
    with open('data/json/dt_long.pickle', 'rb') as f_dt:
        dataframe = pickle.load(f_dt)
    for row in tqdm(dataframe):
        for dt in lst_dt:
            if row[dt]:
                world[dt] += 1

    with open('data/json/sdg_long.pickle', 'rb') as f_dt:
        dataframe = pickle.load(f_dt)
    for row in tqdm(dataframe):
        for sdg in lst_sdg:
            if row[sdg]:
                world[sdg] += 1
        for cat in lst_cat:
            if row[cat]:
                world[cat] += 1
                if row['DST']:
                    for dt in lst_dt_shortened:
                        if row[dt]:
                            name = str(cat) + "-" + str(dt)
                            world[name] += 1
    df_nuts = pd.read_excel("data/nuts_2/full_data_on_nuts_2.xlsx", index_col=0)
    df_nuts.loc["WORLD", :] = dict(world)
    df_nuts.to_excel("data/nuts_2/full_data.xlsx")


def sort_df_full_date():
    """
    reorganize columns in full_data.xlsx and save it as full_date_sorted
    :return:
    """
    df_nuts = pd.read_excel("data/nuts_2/full_data.xlsx", index_col=0).fillna(0)
    col = lst_sdg + lst_dt + lst_cat + lst_cat_dt + ['total_nuts2', 'total_country']
    df_nuts = df_nuts[col]
    df_nuts.to_excel("data/nuts_2/full_data_sorted.xlsx")


def specialization_on_nuts():
    """
    Using full_data.xlsx, the function computes the specialization index
    for each category and for each NUTS.
    :return:
    """

    df_nuts = pd.read_excel("data/nuts_2/full_data_sorted.xlsx", index_col=0)

    nuts_index = list(df_nuts.index.to_list())
    nuts_index.remove("WORLD")
    spec_columns = lst_sdg + lst_dt + lst_cat + lst_cat_dt
    df_spec = df_nuts.copy(deep=True).loc[nuts_index, spec_columns]

    world_total_spec: dict = df_nuts.loc['WORLD', :].to_dict()
    world_total: int = world_total_spec['total_country']
    nuts_total: dict = df_nuts.loc[:, "total_nuts2"].to_dict()
    for i in nuts_index:
        for j in spec_columns:
            df_spec.at[i, j] = (df_nuts.loc[i, j] / nuts_total[i]) / \
                               (world_total_spec[j] / world_total)

    df_spec.to_excel("data/nuts_2/specialization_nuts.xlsx")


if __name__ == "__main__":
    count_world_publication()
    sort_df_full_date()
    specialization_on_nuts()
