"""

"""
import pandas as pd


def drop_dups_on_publication(df):
    df_dups = df.copy()
    df_dups.drop_duplicates(subset="AB", keep="first", inplace=True)
    df_dups.drop_duplicates(subset="TI", keep="first", inplace=True)
    df_dups.drop_duplicates(subset="UT", keep="first", inplace=True)
    return df_dups


if __name__ == "__main__":
    df = pd.read_pickle("data/output/WoS_SDG_updated_new.pkl")
    df_dups = drop_dups_on_publication(df)
    df_dups.to_pickle("data/output/WoS_SDG_updated_new.pkl")
    df_dups.to_csv("data/output/WoS_SDG_updated_new.csv", sep="\t", encoding="utf-8",
                   index=False, header=True)

    df = pd.read_pickle("data/output/clean/all_digital.pkl")
    df_dups = drop_dups_on_publication(df)
    df_dups.to_pickle("data/output/clean/all_digital.pkl")
    df_dups.to_csv("data/output/clean/all_digital.csv", sep="\t", encoding="utf-8",
                   index=False, header=True)

    df = pd.read_pickle("data/output/WoS_SDG_DST.pkl")
    df_dups = drop_dups_on_publication(df)
    df_dups.to_pickle("data/output/WoS_SDG_DST.pkl")
    df_dups.to_csv("data/output/WoS_SDG_DST.csv", sep="\t", encoding="utf-8",
                   index=False, header=True)
