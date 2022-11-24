import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Loading variables
df_pop = pd.read_csv("data/countriesgdp_pop.csv")[['Country', 'pop2022']]
df_plot = pd.read_csv('data/plotly_country_names.csv', sep=',')
df_gdp = pd.read_csv('data/GDP_by_country.csv', sep=",")


def latest_gdp_col(country):
    """

    :param country:
    :return: the latest gdp published, if 2021 is not available, we look at 2020 etc...
    """
    df_gdp_temp = df_gdp.set_index('Country')
    years = [i for i in range(1960, 2022)]
    for year in reversed(years):
        if not np.isnan(df_gdp_temp.loc[country, str(year)]):
            return df_gdp_temp.loc[country, str(year)]
    return 0


df_gdp['gdp'] = df_gdp.apply(lambda x: latest_gdp_col(x['Country']), axis=1)
# Merging
df_gdp = df_gdp[['Country', 'gdp']]

df_plot = df_plot.merge(df_gdp, on="Country")
df_plot = df_plot.merge(df_pop, on="Country")


def draw_choropeth(dataframe_mention: pd.DataFrame, dataframe_plot: pd.DataFrame, scale="World", title="", option="raw",
                   folder=""):
    """

    :param dataframe_plot:
    :param dataframe_mention:
    :param scale:
    :param title:
    :param option:
    :param folder:
    :return:
    """

    def rename_countries_to_plot(country):
        dic_countries_to_rename = {"Palestine": "Palestinian Territory",
                                   "Cote d'Ivoire": "Ivory Coast",
                                   "Congo[DRC]": "Democratic Republic of the Congo",
                                   "Congo, Dem.Rep.": "Democratic Republic of the Congo",
                                   "Eswatini": "Swaziland",
                                   "Guinea Bissau": "Guinea-Bissau",
                                   "Timor-Leste": "East Timor",
                                   }
        if country in dic_countries_to_rename:
            return dic_countries_to_rename[country]
        else:
            return country

    df_mention = dataframe_mention[['Country', 'total_mention']]
    df_mention.loc[:, "Country"] = df_mention.loc[:, "Country"].apply(lambda x: rename_countries_to_plot(x))
    df_plot = dataframe_plot.merge(df_mention, on='Country')

    if option == "raw":
        z = df_plot['total_mention']
    elif option == "pop":
        z = df_plot['total_mention'] / df_plot['pop2022']
    else:
        z = 1000000000 * df_plot['total_mention'] / df_plot['gdp']

    # Drawing
    fig = go.Figure(
        data=go.Choropleth(
            locations=df_plot['Country'],
            z=z,
            text=df_plot['Country'],
            locationmode="country names",
            colorscale='Blues',
            autocolorscale=False,
        )
    )

    fig.update_layout(
        template='plotly',
        title_text='<b>' + title + '</b>',
        title_font_size=30,
        showlegend=True,
        geo=go.layout.Geo(
            scope="world",
            landcolor='lightgray',
            projection_scale=float(5.2) if scale == "EU" else 1.1,
            center=dict(lon=18, lat=52) if scale == "EU" else dict(lon=0, lat=10),
            projection_type="kavrayskiy7",
            showland=True,
            showcountries=True,
        ),
        height=1080,
        width=1980

    )
    # fig.write_image(folder)
    pio.write_image(fig, folder, format='png')


if __name__ == "__main__":
    # Loading database
    df_sdg = pd.read_pickle("data/dataframes/output/all_sdg_fixed_dst.pkl")
    df_sdg_dt = df_sdg[df_sdg['DST']]
    df_digital = pd.read_pickle("data/dataframes/digital/all_digital.pkl")
    for name, df in {"sdg": df_sdg, "sdg_dt": df_sdg_dt, "digital": df_digital}.items():
        dic_name = {"sdg": "SDG-related", "sdg_dt": "SDG-DT", "digital": "Digital"}
        for scale in ['World', 'EU']:
            df_mention = pd.read_pickle("data/dataframes/mentions/df_mention_" + name + "_" + scale.lower() + ".pkl")
            for option in ['raw', 'pop', 'gdp']:
                print(name, scale, option)
                dic_option = {'raw': 'by raw numbers',
                              'pop': 'normalised by total population',
                              'gdp': 'normalised by GDP (in billion dollars)'
                              }
                title = f"Repartition of {dic_name[name]} publications in the {scale.upper()}, \n{dic_option[option]}"
                draw_choropeth(
                    dataframe_mention=df_mention, dataframe_plot=df_plot, option=option, scale=scale, title=title,
                    folder="/media/kevin-work/My Passport/SDG_DST/img/Commission/map/"
                           + name + "_" + scale + "_" + option)
