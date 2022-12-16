"""
Functions
"""
import os
from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd
import re
from functools import reduce
from operator import or_, and_
import swifter

reg = re.compile(r"(\[(?P<authors>[^\[\]]+)])? (?P<country>[^\[\];]+);?")

path_country = "/home/kevin-desktop/PycharmProjects/SDG/data/countries_full.xls"
df_country = pd.read_excel(path_country)
# Special rules for different spelling in WOS
dic_country = {'Peoples R China': "China",
               'England': 'United Kingdom',
               'Scotland': 'United Kingdom',
               'Wales': 'United Kingdom',
               'Northen Ireland': 'United Kingdom',
               'Northern Ireland': 'United Kingdom',
               'North Ireland': 'United Kingdom',
               'U Arab Emirates': 'United Arab Emirates',
               'Bosnia & Herceg': 'Bosnia and Herzegovina',
               'Bosnia and Herz': 'Bosnia and Herzegovina',
               'Trinidad Tobago': 'Trinidad and Tobago',
               'Trinidad and To': 'Trinidad and Tobago',
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
               'St Lucia': 'Saint Lucia',
               'Vatican': 'Vatican City',
               'Svalbard': 'Norway',
               'Falkland Island': 'Falkland Islands',
               'British Virgin Isl': 'British Virgin Islands',
               'Sao Tome & Prin': 'São Tomé and Príncipe',
               'Equat Guinea': 'Equatorial Guinea',
               'Bonaire': 'Netherlands Antilles',
               'Ascension Isl': 'Saint Helena',
               'Tristan da Cunh': 'Saint Helena',
               'Brit Ind Ocean': 'British Indian Ocean Territory',
               'Peoples R Chin': 'China',
               'North Sudan': 'Sudan',
               'St Martin': 'Sint Maarten',
               }


def trim_py(df, start_year, end_year, inclusive="both"):
    """
    Confines a pandas dataframe from by a lower year boundary
    and an upper year boundary.
    Parameters
    ----------
    df : dataframe
        the dataframe in which we need to restrict the year (PY columns)
    start_year : int
    end_year : int
    inclusive : str
        Either both, left, right or neither

    Returns
    -------
    def_new
        a datagrame where the PY column is restricted between the two dates

    """
    df_new = df
    df_new.PY = df_new.PY.fillna(0)
    df_new.PY = pd.to_numeric(df_new.PY, downcast="integer", errors="coerce")

    condition_year = df_new.PY.between(start_year, end_year,
                                       inclusive=inclusive)
    def_new = df_new[condition_year]
    return def_new


def add_country_col(df) -> pd.DataFrame:
    """
    OUTDATED voir C1_to_CN function
    Parameters
    ----------
    df

    Returns
    -------
    df_new
        Where the CN (country) column is created based on the C1 (=adress column),
         this is a list of the countries of universities having publinshed the paper.
        Country names respect the proper terminology to be displayed by plotly.
        Therefore, modification must be made.
    """
    # df_country = pd.read_csv("data/countries1.csv", encoding="utf-8", sep="\t")
    df_country = pd.read_csv("data/countries_full.csv", encoding='utf-8', index_col=0)
    df_new = df.copy()
    # Given the C1 structure, we extract the last group of words of each address.
    # Two possibilities [Names] Address ; [Names] Address or if no Names just the address.
    reg = re.compile(r"(\[([^\[\]]+)])? (?P<adress>[^\[\];]+);?")
    # To respect plotly country names
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

    df_new["CN"] = df_new.C1.apply(
        lambda x: [match.group("country").split(", ")[-1] for match in
                   re.finditer(reg, x)] if type(
            x) == str else np.NaN)
    # We get rid of country name for the US (example :  MA 02139 USA ==> United States)
    df_new.CN = df_new.CN.apply(
        lambda x: [country if "USA" not in country else "United States" for
                   country in x] if type(
            x) == list else np.NaN)
    # countries in the dic_country see their name modified
    df_new.CN = df_new.CN.apply(
        lambda x: [dic_country[country] if country in dic_country else country
                   for country in x] if type(
            x) == list else np.NaN)
    # removing everything that is not a country
    df_new.CN = df_new.CN.apply(lambda x: [country for country in x if
                                           country in df_country.name.values])

    # From list of countries to string of countries
    df_new.CN = df_new.CN.apply(lambda x: ', '.join(str(elem) for elem in x))

    return df_new


def create_cn_string(txt):
    # Regex with two groups. Authors group is optional as some C1 do not have any authors but the
    # university address.

    # Initializing a dic / we use a dic of set {C1 : set(authors), C2: set(authors)} in order to
    # remove a double affiliation in the same country
    dic_affiliations = defaultdict(set)

    # finditer finds all iteration of our regex in the given text
    finditer = re.finditer(reg, txt)
    if finditer:
        for elem in finditer:
            # Check for matches
            match_authors = elem.group('authors')
            match_country = elem.group("country")
            if match_authors:
                lst_authors = elem.group('authors').split(";")
            else:
                # Case where we have the university address without authors
                lst_authors = ["no author"]
            country = match_country.split(", ")[-1]
            # USA case that needs simplifying
            if "USA" in country:
                dic_affiliations["United States"] |= set(lst_authors)
            elif country in dic_country:
                dic_affiliations[dic_country[country]] |= set(lst_authors)
            else:
                if country in df_country['Country'].values:
                    dic_affiliations[country] |= set(lst_authors)

    # Prepping to return a string C1, C1, C1  len(set(authors)) times, C2 etc...
    return_lst = []
    for contr, set_authors in dic_affiliations.items():
        [return_lst.append(contr) for _ in range(len(set_authors))]
    return_string = ", ".join(return_lst)
    return return_string


def c1_to_cn(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    add or modify the CN column using the C1 column (address of authors). CN column a string made
    of all countries having contributed to the publications.
    Args:
        dataframe (pd.DataFrame): input dataframe

    Returns:
        pd.DataFrame with a new CN column

    """

    dataframe['CN'] = dataframe['C1'].apply(create_cn_string)

    return dataframe


def add_sdg_cols(df: pd.DataFrame, sdg_number: int) -> pd.DataFrame:
    """
    OLD method, create 17 columns with only one True for the SDG the pub is from
    Args:
        df (dataframe): a pandas dataframe
        sdg_number (int): the number corresponding to the sdg

    Returns:
        dataframe: the dataframe with a new column containing a list of all sdgs related to the publication

    """
    for i in range(1, 18):
        col = 'SDG' + str(i)
        if i == sdg_number:
            df[col] = True
        else:
            df[col] = False
        df[col] = df[col].astype('category')
    return df


def add_dst_cols(df: pd.DataFrame, dst_tag: str) -> pd.DataFrame:
    """

    Args:
        df (dataframe): a pandas dataframe
        dst_tag (str): the tag of corresponding dst

    Returns:
        dataframe: the dataframe with a new column containing a list of all dsts related to the publication

    """
    lst_dst = ['AI',
               'big_data',
               'IOT',
               'computing_infrastructure',
               'blockchain',
               'robotics',
               'additive_manufacturing']

    for dst in lst_dst:
        if dst == dst_tag:
            df[dst] = True
        else:
            df[dst] = False
        df[dst] = df[dst].astype('category')

    return df


def add_dst_col(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe["DST"] = dataframe["AI"] | dataframe["big_data"] | dataframe["IOT"] | \
                       dataframe["computing_infrastructure"] | dataframe["blockchain"] | \
                       dataframe["robotics"] | dataframe["additive_manufacturing"]
    return dataframe


def save_df(df, path, typ="pickle", header=True, index=False, sep="\t",
            columns=None):
    """

    Parameters
    ----------
    columns
    typ : str
        picke or csv
    df : dataframe
        that needs to be saved
    path : a path
        where to save it

    header : header option from pandas
        don't modify
    index : index option from pandas
        don't modify
    sep : sep option from pandas
        don't modify

    Returns
    -------
    nothing
        save the dataframe as a csv or pickle at the chosen location.
    """
    if columns is None:
        columns = ['PT', 'AU', 'TI', 'LA', 'DE', 'AB', 'C1', 'PY', 'CN']
    if typ == "csv":
        df.to_csv(path, columns=columns, header=header, index=index, sep=sep)
    else:
        df.to_pickle(path)


def add_type_sdg_cat(df: pd.DataFrame) -> pd.DataFrame:
    """
    add three columns Society / Economy / Environment depending to the df
    according to SDGs

    Args:
        df:

    Returns:

    """
    df['Society'] = df.apply(
        lambda x: x['SDG1'] | x['SDG2'] | x['SDG3'] | x['SDG4'] | x['SDG5'] | x[
            'SDG6'] | x['SDG7'] | x['SDG11'] | x['SDG16'], axis=1)
    df['Economy'] = df.apply(
        lambda x: x['SDG8'] | x['SDG9'] | x['SDG10'] | x['SDG12'] | x['SDG17'],
        axis=1)
    df['Environment'] = df.apply(
        lambda x: x['SDG13'] | x['SDG14'] | x['SDG15'], axis=1)
    df['Environment'] = df['Environment'].astype(bool)
    df['Economy'] = df['Economy'].astype(bool)
    df['Society'] = df['Society'].astype(bool)
    return df


def filter_w_sdg(dataframe: pd.DataFrame, lst_col: List[str], how="inclusive") -> pd.DataFrame:
    """
    filter the dataframe by only keeping publications relations to SDG that are in the lst_sdg
    Args:
        lst_col: a list of str, which are the boolean columns of the dataframe. We filter the
        dataframe only keeping said columns when they are equal to True.
        how: if inclusive or OR, filter with "cond1 OR cond2 OR cond3" that is a publication needs
        to be part of at list one of the sdg selected
        if exclusive or AND, a publication needs to be part of all sdg in lst_sdg
        dataframe:

    Returns:

    """

    def apply_filter(dataframe, lst_filter, how):
        if how in ['inclusive', 'or', 'OR']:
            return dataframe[reduce(or_, lst_filter)]
        if how in ['exclusive', 'and', 'AND']:
            return dataframe[reduce(and_, lst_filter)]
        else:
            print("wrong filter")
            return None

    for col in lst_col:
        if col not in dataframe.columns:
            print(col, " not in the dataframe columns")
            print("columns are:", ", ".join(list(dataframe.columns)))
            print(f"removing string {col} and continuing")
            lst_col.remove(col)
    lst_filter = [dataframe[col] for col in lst_col]
    filtered_df = apply_filter(dataframe=dataframe, lst_filter=lst_filter, how=how)
    return filtered_df


def filter_for_eu_countries(dataframe: pd.DataFrame, extended=True, how="filter") -> \
        pd.DataFrame:
    """

    Args:
        how: either filter or add. If "filter", the function will return a new database with only the
        publications related to the EU. If "add", the function adds a new boolean column "EU"
        which will be True if the publication is related to the EU
        country.
        extended: if False, only keep EU27, else we add Iceland Liechtenstein, Norway, Switzerland
        and UK
        dataframe:

    Returns:

    """
    lst_eu = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
              "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
              "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland",
              "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"]
    lst_extended_eu = lst_eu + ["Iceland", "Liechtenstein", "Norway", "Switzerland",
                                "United Kingdom"]
    if extended:
        lst_country = lst_extended_eu
    else:
        lst_country = lst_eu

    def eu_countries_in_cn_col(cn: List) -> bool:
        """
        Args:
            cn:

        Returns:
            True if there is at least one European country in the CN list
        """
        return any(country in cn for country in lst_country)

    mask = dataframe['CN'].apply(eu_countries_in_cn_col)
    if "EU" in dataframe.columns:
        dataframe = dataframe.drop(columns=["EU"])

    dataframe.insert(loc=len(dataframe.columns), column="EU", value=mask)
    if how == "add":
        return dataframe
    elif how == "filter":
        return dataframe[dataframe["EU"]].drop(columns=["EU"])
    else:
        return pd.Dataframe()


if __name__ == "__main__":
    """
    df_all_dst = pd.read_pickle("data/output/all_sdg.pkl")
    df_sdg_dst = pd.read_pickle("data/output/sdg_dst.pkl")
    df_all_digital_eu = pd.read_pickle("data/output/all_digital_europe.pkl")

    df_all_dst.to_csv("data/output/all_sdg.csv",header=True, index=False, sep="\t")
    df_sdg_dst.to_csv("data/output/sdg_dst.csv", header=True, index=False, sep="\t")
    df_all_digital_eu.to_csv("data/output/all_digital_europe.csv", header=True, index=False, sep="\t")
    """
    pass

