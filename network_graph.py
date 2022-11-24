"""
functions to create network graph on maps with plotly depending on a dataframe.
3 options: World, Europe, or Continent
"""
import os
from typing import Tuple, Any

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from itertools import combinations
from collections import Counter

# LOADING STUFF
from numpy import nan, NaN

df_country = pd.read_excel("/media/kevin-work/My Passport/SDG_DST/data/countries_full.xls", sheet_name=0)
df_country_eu = pd.read_excel("/media/kevin-work/My Passport/SDG_DST/data/countries_eu.xlsx", sheet_name=0)
df_country_w_continent = pd.read_excel("/media/kevin-work/My Passport/SDG_DST/data/countries_w_continent.xlsx", sheet_name=0)
df_continent = pd.read_excel("/media/kevin-work/My Passport/SDG_DST/data/continents.xls", sheet_name=0)

# dic of pair Country: Continent
# df_country_w_continent = df_country.dropna(subset=['Region'])
dic_country_continent = dict(zip(df_country_w_continent.Country, df_country_w_continent.Region))
list_eu_countries = df_country_eu.Country.tolist()


def unique_actors(dataframe, map_filter='World') -> pd.DataFrame:
    """
    this function creates a list of unique actors present in the CN column of
    the dataframe. CN column is a made a str such as 'France, United States'
    Args:
        dataframe (pd.Dataframe): input dataframe
        map_filter (str): choose between World, Europe or Continent which
        affects the displays

    Returns:
        list: a list with all actors present in the df (only European countries)
        if map_filter=Europe, only continents if map_filter=Continent.
    """
    return_set = set()
    # df_lst_country = pd.read_csv("data/country_continent.csv", index_col=0)

    if map_filter == 'World':
        for ind, row in dataframe.iterrows():
            if row.CN.split(", "):
                return_set |= set(row.CN.split(", "))

    elif map_filter == 'Europe' or 'EU':
        for ind, row in dataframe.iterrows():
            countries = row.CN.split(", ")
            countries_from_eu = [elem for elem in countries if elem in list_eu_countries]
            return_set |= set(countries_from_eu)

    elif map_filter == 'Continent':
        for ind, row in dataframe.iterrows():
            countries = row.CN.split(", ")
            try:
                lst_countries_as_continent = [dic_country_continent[elem] for elem in countries]
                return_set |= set(lst_countries_as_continent)
            except KeyError:
                for elem in countries:
                    if elem not in dic_country_continent.keys():
                        print(elem)

    if "" in return_set:
        return_set.remove("")
    if return_set:
        return_lst = list(return_set)
    else:
        print("return list is empty")
        return pd.DataFrame(data=None)

    if map_filter in ["World", "Europe", "EU"]:
        df_unique_actors = pd.DataFrame(return_lst, columns=["Country"])
        df_unique_actors.sort_values(by="Country", inplace=True)
    elif map_filter == "Continent":
        df_unique_actors = pd.DataFrame(return_lst, columns=["Continent"])
        df_unique_actors.sort_values(by="Continent", inplace=True)
    else:
        df_unique_actors = pd.DataFrame(data=None, columns=["Country"])

    return df_unique_actors.reset_index(drop=True)


def give_lat_long(country: str, map_filter="World") -> tuple:
    """
    Args:
        country (str): name of the country

    Returns:
        tuple: a tuple made of (latitude, longitude) of a given country
        according to a csv file
        :param map_filter:
    """
    # df_lst_country = pd.read_csv(country_csv_path, sep=sep)
    quer = df_country_w_continent.query('Country == "%s"' % country)[['latitude', 'longitude']]

    if map_filter == "Continent":
        quer = df_continent.query('Continent == "%s"' % country)[['latitude', 'longitude']]
    return tuple(quer.values[0])


def actors_mention(dataframe: pd.DataFrame, map_filter="World",
                   max_num_actors="max") -> pd.DataFrame:
    """

    Args:
        max_num_actors:
        dataframe (pd.Dataframe): Dataframe with a CN column
        map_filter (str): World, Europe or Continent

    Returns:
        pd.Dataframe: a dataframe with columns (Country, total_mention, latitude, longitude,
        continent, percentage (= mention / sum(mentions))
    """
    # getting the list of unique countries/continent and sorting them
    df_mentions = unique_actors(dataframe, map_filter=map_filter)
    if df_mentions is None:
        return pd.DataFrame(data=None)
    if max_num_actors == "max":
        max_num_actors = len(df_mentions)
    else:
        try:
            max_num_actors = int(max_num_actors)
        except ValueError:
            max_num_actors = len(df_mentions)

    # Computing total_mention per actor
    total_mention = Counter()
    for ind, row in dataframe.iterrows():
        if map_filter in ['World', 'Europe', 'EU']:
            lst_actor_in_row = sorted(row.CN.split(", "))
            if "" in lst_actor_in_row:
                lst_actor_in_row.remove("")
            if lst_actor_in_row:
                for mention in lst_actor_in_row:
                    total_mention[mention] += 1

        elif map_filter == 'Continent':
            # For continent, we convert the country to its continent using the dic
            lst_actor_in_row = sorted(row.CN.split(", "))
            if lst_actor_in_row:
                for mention in lst_actor_in_row:
                    if mention != "":
                        total_mention[dic_country_continent[mention]] += 1

    if map_filter in ['World', 'Europe', 'EU']:
        df_mentions['total_mention'] = \
            df_mentions['Country'].apply(lambda x: total_mention[x])
        df_mentions = df_mentions.merge(df_country_w_continent, left_on="Country", right_on='Country')
    if map_filter == "Continent":
        df_mentions['total_mention'] = df_mentions['Continent'].apply(lambda x: total_mention[x])
        df_mentions = df_mentions.merge(df_continent, left_on="Continent", right_on='Continent')
    # df_mentions.drop(columns=['name', 'country'], axis=1, inplace=True)
    max_total = df_mentions['total_mention'].sum()
    df_mentions['percentage'] = df_mentions['total_mention'].apply(
        lambda x: round(100 * float(x) / max_total, 2))
    df_mentions['total_mention'] = pd.to_numeric(df_mentions['total_mention'])
    return df_mentions.nlargest(max_num_actors, columns=['total_mention']).reset_index(drop=True)


def actors_edge(dataframe: pd.DataFrame, dataframe_mentions: pd.DataFrame, map_filter="World", ) -> \
        Tuple[
            pd.DataFrame, int]:
    """

    Args:
        dataframe_mentions:
        dataframe:
        map_filter: World, Europe or Continent

    Returns: a df with the following columns: edge (number of collab between actors),
    c1,c2 (the two actors), latitude_c1, longitude_c1, latitude_c2, longitude_c2
    (their localisations)
    """
    total_edge = Counter()
    for ind, row in dataframe.iterrows():
        if map_filter in ['World', 'Europe', 'EU']:
            lst_actor_in_row = sorted(row.CN.split(", "))
            # For collaborations, we do not take into account publications with more than 10 authors
            if len(lst_actor_in_row) <= 10:
                for edge in list(combinations(lst_actor_in_row, 2)):
                    if len(set(edge)) > 1:
                        res = tuple(sorted(list(edge)))
                        total_edge[res] += 1

        if map_filter == "Continent":
            lst_actor_in_row = row.CN.split(", ")
            # For collaborations, we do not take into account publications with more than 10 authors
            if len(lst_actor_in_row) <= 10:
                if "" in lst_actor_in_row:
                    lst_actor_in_row = lst_actor_in_row.remove("")

                if not lst_actor_in_row:
                    continue
                lst_actor_in_row = sorted([dic_country_continent[actor] for actor in lst_actor_in_row])
                for edge in list(combinations(lst_actor_in_row, 2)):
                    if len(set(edge)) > 1:
                        res = tuple(sorted(list(edge)))
                        total_edge[res] += 1

    df_edge = pd.DataFrame.from_dict(total_edge, orient="index").reset_index()
    df_edge = df_edge.rename(columns={'index': 'country_pair', 0: 'edge'})

    # Transform tuple (c1, c2) into two columns
    df_edge["c1"] = df_edge.country_pair.apply(lambda x: x[0])
    df_edge["c2"] = df_edge.country_pair.apply(lambda x: x[1])
    df_edge = df_edge.drop(columns="country_pair")

    # df_unique_actors = unique_actors(dataframe, map_filter=map_filter) \
    #     .nlargest(max_actors, "total").reset_index(drop=True)
    if map_filter in ["World", "Europe", 'EU']:
        cond_c1 = df_edge["c1"].isin(dataframe_mentions.Country.values.tolist())
        cond_c2 = df_edge["c2"].isin(dataframe_mentions.Country.values.tolist())
        df_edge = df_edge[cond_c1 & cond_c2]
        df_edge['latitude_c1'] = df_edge['c1'].apply(lambda x: give_lat_long(x)[0])
        df_edge['longitude_c1'] = df_edge['c1'].apply(lambda x: give_lat_long(x)[1])
        df_edge['latitude_c2'] = df_edge['c2'].apply(lambda x: give_lat_long(x)[0])
        df_edge['longitude_c2'] = df_edge['c2'].apply(lambda x: give_lat_long(x)[1])
        max_total_edge = df_edge["edge"].max()
        df_edge.reset_index(drop=True, inplace=True)

    elif map_filter == "Continent":
        cond_c1 = df_edge["c1"].isin(dataframe_mentions.Continent.values.tolist())
        cond_c2 = df_edge["c2"].isin(dataframe_mentions.Continent.values.tolist())
        df_edge = df_edge[cond_c1 & cond_c2]
        df_edge['latitude_c1'] = df_edge['c1'].apply(lambda x: give_lat_long(x, map_filter="Continent")[0])
        df_edge['longitude_c1'] = df_edge['c1'].apply(lambda x: give_lat_long(x, map_filter="Continent")[1])
        df_edge['latitude_c2'] = df_edge['c2'].apply(lambda x: give_lat_long(x, map_filter="Continent")[0])
        df_edge['longitude_c2'] = df_edge['c2'].apply(lambda x: give_lat_long(x, map_filter="Continent")[1])
        max_total_edge = df_edge["edge"].max()
        df_edge.reset_index(drop=True, inplace=True)
    else:
        df_edge = pd.DataFrame(data=None)
        max_total_edge = 0
    return df_edge, max_total_edge


def draw_network_map(dataframe, map_filter="World", save=False,
                     folder="/media/kevin-main/My Passport/SDG/img/network_map/",
                     name="all_pubs",
                     max_num_actors="max"):
    """
    this function draws the graph with countries mentions and collaborations
    :param dataframe:
    :param map_filter: World, Europe or Continent as a string
    :param save: if True, the function saves said graph as a jpeg else just it displays it
    :param folder: folder where to save file
    :param name: name of the file
    :param max_num_actors: number of countries which should be displayed
    :return: a plotly graph
    """
    df_mentions = actors_mention(
        dataframe=dataframe, map_filter=map_filter, max_num_actors=max_num_actors
    )

    print("df_mentions ok")
    df_edges, max_total_edge = \
        actors_edge(dataframe=dataframe, dataframe_mentions=df_mentions, map_filter=map_filter)
    print("df_edge_ok")
    if map_filter == "Continent":
        df_mentions = df_mentions.rename(columns={"Continent": "Country"})
    # Plotting
    fig = go.Figure()
    # Mentions
    fig.add_trace(
        go.Scattergeo(
            # locationmode='country names',
            lon=df_mentions['longitude'],
            lat=df_mentions['latitude'],
            # text=str(df_mentions['Country'])+" = "+str(df_mentions['total_mention']),
            text="Country: " + df_mentions['Country'].astype(str) + "<br>Mentions: " +
                 df_mentions['total_mention'].astype(str),
            # marker_color=df_mentions['percentage'],
            marker=dict(
                size=5 * df_mentions['percentage'],
                line_width=0,
                color=df_mentions['percentage'],
                colorscale='Rainbow',
                # colorscale='YlGnBu',
            ),
            showlegend=False,
        )
    )
    for i in range(len(df_edges)):
        fig.add_trace(
            go.Scattergeo(
                # locationmode='country names',
                lon=[df_edges.longitude_c1[i], df_edges.longitude_c2[i]],
                lat=[df_edges.latitude_c1[i], df_edges.latitude_c2[i]],
                mode="lines",
                line=dict(width=5, color='red'),
                opacity=df_edges["edge"][i] / max_total_edge,
                hoverinfo='skip',
                showlegend=False,
            )
        )

    # Stat for legend

    max_mention = df_mentions['total_mention'].max()
    max_mention_country = \
        df_mentions['Country'][df_mentions['total_mention'] == max_mention].values[0]
    max_edge_country1 = df_edges['c1'][df_edges['edge'] == max_total_edge].values[0]
    max_edge_country2 = df_edges['c2'][df_edges['edge'] == max_total_edge].values[0]
    max_edge_countries = str(max_edge_country1) + ' - ' + str(max_edge_country2)

    fig.add_trace(go.Scattergeo(
        lon=[0],
        lat=[0],
        mode="markers",
        marker=dict(size=0),
        name="Max publications: " + str(max_mention) + "<br>Country: " + str(max_mention_country) +
             "<br><br>Max collab: " + str(max_total_edge) + "<br>Country: " + max_edge_countries,

        text=["Text G", "Text H", "Text I"],
        textposition="bottom center"
    ))
    if map_filter == "Europe":
        scope = "europe"
        center = dict(lon=15, lat=50)
        projection_scale = 1.65
    else:
        scope = "world"
        center = dict(lon=0, lat=0)
        projection_scale = 1

    fig.update_layout(
        template='simple_white',
        title_text="Country analysis: " + name,
        showlegend=True,
        geo=go.layout.Geo(
            scope=scope,
            projection_scale=projection_scale,
            center=center,
            projection_type="natural earth",
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showcountries=True,
        ),
        height=1080,
        width=1980

    )
    # fig.show()
    if save:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        fig.write_image(folder + name + ".jpeg")
        # if map_filter == 'World':
        #     df_mentions.to_pickle(folder + name + "_df_mentions.pkl")
        #     df_edges.to_pickle(folder + name + "_df_edges.pkl")


def draw_network_graph(dataframe, map_filter, save=False, folder="img/Commission/network/", name="amm",
                       max_num_actors=20):
    df_mentions = actors_mention(
        dataframe=dataframe, map_filter=map_filter, max_num_actors=max_num_actors
    )

    print("df_mentions ok")
    df_edges, max_total_edge = \
        actors_edge(dataframe=dataframe, dataframe_mentions=df_mentions, map_filter=map_filter)
    print("df_edge_ok")

    # Networkx
    g = nx.Graph()
    nodesize_raw_numbers = []
    for ind, row in df_mentions.iterrows():
        g.add_node(row["Country"])
        nodesize_raw_numbers.append(row.total_mention)
    maxi_node = max(nodesize_raw_numbers)
    node_size = [100 * node / maxi_node for node in nodesize_raw_numbers]
    for ind, row in df_edges.iterrows():
        c1 = row["c1"]
        c2 = row["c2"]
        count = row["edge"]
        g.add_edge(c1, c2, weight=count)

    pos = nx.spring_layout(g, k=0.2, iterations=1000)
    edges = g.edges()
    w = [g[u][v]['weight'] for u, v in edges]
    maxi = max(w) if len(w) > 0 else 0

    for node in g.nodes:
        g.nodes[node]['pos'] = list(pos[node])

    # Edges = Lines logic
    edge_trace = []
    for ind, edge in enumerate(g.edges()):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = 6 * (g[edge[0]][edge[1]]["weight"]) / maxi

        # Line logic
        trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=weight, color='rgb(231,133,135)'),
            mode='lines')
        edge_trace.append(trace)
    # Nodes logic
    node_x = []
    node_y = []
    node_name = []
    for node in g.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_name.append(str(node))

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hovertext=node_size,
            # hoverinfo='',
            text=node_name,
            textposition="bottom center",
            marker=dict(
                showscale=True,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=node_size,
                colorbar=dict(
                    thickness=15,
                    title='Number of publications',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(g.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: ' + str(len(adjacencies[1])))

    node_trace.marker.color = nodesize_raw_numbers

    edge_trace.append(node_trace)

    fig = go.Figure(data=edge_trace,
                    layout=go.Layout(
                        title=f'collaborations between countries based on <b>{name.split("_")[0]}</b> publications',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.update_traces(textposition='top center', textfont=dict(family='sans-serif', size=17, color='#000'))
    fig.update_layout(template='simple_white')
    if save:
        fig.write_image(folder + name + ".jpeg", width=1900, height=800)
    fig.show()


if __name__ == "__main__":

    df_sdg = pd.read_pickle("data/dataframes/output/all_sdg_fixed_dst.pkl")
    df_digital = pd.read_pickle("data/dataframes/digital/all_digital.pkl")

    draw_network_graph(dataframe=df_sdg, map_filter='World', save=True, name="SDG_world")
    draw_network_graph(dataframe=df_sdg, map_filter='Europe', save=True, name="SDG_EU")

    draw_network_graph(dataframe=df_digital, map_filter='World', save=True, name="DT_world")
    draw_network_graph(dataframe=df_digital, map_filter='Europe', save=True, name="DT_EU")

    draw_network_graph(dataframe=df_sdg[df_sdg['DST']], map_filter='World', save=True, name="SDG-DT_world")
    draw_network_graph(dataframe=df_sdg[df_sdg['DST']], map_filter='Europe', save=True, name="SDG-DT_EU")
