"""
26 Sep 2022
set up a new DB, copy of intersection SDG-DT with an extra column ANN, where we give manually an annotation of the
publication.
The script is reusable, so that we can keep annotating from where we stopped last time.
"""
import glob
import os
import re
import sys

import pandas as pd
import textwrap

import termcolor

df_query = pd.read_pickle("/home/kevin-desktop/PycharmProjects/SDG/query/query.pkl")


def to_raw(string):
    return fr"{string.strip()}"


def check_for_sdg(txt):
    res = []
    for sdg, target, query, not_query in df_query.itertuples(index=False, name=None):
        if not not_query:
            try:
                m = re.search(to_raw(query), txt, re.IGNORECASE)
                if m:
                    res.append((sdg, target, m.group()))
            except:
                print("error, weird query")
        else:
            m = re.search(to_raw(query), txt, re.IGNORECASE)
            m_not = re.search(to_raw(not_query), txt, re.IGNORECASE)
            if m and not m_not:
                res.append((sdg, target, m.group()))
    return res


def main(df):
    # df = pd.read_pickle("data/dataframes/SDG/intersection_sdg_dt.pkl")
    columns = list(df.columns) + ['ANN', "ANN_DT", "ANN_SDG", "Relevance"]
    try:
        df_new = pd.read_pickle("data/dataframes/output/manual_annotation_df.pkl")
    except FileNotFoundError:
        df_new = pd.DataFrame(data=None, columns=columns)
    original_size = len(df_new)
    print(f"{original_size} publications already annotated.")
    try:
        while True:
            choice = input("New row (press any) or exit (N) ?\n")
            if choice.lower() == "n":
                df_new.to_pickle('data/dataframes/SDG/manual_annotation_df.pkl')
                print("Saving annotated dataframe...")
                print(
                    f"{len(df_new) - original_size} new publications annotated.")
                print(f"{len(df_new)} annotated publications in the dataframe.")
                break
            else:
                # Taking a random publication
                row = df.sample()
                # Retry for as long as we didn't see that publication
                while row.index[0] in df_new.index:
                    row = df.sample()

                # Convert into a series
                row_to_print = row.iloc[0]

                # Manually checking for SDG
                txt = row_to_print.AB + "    " + row_to_print.TI + "    " + row_to_print.DE
                res = check_for_sdg(txt)

                # Prepping title, Keywords and Abstract
                abstract, title, keywords = row_to_print.AB, row_to_print.TI, row_to_print.DE
                for elem in res:
                    group_to_print = elem[2]
                    abstract = abstract.replace(group_to_print, termcolor.colored(group_to_print, 'red'))
                    title = title.replace(group_to_print, termcolor.colored(group_to_print, 'red'))
                    keywords = keywords.replace(group_to_print, termcolor.colored(group_to_print, 'red'))

                print("--------")
                print(row_to_print.PY, title)
                print('')
                print(row_to_print.CN)
                lst_sdg = df.columns[13:30]
                lst_dt = df.columns[30:37]

                sdg_dt = []
                for sdg in lst_sdg:
                    if row_to_print[sdg]:
                        sdg_dt.append(sdg)
                for dt in lst_dt:
                    if row_to_print[dt]:
                        sdg_dt.append(dt)
                print(", ".join(sdg_dt))

                print()
                for elem in res:
                    print(elem[0], "==>", elem[1], "==>", elem[2])
                print()
                stuff = r"\e[1;31m This is red text \e[0m"
                print(keywords)
                print('')
                print(textwrap.fill(abstract, width=100,
                                    break_long_words=False))
                print('')

                correctly_annotated = True
                while correctly_annotated:
                    try:
                        annotate = input(
                            "How to annotate? 'ANN' 'ANN_DF' 'ANN_SDG' "
                            "'Relevance'\n")
                        row['ANN'], row['ANN_DF'], row['ANN_SDG'], row[
                            'Relevance'] = \
                            annotate.split(" ")
                        df_new = pd.concat([df_new, row])
                        correctly_annotated = False
                    except ValueError:
                        print("annotation incorrect, skipping to the next "
                              "publications")

    except KeyboardInterrupt:
        print('Saving DF')
        print(len(df_new))
        df_new.to_pickle('data/dataframes/SDG/manual_annotation_df.pkl')


if __name__ == '__main__':
    dataframe_path = sys.argv[1]
    dataframe = pd.read_pickle(dataframe_path)
    main(dataframe)
