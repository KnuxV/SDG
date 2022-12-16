"""
Take raw .txt WOS file into a database with every publication annotated
"""
import csv
import glob

import pandas as pd
import os
import tqdm

from utils import c1_to_cn, trim_py


def concat_all_pubs(root, save_folder, save_name):
    # SDG
    # for sdg in tqdm.tqdm(os.listdir(root)):
    for sdg in tqdm.tqdm(os.listdir(root)):
        print(sdg)
        lst_df = []
        sdgpath = os.path.join(root, sdg)

        # Target
        for target in os.listdir(sdgpath):
            targetpath = os.path.join(sdgpath, target)
            for file in os.listdir(targetpath):
                filepath = os.path.join(targetpath, file)
                if os.path.isfile(filepath):
                    df = pd.read_csv(str(filepath), sep='\t', encoding='utf-8', index_col=False,
                                     on_bad_lines="skip", quoting=csv.QUOTE_NONE)

                    df = df.dropna(
                        subset=['DT', 'AU', 'TI', 'LA', 'DE', 'AB', 'C1', 'PY'])
                    df = c1_to_cn(df)
                    df = trim_py(df, 2010, 2022)

                    # Annotating SDG & Target
                    df['SDG'] = str(sdg)
                    df['Target'] = str(target)

                    lst_df.append(df)

        df_concat = pd.concat(lst_df)
        df_concat.to_pickle('data/dataframes/SDG/sdg_df/' + sdg + '.pkl')


def concat_from_sdg_to_all(folder, save_path):
    """
    Takes all pickle dataframe from a folder and concatenate them
    Args:
        folder:

    Returns:

    """
    lst_df = []
    for sdg_pkl in os.listdir(folder):
        sdg_path = os.path.join(folder, sdg_pkl)
        df = pd.read_pickle(sdg_path)
        lst_df.append(df)

    df_final = pd.concat(lst_df)

    df_final.to_pickle(save_path)


def handle_dups(dataframe):
    # Columns, we split the DF into two df, one with most of the info and the second one with UT, SDG, Target

    df1_cols = ['UT', 'Target']
    df2_cols = list(dataframe.columns)
    df2_cols.remove('Target')
    df2_cols.remove('SDG')

    df_to_group = dataframe[df1_cols]
    df_main = dataframe[df2_cols]

    df_main = df_main.drop_duplicates(subset="UT")
    df_to_group = df_to_group.groupby('UT', as_index=False).agg(set)

    df_final = df_main.merge(df_to_group, on='UT')
    return df_final


def create_sdg_col(dataframe):
    """

    Args:
        dataframe:

    Returns:
        A new dataframe with a new row SDG made from the Target column, they are both set.
    """

    def from_target_to_sdg(set_target):
        set_sdg = set()
        if type(set_target) == str:
            set_target = eval(set_target)
        for target in set_target:
            if type(target) == float:
                target = str(target)
            sdg = int(target.split('.')[0])
            set_sdg.add(sdg)
        return set_sdg

    dataframe['SDG'] = dataframe['Target'].apply(from_target_to_sdg)
    return dataframe


if __name__ == '__main__':

    # root = "data/raw_data/raw_sdg/"
    # save_folder = 'data/dataframes/SDG/sdg_df'
    # save_name = 'new_sdg_concat_with_dups.pkl'
    # concat_all_pubs(root=root, save_folder=save_folder, save_name=save_name)

    # root = 'data/dataframes/SDG/sdg_df'
    # for sdg in tqdm.tqdm(os.listdir(root)):
    #     p = os.path.join(root, sdg)
    #     df = pd.read_pickle(p)
    #     df1 = handle_dups(df)
    #     df1.to_pickle("data/dataframes/SDG/sdg_no_dups/" + sdg + ".pkl")

    lst_df = []
    root = "data/dataframes/SDG/sdg_df/"
    for sdg_pkl in tqdm.tqdm(os.listdir(root)):
        sdg_path = os.path.join(root, sdg_pkl)
        df = pd.read_pickle(sdg_path)
        lst_df.append(df)
    df_final = pd.concat(lst_df)

    df_final = handle_dups(df_final)
    df_final = create_sdg_col(df_final)
    df_final.to_pickle("data/dataframes/SDG/all_sdg_no_dups.pkl")
