"""From our 3 main databases df_sdg, df_sdg_dt, df_dt, we compute the df_mentions and df_edge and they are saved as
new pickle df """

import pandas as pd
from network_graph import actors_mention, actors_edge

# Loading dataframes
df_sdg = pd.read_pickle("data/dataframes/SDG/all_sdg_fixed_dst.pkl")
cond = df_sdg['DST']
df_sdg_dt = df_sdg[cond]
df_digital = pd.read_pickle("data/dataframes/digital/all_digital.pkl")

# Mentions
df_mention_sdg_world = actors_mention(df_sdg, map_filter='World')
df_mention_sdg_eu = actors_mention(df_sdg, map_filter='EU')

df_mention_sdg_dt_world = actors_mention(df_sdg_dt, map_filter='World')
df_mention_sdg_dt_eu = actors_mention(df_sdg_dt, map_filter='EU')

df_mention_digital_world = actors_mention(df_digital, map_filter='World')
df_mention_digital_eu = actors_mention(df_digital, map_filter='EU')

# Edge
df_edge_sdg_world = actors_edge(df_sdg, df_mention_sdg_world, map_filter='World')[0]
df_edge_sdg_eu = actors_edge(df_sdg, df_mention_sdg_eu, map_filter='EU')[0]

df_edge_sdg_dt_world = actors_edge(df_sdg_dt, df_mention_sdg_dt_world, map_filter='World')[0]
df_edge_sdg_dt_eu = actors_edge(df_sdg_dt, df_mention_sdg_dt_eu, map_filter='EU')[0]

df_edge_digital_world = actors_edge(df_digital, df_mention_digital_world, map_filter='World')[0]
df_edge_digital_eu = actors_edge(df_digital, df_mention_digital_eu, map_filter='EU')[0]

# Saving in pickle
# Mentions
df_mention_sdg_world.to_pickle("data/dataframes/mentions/df_mention_sdg_world.pkl")
df_mention_sdg_eu.to_pickle("data/dataframes/mentions/df_mention_sdg_eu.pkl")
df_mention_sdg_dt_world.to_pickle("data/dataframes/mentions/df_mention_sdg_dt_world.pkl")
df_mention_sdg_dt_eu.to_pickle("data/dataframes/mentions/df_mention_sdg_dt_eu.pkl")
df_mention_digital_world.to_pickle("data/dataframes/mentions/df_mention_digital_world.pkl")
df_mention_digital_eu.to_pickle("data/dataframes/mentions/df_mention_digital_eu.pkl")
# Edge
df_edge_sdg_world.to_pickle("data/dataframes/edge/df_edge_sdg_world.pkl")
df_edge_sdg_eu.to_pickle("data/dataframes/edge/df_edge_sdg_eu.pkl")
df_edge_sdg_dt_world.to_pickle("data/dataframes/edge/df_edge_sdg_dt_world.pkl")
df_edge_sdg_dt_eu.to_pickle("data/dataframes/edge/df_edge_sdg_dt_eu.pkl")
df_edge_digital_world.to_pickle("data/dataframes/edge/df_edge_digital_world.pkl")
df_edge_digital_eu.to_pickle("data/dataframes/edge/df_edge_digital_eu.pkl")
