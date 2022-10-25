# Creating blank text file, copy paste queries from aurora website, converts them to be compatible in web of science
import os

lst_sdf = ["SDG-01 no poverty", "SDG-02 zero hunger", "SDG-03 good health and well-being", "SDG-04 quality education",
           "SDG-05 gender equality", "SDG-06 clean water and sanitation", "SDG-07 affordable and clean energy",
           "SDG-08 decent work and economic growth", "SDG-09 industry, innovation and infrastructure",
           "SDG-10 reduce inequalities", "SDG-11 sustainable cities and communities",
           "SDG-12 responsible consumption and production", "SDG-13 climate action", "SDG-14 life below water",
           "SDG-15 life on land", "SDG-16 peace, justice and strong institutions", "SDG-17 partnerships for the goals"]


def create_blank_files():
    for title in lst_sdf:
        tit = title.replace(" ", "_")
        with open('query/aurora/' + tit + '.txt', 'w') as f:
            pass


def convert_aurora_web_of_science():
    """
    Converts all query files in the aurora folder to a web of science compatible version stored in the
    web_of_science folder
    :return:
        nothing
    """
    # os.mkdir("query/web_of_science")
    for file in os.listdir("query/aurora"):
        with open("query/aurora/" + file, 'r', encoding='utf-8') as r, \
                open("query/web_of_science/" + file, 'w', encoding='utf-8') as w:
            filedata = r.read()
            new_data = filedata.replace('TITLE-ABS-KEY', 'TS =').replace('W/', 'NEAR/')
            w.write(new_data)


def create_empty_folder():
    for sdf in lst_sdf:
        os.mkdir("data/raw/" + sdf)



if __name__ == "__main__":
    # create_blank_files()
    convert_aurora_web_of_science()
    # create_empty_folder()
