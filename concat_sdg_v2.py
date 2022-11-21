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
        lst_df = []
        sdgpath = os.path.join(root, sdg)
        # Target
        for target in os.listdir(sdgpath):
            targetpath = os.path.join(sdgpath, target)
            for file in os.listdir(targetpath):
                filepath = os.path.join(targetpath, file)
                if os.path.isfile(filepath):
                    df = pd.read_csv(filepath, sep='\t', encoding='utf-8', index_col=False, on_bad_lines="skip",
                                     quoting=csv.QUOTE_NONE)

                    df = df.dropna(
                        subset=['DT', 'AU', 'TI', 'LA', 'DE', 'AB', 'C1', 'PY'])
                    df = c1_to_cn(df)
                    df = trim_py(df, 2010, 2022)

                    # Annotating SDG & Target
                    df['SDG'] = str(sdg)
                    df['Target'] = str(target)

                    lst_df.append(df)

        df_concat = pd.concat(lst_df)
        df_concat.to_pickle('data/dataframes/sdg_df/' + sdg)


def concat_from_sdg_to_all():
    pass


def handle_dups(df):
    # Columns, we split the DF into two df, one with most of the info and the second one with UT, SDG, Target

    df1_cols = ['UT', 'Target']
    df2_cols = list(df.columns)
    df2_cols.remove('Target')
    df2_cols.remove('SDG')

    df_to_group = df[df1_cols]
    df_main = df[df2_cols]

    df_main.drop_duplicates(subset="UT", inplace=True)
    df_to_group = df_to_group.groupby('UT', as_index=False).agg(set)

    df_final = df_main.merge(df_to_group, on='UT')
    return df_final


if __name__ == '__main__':
    # root = "data/raw/raw_sdg"
    # save_folder = 'data/dataframes/sdg_df/'
    # save_name = 'new_sdg_concat_with_dups.pkl'
    # concat_all_pubs(root=root, save_folder=save_folder, save_name=save_name)
    root = "data/dataframes/sdg_df/"

    for sdg in tqdm.tqdm(os.listdir(root)):
        print(sdg)
        p = os.path.join(root, sdg)
        df = pd.read_pickle(p)
        df1 = handle_dups(df)
        df1.to_pickle("data/dataframes/sdg_no_dups/" + sdg + ".pkl")
