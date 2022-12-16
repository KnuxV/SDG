import re

import pandas as pd
import numpy as np
import tqdm

from utils import save_df


def filter_w_digital_science(df: pd.DataFrame,
                             keyword_path="data/keyword_digital_simplified.csv") \
        -> pd.DataFrame:
    """
    A function that will scan the dataframe and annotate rows related to AI
    Parameters
    ----------
    df : dataframe
        the dataframe that needs filtering

    keyword_path : str
        the path of the csv file containing all the keywords related to AI

    Returns nothing
    -------

    """
    df_main = df.copy()
    df_main["TXT"] = df_main["TI"] + " " + df_main["DE"] + " " + df_main["AB"]

    # Getting AI related keywords and adding them to a dic of lists
    keywords_csv = pd.read_csv(keyword_path, sep='\t', encoding="utf-8")
    dic_keywords = {}
    for col in keywords_csv.columns:
        dic_keywords[col] = keywords_csv[col].dropna(how="all").to_list()

    time_counter = 1
    for name, lst_keywords in tqdm.tqdm(dic_keywords.items()):
        print(str(time_counter) + "/7")
        # Creating a pattern of AI related keywords
        t_sb = ["\\b" + word.replace("*", "\\w*") + "\\b" for word in lst_keywords]
        pattern = '|'.join(t_sb)
        # pattern = '|'.join([f'(?i){keyword}' for keyword in lst_keywords])

        # Condition : Does the TXT contain one of the keyword?
        condition = df_main.TXT.str.contains(pattern, na=False, case=False)
        # We add a new column named after the key of the dic True if at
        # least on the keywords appears and False if not
        df_main[name] = np.where(condition, True, False)

        time_counter += 1

    df_main = df_main.drop(['TXT'], axis=1)

    return df_main


def filter_w_digital_science_v2(df: pd.DataFrame,
                                keyword_path="data/keyword_digital_simplified.csv") \
        -> pd.DataFrame:

    keywords_csv = pd.read_csv(keyword_path, sep='\t', encoding="utf-8")
    dic_reg = {}
    for col in keywords_csv.columns:
        lst_keywords = keywords_csv[col].dropna(how="all").to_list()
        t_sb = ["\\b" + word.replace("*", "\\w*") + "\\b" for word in lst_keywords]
        pattern = '|'.join(t_sb)
        dic_reg[col] = re.compile(pattern, re.I)

    idx = {name: i for i, name in enumerate(list(df), start=1)}
    for row in tqdm.tqdm(df.copy(deep=True).itertuples(index=True, name=None), total=df.shape[0]):
        # Bool for DT col
        dt = 0
        # set for set of DTs
        dt_set = set()
        dt_txt = ''
        txt = row[idx["TI"]] + "     " + row[idx["DE"]] + "    " + row[idx["AB"]]
        for col, reg in dic_reg.items():
            m = re.findall(pattern=reg, string=txt)
            if m:
                dt_txt = dt_txt + " " + ", ".join(m)
                dt_set.add(col)
                dt = 1
        df.loc[row[0], "DST"] = dt
        df.loc[row[0], "lst_DT"] = ", ".join(list(dt_set))
        df.loc[row[0], "DT_txt"] = dt_txt
    return df


if __name__ == "__main__":
    df = pd.read_pickle("data/dataframes/SDG/sdg_clean.pkl")

    df1 = filter_w_digital_science_v2(df)

    df1.to_pickle("data/dataframes/SDG/sdg_clean_w_dt.pkl")
