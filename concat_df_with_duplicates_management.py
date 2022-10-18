"""
Script takes the 17 pickle databases and combines them into one.
It handles duplicates, keeping only unique Title/Abstract and updating the SDG columns
"""
import os

import numpy as np
import pandas as pd

import glob


def concat_sdg_duplicate(root_path: str, typ="DST") -> pd.DataFrame:
    """

    Args:
        typ: either DST or SDG
        root_path: str
            a str that is the path of the directory where all the pickle dataFrames are stored

    Returns: pd.DataFrame A dataFrame containing all the sdgs, where the categorical columns (
    SDG1 --> SDG17) are properly updated according to the duplicates. That is to say,
    if a publications was captured in SDG1, SDG5 and SDG16, only the first row will be kept but
    its SDGs columns will be updated to True False False False True False ... True False.
    """
    if typ == "SDG":
        # Storing all 17 DataFrames into a list /
        lst_df = []
        # for df_path in glob.glob(root_path + "*"):
        for path, subdirs, files in os.walk(rootdir):
            for name in files:
                df_path = os.path.join(path, name)
                print(df_path)
                # Checking
                if os.path.isfile(df_path):
                    df = pd.read_pickle(df_path)
                    lst_df.append(df)

        # getting columns from df0 & initialising
        df_tot = pd.DataFrame([], columns=list(lst_df[0].columns))

        # Looping over all df, concat the last one with the total, update dups,
        for ind, df in enumerate(lst_df):
            print(str(ind + 1) + "/17")
            df_tot = pd.concat([df_tot, df])
            df_tot['SDG' + str(ind + 1)] = np.where(df_tot['UT'].duplicated(keep=False), True,
                                                    df_tot['SDG' + str(ind + 1)])
            df_tot.drop_duplicates(subset="UT", keep="first", inplace=True)
            df_tot.drop_duplicates(subset="AB", keep="first", inplace=True)
            df_tot.drop_duplicates(subset="TI", keep="first", inplace=True)
        df_tot.reset_index(drop=True, inplace=True)

    elif typ == "DST":
        dic_df = {}
        # for df_path in glob.glob(root_path + "*"):
        for path, subdirs, files in os.walk(rootdir):
            for name in files:
                df_path = os.path.join(path, name)
                # Checking
                if os.path.isfile(df_path):
                    df = pd.read_pickle(df_path)
                    name = df_path.split('/')[-1].split(".")[0]
                    dic_df[name] = df
            # getting columns from df0 & initialising

        df_tot = pd.DataFrame([], columns=list(dic_df["AI"].columns))
        for name, df in dic_df.items():
            print(name)
            df_tot = pd.concat([df_tot, df])
            df_tot[name] = np.where(df_tot['UT'].duplicated(keep=False), True, df_tot[name])
            df_tot.drop_duplicates(subset="UT", keep="first", inplace=True)
            df_tot.drop_duplicates(subset="AB", keep="first", inplace=True)
            df_tot.drop_duplicates(subset="TI", keep="first", inplace=True)
        df_tot.reset_index(drop=True, inplace=True)

    else:
        return pd.DataFrame([])
    return df_tot


if __name__ == "__main__":
    rootdir = "data/dataframes/dst_pre_2009/"

    df_tot = concat_sdg_duplicate(root_path=rootdir, typ="DST")
    df_tot.to_pickle("data/dataframes/digital/all_digital_from_75.pkl")
