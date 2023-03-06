"""
Created by kevin-desktop, on the 13/02/2023
"""
import os

import pandas as pd
import numpy as np
import tqdm

# Load auths
df_auth = pd.read_pickle("data/dataframes/authors_full.pkl")


def splitting_df(dataframe: pd.DataFrame, nb_partition: int, folder_path: str):
    """
    Takes a dataframe and splits it into nb partitions and save it to pickle.
    Args:
        dataframe: pd.DataFrame
        nb_partition (int): the number of databases that will be created
        folder_path (str) : the folder where dataframes will be saved

    Returns: nothing

    """
    lst_df = np.array_split(dataframe, nb_partition)
    for i, df in tqdm.tqdm(enumerate(lst_df)):
        df.to_pickle(f"{folder_path}/{i}.pkl")


def join_dfs(folder_path: str, exit_path: str):
    """
    Takes a folder of dataframes with the sames columns and concatenate them together, write a new datafarme out of them
    Args:
        folder_path:
        exit_path:

    Returns: nothing

    """
    lst_df = []
    for df_path in os.listdir(folder_path):
        full_path = os.path.join(folder_path, df_path)
        df = pd.read_pickle(full_path)
        lst_df.append(df)

    df_all = pd.concat(lst_df)
    df_all.to_pickle(exit_path)


if __name__ == '__main__':
    pass
    # splitting_df(df_auth, 30, 'data/dataframes/authors')
    # join_dfs("data/dataframes/authors/authors_w_cn_title", "data/dataframes/authors_w_cn_ti.pkl")
