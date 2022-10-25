"""
Modify Excel file aurora_wos_v2.xlsx adding the total number of pubs for each target
"""

import pandas as pd

from autoclicker_v3 import set_driver, login_wos, enter_query, get_total_pub, \
    set_download_folder_firefox, wait_for_elem

lst_df = []

for i in range(1, 18):
    path = "query"
    options = set_download_folder_firefox(path)
    driver = set_driver(options)
    login_wos(driver=driver)

    sdg_name = "SDG" + str(i)
    df_query = pd.read_excel("query/aurora_wos_v2.xlsx",
                             sheet_name=sdg_name, index_col=0)

    series_query = pd.Series(
        df_query.set_index('Target').dropna().loc[:, 'Query_wos'])
    dic = series_query.to_dict()

    for target, query in dic.items():
        enter_query(driver, query)
        total_pub = get_total_pub(driver)
        print(target, total_pub)
        df_query.loc[df_query['Target'] == target, "total_pub"] = total_pub

        driver.back()
        wait_for_elem(driver, elem_path='//*[@id="advancedSearchInputArea"]',
                      how="xpath")
    driver.close()
    lst_df.append(df_query)

with pd.ExcelWriter("query/aurora_wos_v2_copy.xlsx") as writer:
    for num, df in enumerate(lst_df):
        df.to_excel(writer, sheet_name=f'SDG{num + 1}')
