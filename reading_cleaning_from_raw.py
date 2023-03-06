"""
Script which takes all txt files from a folder, convert them and save them in to csv file.
"""
import csv
import os

import numpy as np
import pandas as pd
import tqdm

from utils import trim_py, c1_to_cn


def concat_df(root_dir_path, sdg_number=0, dst_tag="", start_year=2010, end_year=2021):
    """

    Parameters
    ----------
    root_dir_path path
        folder path where are located all the text files used to create the concatenated db

    Returns
    -------
    dataframe
        the dataframe containing all the concatenated files

    Args:
        sdg_number (str): the number associated to the SDG
    """

    lst_of_df = []

    cols = ['PT', 'AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB', 'C1', 'RP', 'EM', 'NR', 'TC', 'Z9', 'PY', 'WC',
            'DI', 'SC', 'UT']
    # We explore the folder and its sub-folder looking for .txt to be read as
    # dataframes
    for subdir, dirs, files in os.walk(root_dir_path):
        for num, file in enumerate(files):
            # file_path = subdir + '/' + file
            file_path = os.path.join(subdir, file)

            try:
                # Error bad lines = False to skip parsing errors
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8',
                                 index_col=False, on_bad_lines="skip",
                                 quoting=csv.QUOTE_NONE)
                # we keep only a handful of useful variables, to avoid bugs,
                # we only keep the file if our 8 variables are present.
                set_columns = set(cols)
                if set_columns.issubset(set(df.columns)):
                    # making sure to only keep rows that have the proper columns
                    df = df[cols]
                else:
                    print(set_columns - set(df.columns))
                    continue

                # We need to remove NaN values
                df = df.dropna(
                    subset=['DT', 'AU', 'TI', 'LA', 'AB', 'C1', 'PY'])

                # Language = English Only
                condition_language = df.LA == "English"
                df = df[condition_language]
                df.drop('LA', axis=1, inplace=True)

                # Fixing C1 from Address to Country
                df = c1_to_cn(df)

                # Adding columns regarding SDG and DT tags
                if sdg_number != 0:
                    df['lst_SDG'] = sdg_number
                else:
                    df['lst_SDG'] = ""
                if dst_tag != "":
                    df['lst_DT'] = dst_tag
                    df['lst_SDG'] = ""
                    df['lst_Target'] = ""
                else:
                    df['lst_DT'] = ""

                df = trim_py(df, start_year=start_year, end_year=end_year)

                lst_of_df.append(df)

            except pd.errors.ParserError:
                print("Parser Error", file_path)
                continue
            except pd.errors.EmptyDataError:
                print("No columns to parse from file")
                print(file_path)
                continue

    #  Concatenation
    df_concat = pd.concat(lst_of_df, ignore_index=True)

    # Removing Duplicates
    df_concat = df_concat.drop_duplicates(['UT'], keep='last')
    df_concat = df_concat.drop_duplicates(['AB'], keep='last')

    # Categorical values
    df_concat['DT'] = df_concat['DT'].astype('category')
    df_concat['PT'] = df_concat['PT'].astype('category')
    df_concat['PY'] = df_concat['PY'].astype('category')
    df_concat['TC'] = df_concat['TC'].astype('int')

    return df_concat


def concat_sdg_df_with_targets(root, start_year=2010, end_year=2021):
    """
    This functions handles a directory of folders which contains SDG Targets.
    We concat dataframe and remove duplicated on the TARGET LEVEL
    Args:
        end_year:
        start_year:
        root:

    Returns:

    """
    lst_all = []
    for sdg in tqdm.tqdm(os.listdir(root)):
        sdgpath = os.path.join(root, sdg)

        # Target
        for target in os.listdir(sdgpath):
            lst_df = []
            targetpath = os.path.join(sdgpath, target)
            for file in os.listdir(targetpath):
                filepath = os.path.join(targetpath, file)
                if os.path.isfile(filepath):
                    df = pd.read_csv(str(filepath), sep='\t', encoding='utf-8', index_col=False,
                                     on_bad_lines="skip", quoting=csv.QUOTE_NONE)
                    cols = ['PT', 'AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB', 'C1', 'RP', 'EM', 'NR', 'TC',
                            'Z9', 'PY', 'WC',
                            'DI', 'SC', 'UT']
                    set_columns = set(cols)
                    if set_columns.issubset(set(df.columns)):
                        # making sure to only keep rows that have the proper columns
                        df = df[cols]
                    else:
                        print(set_columns - set(df.columns))
                        print(target)
                        print(file)
                        continue
                    df = df.dropna(
                        subset=['DT', 'AU', 'TI', 'LA', 'DE', 'AB', 'C1', 'PY'])
                    # Language = English Only
                    condition_language = df.LA == "English"
                    df = df[condition_language]
                    df.drop('LA', axis=1, inplace=True)

                    # Fixing C1 from Address to Country
                    df = c1_to_cn(df)

                    # Adding columns regarding SDG and DT tags
                    # Annotating SDG & Target
                    df['lst_SDG'] = str(sdg)
                    df['lst_Target'] = str(target)
                    df['lst_DT'] = ""

                    df = trim_py(df, start_year=start_year, end_year=end_year)

                    lst_df.append(df)

            #  Concatenation FOR EACH TARGET
            df_concat = pd.concat(lst_df, ignore_index=True)

            # Removing Duplicates
            df_concat = df_concat.drop_duplicates(['UT'], keep='last')
            df_concat = df_concat.drop_duplicates(['AB'], keep='last')

            # Categorical values
            df_concat['DT'] = df_concat['DT'].astype('category')
            df_concat['PT'] = df_concat['PT'].astype('category')
            df_concat['PY'] = df_concat['PY'].astype('category')
            df_concat['TC'] = df_concat['TC'].astype('int')

            lst_all.append(df_concat)

    df_final = pd.concat(lst_all)

    return df_final


def handle_duplicates(dataframe, type_dups):
    """
    Takes a dataframes full of publications, and remove duplicated while updating the corresponding columns.
    For example, if a publications appears both as AI and IOT, the column lst_DT will be a set {'AI', 'IOT'}.

    Args:
        dataframe:
        type_dups: "lst_Target", "lst_DT", "both"

    Returns:

    """
    df2_cols = list(dataframe.columns)
    df1_cols = ['UT']
    if type_dups == "lst_Target":
        df1_cols = ['UT', 'lst_Target']
        df2_cols = list(dataframe.columns)
        df2_cols.remove('lst_Target')
        df2_cols.remove('lst_SDG')

    elif type_dups == "lst_DT":
        df1_cols = ['UT', 'lst_DT']
        df2_cols.remove('lst_DT')

    elif type_dups == "both":
        df1_cols = ['UT', 'lst_DT', 'lst_Target', 'lst_SDG']
        df2_cols.remove('lst_DT')
        df2_cols.remove('lst_Target')
        df2_cols.remove('lst_SDG')

    df_to_group = dataframe[df1_cols]
    df_main = dataframe[df2_cols]

    df_main = df_main.drop_duplicates(subset="UT")
    df_to_group = df_to_group.groupby('UT', as_index=False).agg(set)
    remove_empty_from_set(df_to_group, ["lst_DT", "lst_Target", "lst_SDG"])

    df_final = df_main.merge(df_to_group, on='UT')
    return df_final


def remove_empty_from_set(dataframe, lst_column_names):
    """
    Update the column that is made of a set of items and remove empty string from it
    Args:
        dataframe:
        lst_column_names: a lst of columns name

    Returns: Nothing, but update the dataframe

    """
    for col in lst_column_names:
        for s in dataframe[col]:
            if type(s) == set:
                if "" in s:
                    s.remove("")


if __name__ == '__main__':
    folder = "data/raw_data/2021/AI"
    df_ai_2021 = concat_df(root_dir_path=folder, sdg_number=0, dst_tag='AI', start_year=2021, end_year=2021)
    df_ai_2021.drop(columns=['lst_SDG', "lst_Target"], inplace=True)
    df_ai_2021.to_csv("/media/kevin-desktop/My Passport/SDG/data/AI_2021.csv", sep="\t")




    # df_sdg = pd.read_pickle("data/dataframes/new_sdg.pkl")
    # df_dt = pd.read_pickle("data/dataframes/new_dt.pkl")
    #
    # df_concat = pd.concat([df_sdg, df_dt])
    #
    # df_all_no_dups = handle_duplicates(df_concat, type_dups="both")
    # df_all_no_dups.to_pickle("data/dataframes/all_nodups.pkl")


    # rootpath_2021 = "data/raw_data/2021/"
    # root_path_main = "data/raw_data/raw_dst/"
    #
    # lst_df = []
    #
    # for dt in tqdm.tqdm(os.listdir(rootpath_2021)):
    #     dt_path = rootpath_2021+dt
    #     df = concat_df(dt_path, sdg_number=0, dst_tag=dt)
    #     lst_df.append(df)
    #
    # for dt in tqdm.tqdm(os.listdir(root_path_main)):
    #     dt_path = root_path_main+dt
    #     df = concat_df(dt_path, sdg_number=0, dst_tag=dt)
    #     lst_df.append(df)
    #
    # df_dt = pd.concat(lst_df, ignore_index=True)
    # df_dt.to_pickle("data/dataframes/new_dt.pkl")
    # df_dt_no_dups = handle_duplicates(df_dt, type_dups='lst_DT')
    # df_dt_no_dups.to_pickle("data/dataframes/new_dt_no_dups.pkl")

    # root_sdg = "data/raw_data/raw_sdg"
    # df_sdg = concat_sdg_df_with_targets(root=root_sdg)
    # df_sdg.to_pickle("data/dataframes/new_sdg.pkl")
