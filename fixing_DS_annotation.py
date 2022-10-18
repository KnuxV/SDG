"""
quick script to redo the digital annotation which were slightly wrong, it basically uses
digitalscience_annotation
"""
import pandas as pd
from digitalscience_annotation import filter_w_digital_science
from utils import add_dst_col

if __name__ == "__main__":
    df = pd.read_pickle("data/output/all_sdg_fixed_dst.pkl")
    df_fixed_dst = add_dst_col(df)
    df_fixed_dst.to_pickle("data/output/all_sdg_fixed_dst.pkl")
