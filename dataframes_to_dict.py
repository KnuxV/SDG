"""
21 Sep 2022
Quick script which takes our main dataframe and converts them to
json ('records')
"""
import pickle

import pandas as pd
import json

from tqdm import tqdm

dic_dataframes = {'sdg': pd.read_pickle('data/dataframes/SDG/all_sdg_fixed_dst.pkl'),
                  'sdg_long': pd.read_csv('data/dataframes/SDG/SDG_georef_more10_moreNUTS.csv', sep=','),
                  'dt': pd.read_pickle('data/dataframes/digital/all_digital.pkl'),
                  'dt_long': pd.read_csv('data/dataframes/digital/digital_georef_more10_moreNUTS.csv', sep=',')}


def main():
    for df_name, df in tqdm(dic_dataframes.items()):
        result = df.to_dict(orient="records")

        with open(f'data/json/{df_name}.pickle', 'wb') as handle:
            pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()
