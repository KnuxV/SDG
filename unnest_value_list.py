"""
Created by kevin-desktop, on the 04/01/2023
"""
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def formalize(dataframe) -> pd.DataFrame:
    # Lists of columns for SDG and DT
    lst_dt = ['AI', 'big_data', 'IOT', 'computing_infrastructure', 'blockchain', 'robotics', 'additive_manufacturing']
    lst_dt.sort(key=lambda v: v.lower())
    lst_sdg = list(f'SDG{i}' for i in range(1, 18))

    # scikit learn module for transforming list values into Dummies columns
    # new DF with index and lst_SDG exploded into dummy columns
    mlb = MultiLabelBinarizer()
    df_sdg = pd.DataFrame(mlb.fit_transform(dataframe['lst_SDG']), columns=mlb.classes_, index=dataframe.index).astype(
        bool)
    # new DF with index and lst_DT exploded into dummy columns
    mlb = MultiLabelBinarizer()
    df_dt = pd.DataFrame(mlb.fit_transform(dataframe['lst_DT']), columns=mlb.classes_, index=dataframe.index).astype(
        bool)

    # Merging
    res = dataframe.merge(df_sdg, left_index=True, right_index=True).merge(df_dt, left_index=True, right_index=True)

    # SDG, DT, Intersection,  Env, Eco, Soc columns
    cond_soc = res['SDG1'] | res['SDG2'] | res['SDG3'] | res['SDG4'] | res['SDG5'] | res['SDG6'] | res['SDG7'] | res[
        'SDG11'] | res['SDG16']
    res.loc[:, 'Society'] = cond_soc

    cond_eco = res['SDG8'] | res['SDG9'] | res['SDG10'] | res['SDG12'] | res['SDG17']
    res.loc[:, 'Economy'] = cond_eco

    cond_env = res['SDG13'] | res['SDG14'] | res['SDG15']
    res.loc[:, 'Environment'] = cond_env

    cond_sdg = cond_env | cond_eco | cond_soc
    res.loc[:, 'SDG'] = cond_sdg

    cond_dt = res['AI'] | res['big_data'] | res['computing_infrastructure'] | res['IOT'] | res['robotics'] | res[
        'blockchain'] | res['additive_manufacturing']
    res.loc[:, 'DT'] = cond_dt

    cond_inter = res['SDG'] & res['DT']
    res['Intersection'] = cond_inter

    dataframe_columns = [col for col in list(dataframe.columns) if col not in ['lst_DT', 'lst_SDG']]
    res_columns = dataframe_columns + ['SDG', 'DT', 'Intersection', 'Economy', 'Society',
                                       'Environment'] + lst_sdg + lst_dt

    return res.loc[:, res_columns]


if __name__ == '__main__':
    df = pd.read_pickle("data/dataframes/all_nodups.pkl")
    res = formalize(df)
    res.to_pickle("data/dataframes/full_pubs.pkl")
