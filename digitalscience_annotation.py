import pandas as pd
import numpy as np

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
    for name, lst_keywords in dic_keywords.items():
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


if __name__ == "__main__":
    df = pd.read_pickle("data/dataframes/SDG/core_sdg.pkl")
    df = filter_w_digital_science(df)
    df.to_pickle("data/dataframes/SDG/core_sdg_dt.pkl")
