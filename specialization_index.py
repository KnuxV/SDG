"""
Specialization index
"""
import pandas as pd
from collections import Counter, defaultdict

# Global variables
from pretty_html_table import build_table

df = pd.read_pickle("data/output/all_sdg_fixed_dst.pkl")
df_digital = pd.read_pickle("data/dataframes/digital/all_digital.pkl")
df_eu_countries = pd.read_excel("data/countries_eu.xlsx", sheet_name=0, index_col=0)
df_continent = pd.read_excel("data/continents.xls", sheet_name=0)

df_country_w_continent = pd.read_excel("data/countries_w_continent.xlsx", sheet_name=0)
dic_country_continent = dict(zip(df_country_w_continent.Country, df_country_w_continent.Region))

# Filtered database
df_eu = df[df["EU"]]
df_dst = df_digital
df_eu_dst = df_eu[df_eu['DST']]

# list EU countries
lst_eu = df_eu_countries.Country.to_list()
# list continents
lst_continent = df_continent.Continent.to_list()
# list SDG
lst_sdg = ["SDG" + str(i) for i in range(1, 18)]
# list Categories
lst_cat = ["Environment", "Society", "Economy"]
# list DST
lst_dst = list(df.columns)[30:37]
dic_filter = {"eu": lst_eu, "continent": lst_continent, "sdg": lst_sdg, "cat": lst_cat, "dst": lst_dst}


def count_publications(dataframe: pd.DataFrame, filter1: str, filter2: str, name: str, save=False) -> pd.DataFrame:
    """
    Iterates though the dataframe and count how many publications are part of each filter
    :param save:
    :param name:
    :param dataframe:
    :param filter1: choose from [eu, continent, sdg, dst]
    :param filter2: choose from [sdg, dst, cat]
    :return: a dataframe with count f
    """
    # Initialising a dictionary
    # d = {elem: {elem: Counter() for elem in dic_filter[filter2]} for elem in dic_filter[filter1]}
    d = {elem_x: defaultdict(lambda: 0) for elem_x in dic_filter[filter1]+['total_x']}
    if filter1 in ["eu", 'continent']:
        for ind, row in dataframe.iterrows():
            if filter1 == "eu":
                lst_actors_in_row = row.CN.split(", ")
            else:
                lst_actors_in_row = [dic_country_continent[actor] for actor in row.CN.split(", ")]
            for actor in lst_actors_in_row:
                if actor in d.keys():
                    d[actor]["total_y"] += 1
                    d['total_x']["total_y"] += 1
                    for elem in dic_filter[filter2]:
                        if row[elem]:
                            d[actor][elem] += 1
                            d["total_x"][elem] += 1

    elif filter1 in ["sdg", "cat", "dst"]:
        for ind, row in dataframe.iterrows():
            for elem_x in dic_filter[filter1]:
                if row[elem_x]:
                    d[elem_x]["total_y"] += 1
                    d['total_x']["total_y"] += 1
                for elem_y in dic_filter[filter2]:
                    if row[elem_y]:
                        d[elem_x][elem_y] += 1
                        ["total_x"][elem_y] += 1
    else:
        print(f"{filter1} is not a valid filter")

    df_tableau = pd.DataFrame.from_dict(d, orient='index')
    # sorting columns
    df_tableau1 = df_tableau.reindex(columns=dic_filter[filter2] + ['total_y']).sort_index()
    # Sorting index
    idx = sorted(dic_filter[filter1]) + ["total_x"]
    df_tableau2 = df_tableau1.loc[idx]

    # Replacing NAN by 0
    df_tableau3 = df_tableau2.fillna(0)

    # Computing specialization
    dic_spe = {elem_x: {elem_y: 0 for elem_y in dic_filter[filter2]} for elem_x in dic_filter[filter1]}

    for elem_x in dic_filter[filter1]:
        for elem_y in dic_filter[filter2]:
            specialization_value = (df_tableau3.loc[elem_x, elem_y] / df_tableau3.loc[elem_x, 'total_y']) / (
                    df_tableau3.loc['total_x', elem_y] / df_tableau3.loc["total_x", 'total_y'])
            dic_spe[elem_x][elem_y] = round(specialization_value, 2)

    df_spe = pd.DataFrame.from_dict(dic_spe, orient='index')
    # sorting columns
    df_spe = df_spe.reindex(columns=dic_filter[filter2]).sort_index()
    # Sorting index
    idx = sorted(dic_filter[filter1])
    df_spe = df_spe.loc[idx]

    html_table_blue_light = build_table(df_spe, 'blue_dark', index=True, border_bottom_color="dark blue")

    # Save to html file
    if save:
        with open('/home/kevin/PycharmProjects/SDG_DST/img/Commission/Specialization/' + str(name) + '.html', 'w') as f:
            f.write(html_table_blue_light)
    return df_spe


if __name__ == "__main__":
    # count_publications(df_eu, filter1="eu", filter2="sdg", name="test", save=True)
    # count_publications(df_eu_dst, filter1="eu", filter2="dst", name="eu_dst", save=True)
    count_publications(df_dst, filter1="eu", filter2="dst", name="dst", save=True)
    # count_publications(df, filter1="continent", filter2="sdg", name="continent_sdg", save=True)


