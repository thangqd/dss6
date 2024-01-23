# -*- coding: utf-8 -*-
"""

"""

# =============================================================================
# Import packages
# =============================================================================
import streamlit as st
from streamlit_option_menu import option_menu
import pyproj
import pandas as pd
import requests
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot

# from forex_python.converter import CurrencyRates
import leafmap.foliumap as leafmap
import folium
from streamlit_folium import st_folium
from PIL import Image
import time
import branca
import json
from shapely import geometry
import matplotlib.pyplot as plt
import os
from streamlit import session_state as ss
import branca.colormap as cm
from matplotlib import colormaps

# import chart_studio.plotly as py
# from IPython.display import HTML

import io
from functions.Lizard_functions import *
from functions.Streamlit_functions import *
from functions.Statistics_functions import *

# import constants (such as labels and colors for legendas in maps)
from input.Constants import *

# =============================================================================
# Page configuration
# =============================================================================
st.set_page_config(page_title="DSS 6", page_icon=":water:", layout="wide")
st.title("MKDC DSS 6")

EXAMPLE_NO = 3
st.write("  ")
selected = streamlit_menu(example=EXAMPLE_NO)

# =============================================================================
# Data retrival
# =============================================================================
lizard_headers = {
    # "username": os.environ["USERNAME"],
    # "password": os.environ["PASSWORD"],
    "username": '__key__',
    "password": 'dHrkmkoz.aeLBK4c0wW0z2OIQWmqWF9QajHARwDQQ',
    "Content-Type": "application/json",
}

damage_curve_flood = pd.read_csv("./input/damageclasses_flood.csv", sep=",")

damage_curve_drought = pd.read_csv("./input/damageclasses_drought.csv", sep=",")

damage_curve_salt = pd.read_csv("./input/damageclasses_salt.csv", sep=",")

damage_curve_landslide = pd.read_csv("./input/damageclasses_landslides.csv", sep=",")


flood_scenarios = find_scenarios("3di_waterdepth")
drought_scenarios = find_scenarios("SPI")
landslide_scenarios = find_scenarios("PDI")
salt_scenarios = find_scenarios("CSI")

# obtain legend colors for damage and affect people maps
df_colors_damage = define_color_legenda(url_colormaps_damage)
colors_damage = df_colors_damage[
    "colors"
].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants

df_colors_ap = define_color_legenda(url_colormaps_ap)
colors_ap = df_colors_ap[
    "colors"
].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants


# =============================================================================
# Body of dashboard
# =============================================================================

if selected == "Floods":
    # Following are dependent on hazard
    scenario_list = flood_scenarios
    hazard_type = "flood_map"
    hazard_style = flood_style
    caption_hazard_map = "Waterdepth (m)"
    header_hazard_map = "Flood map"
    damage_curve = damage_curve_flood
    param = ""

    total_damage = globals()[f"total{param}_url"]
    resi_damage = globals()[f"resi{param}_url"]
    agri_damage = globals()[f"agri{param}_url"]
    com_damage = globals()[f"com{param}_url"]
    indu_damage = globals()[f"indu{param}_url"]
    infra_damage = globals()[f"infra{param}_url"]
    trans_damage = globals()[f"trans{param}_url"]

    # legend colors and range
    colors_hazard = define_color_legenda(url_colormap_flood)
    colors_hazard = colors_hazard[
        "colors"
    ].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants
    vmin_hazard = 0
    vmax_hazard = 1
    invert = False
    # essential coordinates
    location_flood, bbox_flood = define_coordinates_maps(total_url, lizard_headers)

    ######
    col1, col2, col3 = st.columns([0.2, 0.79, 0.01])

    # introduce session state to store the 'pressed' state of each button
    if "damage_curve" not in st.session_state:  # 1 = Damage curve
        st.session_state["damage_curve"] = False

    if "land_use" not in st.session_state:  # 2 = Land use
        st.session_state["land_use"] = False

    if "calculate_damage" not in st.session_state:  # 3 = Calculate Damage
        st.session_state["calculate_damage"] = False

    if "flood_map" not in st.session_state:  # 3 = Go back to Flood map
        st.session_state["flood_map"] = False

    if "calculator" not in st.session_state:
        st.session_state["calculator"] = False

    with col1:
        # Section 1: Select Scenario and Display Map
        st.header("Menu")

        scenarios = scenario_list["name"]
        selected_scenario = st.selectbox("##### 1) Select a scenario", scenarios)

        if st.button("Flood map"):
            # toggle calculate_damage session state
            st.session_state["flood_map"] = not st.session_state["flood_map"]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["calculate_damage"] = False

        st.write("##### 2) View background information")

        if st.button("Go to Damage Curve"):
            st.session_state["damage_curve"] = not st.session_state["damage_curve"]
            st.session_state["calculate_damage"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False

        if st.button("Go to Land Use"):
            st.session_state["land_use"] = not st.session_state["land_use"]
            st.session_state["damage_curve"] = False
            st.session_state["calculate_damage"] = False
            st.session_state["flood_map"] = False

        st.write("   ")
        st.markdown("##### 3) Start calculations")

        if st.button("Calculate Damage", type="primary"):
            st.session_state["calculate_damage"] = not st.session_state[
                "calculate_damage"
            ]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False


    with col2:
        subcol1, subcol2 = st.columns([0.8, 0.2])
        if st.session_state["flood_map"]:
            if selected_scenario is not None:
                scenario_data = scenario_list[
                    scenario_list["name"] == selected_scenario
                ].iloc[0]
                layer_hazard = format_wms(
                    scenario_data["name"],
                    scenario_data["wms_info"]["layer"],
                    hazard_style,
                )
                st.subheader(header_hazard_map)

                # get flood map
                folium_map_hazard = make_map(
                    layer_hazard,
                    location_flood,
                    bbox_flood,
                    colors_hazard,
                    vmin_hazard,
                    vmax_hazard,
                    caption_hazard_map,
                )

                st_data_start = st_folium(folium_map_hazard, width=790, height=400)

        if st.session_state["damage_curve"]:  # add under this line damage curve
            # make damage curve
            fig_damage_curve = make_damage_curve(
                damage_curve, df_colors_landuse, caption_hazard_map, invert
            )

            st.plotly_chart(fig_damage_curve, use_container_width=True)

        if st.session_state[
            "land_use"
        ]:  # add under this line land use and population maps
            # st.header("Step 3: Land use and population")

            # Display the first WMS map
            st.subheader("Landuse map")
            landuse_layer = format_wms(monre_lulc_name, monre_lulc_layer, landuse_style)

            landuse_map = make_landuse_map(
                landuse_layer,
                location_landuse,
                df_colors_landuse.index.tolist(),
                df_colors_landuse["colors"].tolist(),
            )

            landuse_map.to_streamlit(height=400)

        if st.session_state[
            "calculate_damage"
        ]:  # add under this line the table with damages per land use class
            # create states and buttons

            if "damage_map" not in st.session_state:  # 5 = damage map
                st.session_state["damage_map"] = True

            if "damage_statistics" not in st.session_state:  # 6 = damage statistics
                st.session_state["damage_statistics"] = False

            if (
                "affected_people" not in st.session_state
            ):  # 7 = affected people map and statistics
                st.session_state["affected_people"] = False

            if "download_results" not in st.session_state:  # 8 = download results
                st.session_state["download_results"] = False

            col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
            with col1:
                if st.button("Damage Map", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_map"] = not st.session_state["damage_map"]
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col2:
                if st.button("Damage Statistics", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_statistics"] = not st.session_state[
                        "damage_statistics"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col3:
                if st.button(
                    "Affected people Map and Statistics", use_container_width=True
                ):
                    # toggle calculate_damage session state
                    st.session_state["affected_people"] = not st.session_state[
                        "affected_people"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col4:
                if st.button("Download results", use_container_width=True):
                    st.session_state["download_results"] = not st.session_state[
                        "download_results"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["calculate_damage"] = True

            # define all maps, tables and figures here --> then it can be used in each under state
            if selected_scenario is not None:

                #Before calculating damage all the scenarios need to be patched
                scenario_data = flood_scenarios[flood_scenarios['name'] == selected_scenario].iloc[0]
                scenario_uuid = scenario_data['uuid']
                projection = scenario_data['projection']
                new_scenario = create_lizard_scenario(hazard_type,scenario_uuid, total_damage, resi_damage, agri_damage, com_damage, indu_damage,infra_damage,trans_damage)
            

            # make damage map
            layer_damage = format_wms(
                "damage", new_scenario["total"]["wms_info"], damage_style
            )
            vmin_damage_f = 0
            vmax_damage_f = 1000000
            caption_damage_f = "Damage costs (VND/m2)"
            # Create
            folium_map_damage = make_map(
                layer_damage,
                location_flood,
                bbox_flood,
                colors_damage,
                vmin_damage_f,
                vmax_damage_f,
                caption_damage_f,
            )

            # make damage costs per land use table

            df_damage1 = calculate_total_damage_per_landuse(new_scenario['total']['url'], new_scenario['residential']['url'], new_scenario['agricultural']['url'], new_scenario['commercial']['url'], new_scenario['industrial']['url'], new_scenario['infrastructure']['url'], new_scenario['transportation']['url'], lizard_headers, pixel_size, total_damage, projection)

            
            fig_damage_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_damage1[["Land use",r"Damage costs (VND) "]]),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_damage1["Land use"], df_damage1[r"Damage costs (VND) "]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])
                        
            # make damage costs per land use pie chart 

            labels = (
                "Residential",
                "Agricultural",
                "Commercial",
                "Industrial",
                "Infrastructure",
                "Transport",
            )

            df_damage_without_total = df_damage1[:-1]
            fig_damage_pie = px.pie(
                df_damage_without_total,
                values="Damage costs (VND)",
                names="Land use",
                color="Land use",
                color_discrete_map={
                    "Residential": df_colors_landuse.colors["Residential"],
                    "Agricultural": df_colors_landuse.colors["Agriculture"],
                    "Commercial": df_colors_landuse.colors["Commercial"],
                    "Industrial": df_colors_landuse.colors["Industrial"],
                    "Infrastructure": df_colors_landuse.colors["Infrastructure"],
                    "Transport": df_colors_landuse.colors["Transport"],
                },
            )

            # make affected people map
            if selected_scenario is not None:
                affected_new = create_affected_breakdown(scenario_uuid)

                layer_affected = format_wms(
                    "Affected people",
                    affected_new["total_affected"]["wms_info"],
                    damage_style,
                )

                # ap = affected people
                # colors_ap_f = df_colors_ap['colors'].tolist() # dit nog aanpassen, waarschijnlijk defineren in constants
                vmin_ap_f = 0
                vmax_ap_f = 1000
                caption_ap_f = "Affected people (people/km2)"

                folium_map_ap = make_map(
                    layer_affected,
                    location_flood,
                    bbox_flood,
                    colors_ap,
                    vmin_ap_f,
                    vmax_ap_f,
                    caption_ap_f,
                )

            # make affected people table

            df_ap = calculate_total_ap_per_breakdown(affected_new['total_affected']['url'], affected_new['men_affected']['url'], affected_new['women_affected']['url'], 
                                                     affected_new['youth_affected']['url'], affected_new['children_affected']['url'], lizard_headers, pixel_size, new_scenario['total']['url'], projection)
            
            fig_ap_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_ap.columns),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_ap["Population group"], df_ap["Number of affected people"]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])

 

            if st.session_state["damage_map"]:
                st.subheader("Calculated Damage Map")

                # make damage map

                st_data_damage = st_folium(folium_map_damage, height=500, width=900)

            if st.session_state["damage_statistics"]:
                st.subheader("Damage Statistics")

                col1, col2 = st.columns([1, 2])

                with col1:
                    # Table - damage costs per land use

                    st.plotly_chart(
                        fig_damage_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    # Pie chart - damage costs per land use

                    st.plotly_chart(fig_damage_pie, theme=None)

            if st.session_state["affected_people"]:
                st.subheader("Affected people Map")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.plotly_chart(
                        fig_ap_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    st_data_damage = st_folium(folium_map_ap, width=670, height=400)

            if st.session_state["download_results"]:
                # first_plot_url = py.plot(fig, filename='apple stock moving average', auto_open=False,)

                st.write("press this button to download all tables and charts")

                html_fig1 = fig_damage_costs.to_html(full_html=False)
                html_fig2 = fig_damage_pie.to_html(full_html=False)
                html_fig3 = fig_ap_costs.to_html(full_html=False)

                # Convert Folium map to HTML
                map_damage_html = folium_map_damage._repr_html_()
                map_ap_html = folium_map_ap._repr_html_()

                # Create HTML string incorporating Plotly figures
                your_html_string = f"""
                <html>
                <head>
                    <title>MKDC DSS6</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                </head>
                <body>
                    <h1>MKDC DSS6 Forecast Damage costs and Affected people </h1>
                    <div>
                        <h3>Hazard:</h3><p>{selected}</p>
                        <h3>Scenario:</h3><p>{selected_scenario}</p>
                    </div>
                    <div>
                        <h2>Damage costs map</h2>
                        {map_damage_html}
                    </div>
                    <div>
                        <h2>Damage cost table</h2>
                        {html_fig1}
                    </div>
                    <div>
                        <h2>Damage costs pie</h2>
                        {html_fig2}
                    </div>
                    <div>
                        <h2>Affected people map</h2>
                        {map_ap_html}
                    </div>
                    <div>
                        <h2>Affected people statistics</h2>
                        {html_fig3}
                    </div>
                </body>
                </html>
                """

                # Display download button
                download_html(your_html_string)


if selected == "Drought":
    # Following are dependent on hazard
    scenario_list = drought_scenarios
    hazard_type = "drought_map"
    hazard_style = drought_style
    caption_hazard_map = "SPI (-)"
    header_hazard_map = "Drought map"
    damage_curve = damage_curve_drought
    param = "_drought"

    total_damage = globals()[f"total{param}_url"]
    resi_damage = globals()[f"resi{param}_url"]
    agri_damage = globals()[f"agri{param}_url"]
    com_damage = globals()[f"com{param}_url"]
    indu_damage = globals()[f"indu{param}_url"]
    infra_damage = globals()[f"infra{param}_url"]
    trans_damage = globals()[f"trans{param}_url"]
    vmin_hazard = -2
    vmax_hazard = 2
    invert = True

    # legend colors and range
    colors_hazard = define_color_legenda(url_colormap_drought)
    colors_hazard = colors_hazard[
        "colors"
    ].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants

    # essential coordinates

    location_drought, bbox_drought = define_coordinates_maps(
        total_drought_url, lizard_headers
    )


    ######
    col1, col2, col3 = st.columns([0.2, 0.79, 0.01])

    # introduce session state to store the 'pressed' state of each button
    if "damage_curve" not in st.session_state:  # 1 = Damage curve
        st.session_state["damage_curve"] = False

    if "land_use" not in st.session_state:  # 2 = Land use
        st.session_state["land_use"] = False

    if "calculate_damage" not in st.session_state:  # 3 = Calculate Damage
        st.session_state["calculate_damage"] = False

    if "flood_map" not in st.session_state:  # 3 = Go back to Flood map
        st.session_state["flood_map"] = False

    if "calculator" not in st.session_state:
        st.session_state["calculator"] = False

    with col1:
        # Section 1: Select Scenario and Display Map
        st.header("Menu")

        scenarios = scenario_list["name"]
        selected_scenario = st.selectbox("##### 1) Select a scenario", scenarios)

        if st.button(header_hazard_map):
            # toggle calculate_damage session state
            st.session_state["flood_map"] = not st.session_state["flood_map"]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["calculate_damage"] = False

        st.write("##### 2) View background information")

        if st.button("Go to Damage Curve"):
            st.session_state["damage_curve"] = not st.session_state["damage_curve"]
            st.session_state["calculate_damage"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False

        if st.button("Go to Land Use"):
            st.session_state["land_use"] = not st.session_state["land_use"]
            st.session_state["damage_curve"] = False
            st.session_state["calculate_damage"] = False
            st.session_state["flood_map"] = False

        st.write("   ")
        st.markdown("##### 3) Start calculations")

        if st.button("Calculate Damage", type="primary"):
            st.session_state["calculate_damage"] = not st.session_state[
                "calculate_damage"
            ]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False



    with col2:
        subcol1, subcol2 = st.columns([0.8, 0.2])
        if st.session_state["flood_map"]:
            if selected_scenario is not None:
                scenario_data = scenario_list[
                    scenario_list["name"] == selected_scenario
                ].iloc[0]
                layer_hazard = format_wms(
                    scenario_data["name"],
                    scenario_data["wms_info"]["layer"],
                    hazard_style,
                )
                st.subheader(header_hazard_map)

                # get flood map
                folium_map_hazard = make_map(
                    layer_hazard,
                    location_drought,
                    bbox_drought,
                    colors_hazard,
                    vmin_hazard,
                    vmax_hazard,
                    caption_hazard_map,
                )

                st_data_start = st_folium(folium_map_hazard, width=790, height=400)

        if st.session_state["damage_curve"]:  # add under this line damage curve
            # make damage curve
            fig_damage_curve = make_damage_curve(
                damage_curve, df_colors_landuse, caption_hazard_map, invert
            )

            st.plotly_chart(fig_damage_curve, use_container_width=True)

        if st.session_state[
            "land_use"
        ]:  # add under this line land use and population maps
            # st.header("Step 3: Land use and population")

            # Display the first WMS map
            st.subheader("Landuse map")

            landuse_layer = format_wms(monre_lulc_name, monre_lulc_layer, landuse_style)

            landuse_map = make_landuse_map(
                landuse_layer,
                location_landuse,
                df_colors_landuse.index.tolist(),
                df_colors_landuse["colors"].tolist(),
            )

            landuse_map.to_streamlit(height=400)

        if st.session_state[
            "calculate_damage"
        ]:  # add under this line the table with damages per land use class
            # create new scenario
            if selected_scenario is not None:

                #Before calculating damage all the scenarios need to be patched
                scenario_data = scenario_list[scenario_list['name'] == selected_scenario].iloc[0]
                scenario_uuid = scenario_data['uuid']
                projection = scenario_data['projection']
                new_scenario = create_lizard_scenario(hazard_type, scenario_uuid, total_damage, resi_damage, agri_damage, com_damage, indu_damage, infra_damage, trans_damage)
                
            
        

            # make damage map
            layer_damage = format_wms(
                "damage", new_scenario["total"]["wms_info"], damage_style_drought
            )
            vmin_damage_f = 0
            vmax_damage_f = 100
            caption_damage_f = "Damage costs (VND/m2)"
            # Create
            folium_map_damage = make_map(
                layer_damage,
                location_drought,
                bbox_drought,
                colors_damage,
                vmin_damage_f,
                vmax_damage_f,
                caption_damage_f,
            )

            # damage statistics - table

            df_damage1 = calculate_total_damage_per_landuse(new_scenario['total']['url'], new_scenario['residential']['url'], 
                                                            new_scenario['agricultural']['url'], new_scenario['commercial']['url'], 
                                                            new_scenario['industrial']['url'], new_scenario['infrastructure']['url'], 
                                                            new_scenario['transportation']['url'], lizard_headers, pixel_size_drought,
                                                            total_damage, projection)

            fig_damage_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_damage1[["Land use",r"Damage costs (VND) "]]),
                                        fill_color='#859C79',
                                        align='center',
                                        font=dict(color='white', size=16),
                                        height=35),
                            cells=dict(values=[df_damage1["Land use"], df_damage1[r"Damage costs (VND) "]],
                                       fill_color='#F0F2F6',
                                       align=['center', 'right'],
                                       font=dict(color='black', size=14,),
                                       height=30))
                        ])

            

            # damage statistics - pie chart
            df_damage_without_total = df_damage1[:-1]
            fig_damage_pie = px.pie(
                df_damage_without_total,
                values="Damage costs (VND)",
                names="Land use",
                color="Land use",
                color_discrete_map={
                    "Residential": df_colors_landuse.colors["Residential"],
                    "Agricultural": df_colors_landuse.colors["Agriculture"],
                    "Commercial": df_colors_landuse.colors["Commercial"],
                    "Industrial": df_colors_landuse.colors["Industrial"],
                    "Infrastructure": df_colors_landuse.colors["Infrastructure"],
                    "Transport": df_colors_landuse.colors["Transport"],
                },
            )

            # affected people - map
            affected_new = create_affected_breakdown(new_scenario["total"]["uuid"])

            layer_affected = format_wms(
                " people", affected_new["total_affected"]["wms_info"], displaced_style
            )

            # ap = affected people
            # colors_ap_f = df_colors_ap['colors'].tolist() # dit nog aanpassen, waarschijnlijk defineren in constants
            vmin_ap_f = 0
            vmax_ap_f = 1000
            caption_ap_f = "Affecteded people (people/km2)"

            folium_map_ap = make_map(
                layer_affected,
                location_drought,
                bbox_drought,
                colors_ap,
                vmin_ap_f,
                vmax_ap_f,
                caption_ap_f,
            )

            # make affected people table

            df_ap = calculate_total_ap_per_breakdown(affected_new['total_affected']['url'], affected_new['men_affected']['url'], affected_new['women_affected']['url'], 
                                                     affected_new['youth_affected']['url'], affected_new['children_affected']['url'], lizard_headers, pixel_size_drought,  total_damage, projection)
            
            fig_ap_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_ap.columns),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_ap["Population group"], df_ap["Number of affected people"]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])

        
        
            if "damage_map" not in st.session_state:  # 5 = damage map
                st.session_state["damage_map"] = True

            if "damage_statistics" not in st.session_state:  # 6 = damage statistics
                st.session_state["damage_statistics"] = False

            if (
                "affected_people" not in st.session_state
            ):  # 7 = affected people map and statistics
                st.session_state["affected_people"] = False

            if "download_results" not in st.session_state:  # 8 = download results
                st.session_state["download_results"] = False

            col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
            with col1:
                if st.button("Damage Map", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_map"] = not st.session_state["damage_map"]
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col2:
                if st.button("Damage Statistics", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_statistics"] = not st.session_state[
                        "damage_statistics"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col3:
                if st.button(
                    "Affected people Map and Statistics", use_container_width=True
                ):
                    # toggle calculate_damage session state
                    st.session_state["affected_people"] = not st.session_state[
                        "affected_people"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col4:
                if st.button("Download results", use_container_width=True):
                    st.session_state["download_results"] = not st.session_state[
                        "affected_people"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["calculate_damage"] = True

            if st.session_state["damage_map"]:
                st.subheader("Calculated Damage Map")

                st_data_damage = st_folium(folium_map_damage, height=500, width=900)

            if st.session_state["damage_statistics"]:
                st.subheader("Damage Statistics")
                col1, col2 = st.columns([1, 2])

                with col1:

                    def make_bold(val):
                        return "font-weight: bold"


                    fig = go.Figure(
                        data=[
                            go.Table(
                                header=dict(
                                    values=list(
                                        df_damage1[["Land use", r"Damage costs (VND) "]]
                                    ),
                                    fill_color="#859C79",
                                    align="center",
                                    font=dict(color="white", size=16),
                                    height=35,
                                ),
                                cells=dict(
                                    values=[
                                        df_damage1["Land use"],
                                        df_damage1[r"Damage costs (VND) "],
                                    ],
                                    fill_color="#F0F2F6",
                                    align=["center", "right"],
                                    font=dict(
                                        color="black",
                                        size=14,
                                    ),
                                    height=30,
                                ),
                            )
                        ]
                    )

                    st.plotly_chart(
                        fig_damage_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    # Pie chart, where the slices will be ordered and plotted counter-clockwise:

                    st.plotly_chart(fig_damage_pie, theme=None)

            if st.session_state["affected_people"]:
                st.subheader("Affected people Map")
                col1, col2 = st.columns([1, 2])

                
                with col1:
                    st.plotly_chart(fig_ap_costs, theme='streamlit', use_container_width =  True)
                
                with col2:
                    
                        st_data_damage = st_folium(
                            folium_map_ap, width=670, height=400
                        )
                            
            if st.session_state["download_results"]:
                st.write("press this button to download all tables and charts")

                html_fig1 = fig_damage_costs.to_html(full_html=False)
                html_fig2 = fig_damage_pie.to_html(full_html=False)
                html_fig3 = fig_ap_costs.to_html(full_html=False)

                # Convert Folium map to HTML
                map_damage_html = folium_map_damage._repr_html_()
                map_ap_html = folium_map_ap._repr_html_()

                # Create HTML string incorporating Plotly figures
                your_html_string = f"""
                <html>
                <head>
                    <title>MKDC DSS6</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                </head>
                <body>
                    <h1>MKDC DSS6 Forecast Damage costs and Affected people</h1>
                    <div>
                        <h3>Hazard:</h3><p>{selected}</p>
                        <h3>Scenario:</h3><p>{selected_scenario}</p>
                    </div>
                    <div>
                        <h2>Damage costs map</h2>
                        {map_damage_html}
                    </div>
                    <div>
                        <h2>Damage cost table</h2>
                        {html_fig1}
                    </div>
                    <div>
                        <h2>Damage costs pie</h2>
                        {html_fig2}
                    </div>
                    <div>
                        <h2>Affected people map</h2>
                        {map_ap_html}
                    </div>
                    <div>
                        <h2>Affected people statistics</h2>
                        {html_fig3}
                    </div>
                </body>
                </html>
                """

                # Display download button
                download_html(your_html_string)

if selected == "Saline intrusion":
    # Following are dependent on hazard
    scenario_list = salt_scenarios
    hazard_type = "salt_map"
    hazard_style = insaline_style
    caption_hazard_map = "CSI (-)"
    header_hazard_map = "Saline intrusion map"
    damage_curve = damage_curve_salt
    param = "_salt"

    total_damage = globals()[f"total{param}_url"]
    resi_damage = globals()[f"resi{param}_url"]
    agri_damage = globals()[f"agri{param}_url"]
    com_damage = globals()[f"com{param}_url"]
    indu_damage = globals()[f"indu{param}_url"]
    infra_damage = globals()[f"infra{param}_url"]
    trans_damage = globals()[f"trans{param}_url"]
    vmin_hazard = -2
    vmax_hazard = 2
    invert = True

    # legend colors and range
    colors_hazard = define_color_legenda(url_colormap_insaline)
    colors_hazard = colors_hazard[
        "colors"
    ].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants

    # essential coordinates
    location_drought, bbox_drought = define_coordinates_maps(
        total_drought_url, lizard_headers
    )


    ######
    col1, col2, col3 = st.columns([0.2, 0.79, 0.01])

    # introduce session state to store the 'pressed' state of each button
    if "damage_curve" not in st.session_state:  # 1 = Damage curve
        st.session_state["damage_curve"] = False

    if "land_use" not in st.session_state:  # 2 = Land use
        st.session_state["land_use"] = False

    if "calculate_damage" not in st.session_state:  # 3 = Calculate Damage
        st.session_state["calculate_damage"] = False

    if "flood_map" not in st.session_state:  # 3 = Go back to Flood map
        st.session_state["flood_map"] = False

    if "calculator" not in st.session_state:
        st.session_state["calculator"] = False

    with col1:
        # Section 1: Select Scenario and Display Map
        st.header("Menu")

        scenarios = scenario_list["name"]
        selected_scenario = st.selectbox("##### 1) Select a scenario", scenarios)

        if st.button(header_hazard_map):
            # toggle calculate_damage session state
            st.session_state["flood_map"] = not st.session_state["flood_map"]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["calculate_damage"] = False

        st.write("##### 2) View background information")

        if st.button("Go to Damage Curve"):
            st.session_state["damage_curve"] = not st.session_state["damage_curve"]
            st.session_state["calculate_damage"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False

        if st.button("Go to Land Use"):
            st.session_state["land_use"] = not st.session_state["land_use"]
            st.session_state["damage_curve"] = False
            st.session_state["calculate_damage"] = False
            st.session_state["flood_map"] = False

        st.write("   ")
        st.markdown("##### 3) Start calculations")

        if st.button("Calculate Damage", type="primary"):
            st.session_state["calculate_damage"] = not st.session_state[
                "calculate_damage"
            ]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False


    with col2:
        subcol1, subcol2 = st.columns([0.8, 0.2])
        if st.session_state["flood_map"]:
            if selected_scenario is not None:
                scenario_data = scenario_list[
                    scenario_list["name"] == selected_scenario
                ].iloc[0]
                layer_hazard = format_wms(
                    scenario_data["name"],
                    scenario_data["wms_info"]["layer"],
                    hazard_style,
                )
                st.subheader(header_hazard_map)

                # get flood map
                folium_map_hazard = make_map(
                    layer_hazard,
                    location_drought,
                    bbox_drought,
                    colors_hazard,
                    vmin_hazard,
                    vmax_hazard,
                    caption_hazard_map,
                )

                st_data_start = st_folium(folium_map_hazard, width=790, height=400)

        if st.session_state["damage_curve"]:  # add under this line damage curve
            # make damage curve
            fig_damage_curve = make_damage_curve(
                damage_curve, df_colors_landuse, caption_hazard_map, invert
            )

            st.plotly_chart(fig_damage_curve, use_container_width=True)

        if st.session_state[
            "land_use"
        ]:  # add under this line land use and population maps
            # st.header("Step 3: Land use and population")

            # Display the first WMS map
            st.subheader("Landuse map")

            landuse_layer = format_wms(monre_lulc_name, monre_lulc_layer, landuse_style)

            landuse_map = make_landuse_map(
                landuse_layer,
                location_landuse,
                df_colors_landuse.index.tolist(),
                df_colors_landuse["colors"].tolist(),
            )

            landuse_map.to_streamlit(height=400)

        if st.session_state[
            "calculate_damage"
        ]:  # add under this line the table with damages per land use class
            # create new scenario
            if selected_scenario is not None:
                #Before calculating damage all the scenarios need to be patched
                scenario_data = scenario_list[scenario_list['name'] == selected_scenario].iloc[0]
                scenario_uuid = scenario_data['uuid']
                projection = scenario_data['projection']
                new_scenario = create_lizard_scenario(hazard_type,scenario_uuid,total_damage, resi_damage, agri_damage, com_damage, indu_damage,infra_damage,trans_damage)
            
        

            # make damage map
            layer_damage = format_wms(
                "damage", new_scenario["total"]["wms_info"], damage_style_drought
            )
            vmin_damage_f = 0
            vmax_damage_f = 100

            caption_damage_f = "Damage costs (VND/m2)"
            # Create
            folium_map_damage = make_map(
                layer_damage,
                location_drought,
                bbox_drought,
                colors_damage,
                vmin_damage_f,
                vmax_damage_f,
                caption_damage_f,
            )


            # damage statistics - table

            df_damage1 = calculate_total_damage_per_landuse(new_scenario['total']['url'], new_scenario['residential']['url'], new_scenario['agricultural']['url'], new_scenario['commercial']['url'], new_scenario['industrial']['url'], new_scenario['infrastructure']['url'], new_scenario['transportation']['url'], lizard_headers, pixel_size_drought, total_damage, projection)

            fig_damage_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_damage1[["Land use",r"Damage costs (VND) "]]),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_damage1["Land use"], df_damage1[r"Damage costs (VND) "]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])


            

            # damage statistics - pie chart
            df_damage_without_total = df_damage1[:-1]
            fig_damage_pie = px.pie(
                df_damage_without_total,
                values="Damage costs (VND)",
                names="Land use",
                color="Land use",
                color_discrete_map={
                    "Residential": df_colors_landuse.colors["Residential"],
                    "Agricultural": df_colors_landuse.colors["Agriculture"],
                    "Commercial": df_colors_landuse.colors["Commercial"],
                    "Industrial": df_colors_landuse.colors["Industrial"],
                    "Infrastructure": df_colors_landuse.colors["Infrastructure"],
                    "Transport": df_colors_landuse.colors["Transport"],
                },
            )

            # affected people - map
            affected_new = create_affected_breakdown(new_scenario["total"]["uuid"])

            layer_affected = format_wms(
                " people", affected_new["total_affected"]["wms_info"], displaced_style
            )

            # ap = affected people
            # colors_ap_f = df_colors_ap['colors'].tolist() # dit nog aanpassen, waarschijnlijk defineren in constants
            vmin_ap_f = 0
            vmax_ap_f = 1000
            caption_ap_f = "Affecteded people (people/km2)"

            folium_map_ap = make_map(
                layer_affected,
                location_drought,
                bbox_drought,
                colors_ap,
                vmin_ap_f,
                vmax_ap_f,
                caption_ap_f,
            )

            # make affected people table

            df_ap = calculate_total_ap_per_breakdown(affected_new['total_affected']['url'], affected_new['men_affected']['url'], affected_new['women_affected']['url'], 
                                                     affected_new['youth_affected']['url'], affected_new['children_affected']['url'], lizard_headers, pixel_size_drought, total_damage, projection)
            
            fig_ap_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_ap.columns),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_ap["Population group"], df_ap["Number of affected people"]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])
        
        

            if "damage_map" not in st.session_state:  # 5 = damage map
                st.session_state["damage_map"] = True

            if "damage_statistics" not in st.session_state:  # 6 = damage statistics
                st.session_state["damage_statistics"] = False

            if (
                "affected_people" not in st.session_state
            ):  # 7 = affected people map and statistics
                st.session_state["affected_people"] = False

            if "download_results" not in st.session_state:  # 8 = download results
                st.session_state["download_results"] = False

            col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
            with col1:
                if st.button("Damage Map", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_map"] = not st.session_state["damage_map"]
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col2:
                if st.button("Damage Statistics", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_statistics"] = not st.session_state[
                        "damage_statistics"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col3:
                if st.button(
                    "Affected people Map and Statistics", use_container_width=True
                ):
                    # toggle calculate_damage session state
                    st.session_state["affected_people"] = not st.session_state[
                        "affected_people"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col4:
                if st.button("Download results", use_container_width=True):
                    st.session_state["download_results"] = not st.session_state[
                        "download_results"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["calculate_damage"] = True

            if st.session_state["damage_map"]:
                st.subheader("Calculated Damage Map")

                st_data_damage = st_folium(folium_map_damage, height=500, width=900)

            if st.session_state["damage_statistics"]:
                st.subheader("Damage Statistics")
                col1, col2 = st.columns([1, 2])

                with col1:


                    def make_bold(val):
                        return "font-weight: bold"

                    fig = go.Figure(
                        data=[
                            go.Table(
                                header=dict(
                                    values=list(
                                        df_damage1[["Land use", r"Damage costs (VND) "]]
                                    ),
                                    fill_color="#859C79",
                                    align="center",
                                    font=dict(color="white", size=16),
                                    height=35,
                                ),
                                cells=dict(
                                    values=[
                                        df_damage1["Land use"],
                                        df_damage1[r"Damage costs (VND) "],
                                    ],
                                    fill_color="#F0F2F6",
                                    align=["center", "right"],
                                    font=dict(
                                        color="black",
                                        size=14,
                                    ),
                                    height=30,
                                ),
                            )
                        ]
                    )

                    st.plotly_chart(
                        fig_damage_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    # Pie chart, where the slices will be ordered and plotted counter-clockwise:

                    st.plotly_chart(fig_damage_pie, theme=None)

            if st.session_state["affected_people"]:
                st.subheader("Affected people Map")
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.plotly_chart(
                        fig_ap_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    st_data_damage = st_folium(folium_map_ap, width=670, height=400)

            if st.session_state["download_results"]:
                st.write("press this button to download all tables and charts")

                html_fig1 = fig_damage_costs.to_html(full_html=False)
                html_fig2 = fig_damage_pie.to_html(full_html=False)
                html_fig3 = fig_ap_costs.to_html(full_html=False)

                # Convert Folium map to HTML
                map_damage_html = folium_map_damage._repr_html_()
                map_ap_html = folium_map_ap._repr_html_()

                # Create HTML string incorporating Plotly figures
                your_html_string = f"""
                <html>
                <head>
                    <title>MKDC DSS6</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                </head>
                <body>
                    <h1>MKDC DSS6 Forecast Damage costs and Affected people</h1>
                    <div>
                        <h3>Hazard:</h3><p>{selected}</p>
                        <h3>Scenario:</h3><p>{selected_scenario}</p>
                    </div>
                    <div>
                        <h2>Damage costs map</h2>
                        {map_damage_html}
                    </div>
                    <div>
                        <h2>Damage cost table</h2>
                        {html_fig1}
                    </div>
                    <div>
                        <h2>Damage costs pie</h2>
                        {html_fig2}
                    </div>
                    <div>
                        <h2>Affected people map</h2>
                        {map_ap_html}
                    </div>
                    <div>
                        <h2>Affected people statistics</h2>
                        {html_fig3}
                    </div>
                </body>
                </html>
                """

                # Display download button
                download_html(your_html_string)

if selected == "Landslide":
    # Following are dependent on hazard
    scenario_list = landslide_scenarios
    hazard_type = "landslides_map"
    hazard_style = landslide_style
    caption_hazard_map = "PDI (-)"
    header_hazard_map = "Landslide map"
    damage_curve = damage_curve_landslide
    param = "_slide"

    total_damage = globals()[f"total{param}_url"]
    resi_damage = globals()[f"resi{param}_url"]
    agri_damage = globals()[f"agri{param}_url"]
    com_damage = globals()[f"com{param}_url"]
    indu_damage = globals()[f"indu{param}_url"]
    infra_damage = globals()[f"infra{param}_url"]
    trans_damage = globals()[f"trans{param}_url"]
    vmin_hazard = -2
    vmax_hazard = 2
    invert = False

    # legend colors and range
    colors_hazard = define_color_legenda(url_colormap_landslide)
    colors_hazard = colors_hazard[
        "colors"
    ].tolist()  # dit nog aanpassen, waarschijnlijk defineren in constants

    # essential coordinates

    location_drought, bbox_drought = define_coordinates_maps(
        total_slide_url, lizard_headers
    )

    ######
    col1, col2, col3 = st.columns([0.2, 0.79, 0.01])

    # introduce session state to store the 'pressed' state of each button
    if "damage_curve" not in st.session_state:  # 1 = Damage curve
        st.session_state["damage_curve"] = False

    if "land_use" not in st.session_state:  # 2 = Land use
        st.session_state["land_use"] = False

    if "calculate_damage" not in st.session_state:  # 3 = Calculate Damage
        st.session_state["calculate_damage"] = False

    if "flood_map" not in st.session_state:  # 3 = Go back to Flood map
        st.session_state["flood_map"] = False

    if "calculator" not in st.session_state:
        st.session_state["calculator"] = False

    with col1:
        # Section 1: Select Scenario and Display Map
        st.header("Menu")

        scenarios = scenario_list["name"]
        selected_scenario = st.selectbox("##### 1) Select a scenario", scenarios)

        if st.button(header_hazard_map):
            # toggle calculate_damage session state
            st.session_state["flood_map"] = not st.session_state["flood_map"]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["calculate_damage"] = False

        st.write("##### 2) View background information")

        if st.button("Go to Damage Curve"):
            st.session_state["damage_curve"] = not st.session_state["damage_curve"]
            st.session_state["calculate_damage"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False

        if st.button("Go to Land Use"):
            st.session_state["land_use"] = not st.session_state["land_use"]
            st.session_state["damage_curve"] = False
            st.session_state["calculate_damage"] = False
            st.session_state["flood_map"] = False

        st.write("   ")
        st.markdown("##### 3) Start calculations")

        if st.button("Calculate Damage", type="primary"):
            st.session_state["calculate_damage"] = not st.session_state[
                "calculate_damage"
            ]
            st.session_state["damage_curve"] = False
            st.session_state["land_use"] = False
            st.session_state["flood_map"] = False



    with col2:
        subcol1, subcol2 = st.columns([0.8, 0.2])
        if st.session_state["flood_map"]:
            if selected_scenario is not None:
                scenario_data = scenario_list[
                    scenario_list["name"] == selected_scenario
                ].iloc[0]
                layer_hazard = format_wms(
                    scenario_data["name"],
                    scenario_data["wms_info"]["layer"],
                    hazard_style,
                )
                st.subheader(header_hazard_map)

                # get flood map
                folium_map_hazard = make_map(
                    layer_hazard,
                    location_drought,
                    bbox_drought,
                    colors_hazard,
                    vmin_hazard,
                    vmax_hazard,
                    caption_hazard_map,
                )

                st_data_start = st_folium(folium_map_hazard, width=790, height=400)

        if st.session_state["damage_curve"]:  # add under this line damage curve
            # make damage curve
            fig_damage_curve = make_damage_curve(
                damage_curve, df_colors_landuse, caption_hazard_map, invert
            )

            st.plotly_chart(fig_damage_curve, use_container_width=True)

        if st.session_state[
            "land_use"
        ]:  # add under this line land use and population maps
            # st.header("Step 3: Land use and population")

            # Display the first WMS map
            st.subheader("Landuse map")

            landuse_layer = format_wms(monre_lulc_name, monre_lulc_layer, landuse_style)

            landuse_map = make_landuse_map(
                landuse_layer,
                location_landuse,
                df_colors_landuse.index.tolist(),
                df_colors_landuse["colors"].tolist(),
            )

            landuse_map.to_streamlit(height=400)

        if st.session_state[
            "calculate_damage"
        ]:  # add under this line the table with damages per land use class
            # create new scenario
            if selected_scenario is not None:

                #Before calculating damage all the scenarios need to be patched
                scenario_data = scenario_list[scenario_list['name'] == selected_scenario].iloc[0]
                scenario_uuid = scenario_data['uuid']
                projection = scenario_data['projection']
                new_scenario = create_lizard_scenario(hazard_type,scenario_uuid,total_damage, resi_damage, agri_damage, com_damage, indu_damage,infra_damage,trans_damage)
            
        

            # make damage map
            layer_damage = format_wms(
                "damage", new_scenario["total"]["wms_info"], damage_style_drought
            )
            vmin_damage_f = 0
            vmax_damage_f = 100

            caption_damage_f = "Damage costs (VND/m2)"
            # Create
            folium_map_damage = make_map(
                layer_damage,
                location_drought,
                bbox_drought,
                colors_damage,
                vmin_damage_f,
                vmax_damage_f,
                caption_damage_f,
            )

            # damage statistics - table

            df_damage1 = calculate_total_damage_per_landuse(new_scenario['total']['url'], new_scenario['residential']['url'], new_scenario['agricultural']['url'], new_scenario['commercial']['url'], new_scenario['industrial']['url'], new_scenario['infrastructure']['url'], new_scenario['transportation']['url'], lizard_headers, pixel_size_drought, total_damage, projection)

            fig_damage_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_damage1[["Land use",r"Damage costs (VND) "]]),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_damage1["Land use"], df_damage1[r"Damage costs (VND) "]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])

            

            # damage statistics - pie chart
            df_damage_without_total = df_damage1[:-1]
            fig_damage_pie = px.pie(
                df_damage_without_total,
                values="Damage costs (VND)",
                names="Land use",
                color="Land use",
                color_discrete_map={
                    "Residential": df_colors_landuse.colors["Residential"],
                    "Agricultural": df_colors_landuse.colors["Agriculture"],
                    "Commercial": df_colors_landuse.colors["Commercial"],
                    "Industrial": df_colors_landuse.colors["Industrial"],
                    "Infrastructure": df_colors_landuse.colors["Infrastructure"],
                    "Transport": df_colors_landuse.colors["Transport"],
                },
            )

            # affected people - map
            affected_new = create_affected_breakdown(new_scenario["total"]["uuid"])
            layer_affected = format_wms(
                " people", affected_new["total_affected"]["wms_info"], displaced_style
            )

            # ap = affected people
            # colors_ap_f = df_colors_ap['colors'].tolist() # dit nog aanpassen, waarschijnlijk defineren in constants
            vmin_ap_f = 0
            vmax_ap_f = 1000

            caption_ap_f = "Affecteded people (people/km2)"

            folium_map_ap = make_map(
                layer_affected,
                location_drought,
                bbox_drought,
                colors_ap,
                vmin_ap_f,
                vmax_ap_f,
                caption_ap_f,
            )

            # make affected people table

            df_ap = calculate_total_ap_per_breakdown(affected_new['total_affected']['url'], affected_new['men_affected']['url'], affected_new['women_affected']['url'], 
                                                     affected_new['youth_affected']['url'], affected_new['children_affected']['url'], lizard_headers, pixel_size, total_damage, projection)
            
        
            fig_ap_costs = go.Figure(data=[go.Table(
                    header=dict(values=list(df_ap.columns),
                                fill_color='#859C79',
                                align='center',
                                font=dict(color='white', size=16),
                                height=35),
                    cells=dict(values=[df_ap["Population group"], df_ap["Number of affected people"]],
                               fill_color='#F0F2F6',
                               align=['center', 'right'],
                               font=dict(color='black', size=14,),
                               height=30))
                ])
        
        

            if "damage_map" not in st.session_state:  # 5 = damage map
                st.session_state["damage_map"] = True

            if "damage_statistics" not in st.session_state:  # 6 = damage statistics
                st.session_state["damage_statistics"] = False

            if (
                "affected_people" not in st.session_state
            ):  # 7 = affected people map and statistics
                st.session_state["affected_people"] = False

            if "download_results" not in st.session_state:  # 8 = download results
                st.session_state["download_results"] = False

            col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
            with col1:
                if st.button("Damage Map", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_map"] = not st.session_state["damage_map"]
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col2:
                if st.button("Damage Statistics", use_container_width=True):
                    # toggle calculate_damage session state
                    st.session_state["damage_statistics"] = not st.session_state[
                        "damage_statistics"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col3:
                if st.button(
                    "Affected people Map and Statistics", use_container_width=True
                ):
                    # toggle calculate_damage session state
                    st.session_state["affected_people"] = not st.session_state[
                        "affected_people"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["download_results"] = False
                    st.session_state["calculate_damage"] = True

            with col4:
                if st.button("Download results", use_container_width=True):
                    st.session_state["download_results"] = not st.session_state[
                        "download_results"
                    ]
                    st.session_state["damage_map"] = False
                    st.session_state["damage_statistics"] = False
                    st.session_state["affected_people"] = False
                    st.session_state["calculate_damage"] = True

            if st.session_state["damage_map"]:
                st.subheader("Calculated Damage Map")

                st_data_damage = st_folium(folium_map_damage, height=500, width=900)

            if st.session_state["damage_statistics"]:
                st.subheader("Damage Statistics")
                col1, col2 = st.columns([1, 2])

                with col1:

                    st.plotly_chart(
                        fig_damage_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    # Pie chart, where the slices will be ordered and plotted counter-clockwise:

                    st.plotly_chart(fig_damage_pie, theme=None)

            if st.session_state["affected_people"]:
                st.subheader("Affected people Map")
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.plotly_chart(
                        fig_ap_costs, theme="streamlit", use_container_width=True
                    )

                with col2:
                    st_data_damage = st_folium(folium_map_ap, width=670, height=400)

            if st.session_state["download_results"]:
                st.write("press this button to download all tables and charts")

                html_fig1 = fig_damage_costs.to_html(full_html=False)
                html_fig2 = fig_damage_pie.to_html(full_html=False)
                html_fig3 = fig_ap_costs.to_html(full_html=False)

                # Convert Folium map to HTML
                map_damage_html = folium_map_damage._repr_html_()
                map_ap_html = folium_map_ap._repr_html_()

                # Create HTML string incorporating Plotly figures
                your_html_string = f"""
                <html>
                <head>
                    <title>MKDC DSS6</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                </head>
                <body>
                    <h1>MKDC DSS6 Forecast Damage costs and Affected people</h1>
                    <div>
                        <h3>Hazard:</h3><p>{selected}</p>
                        <h3>Scenario:</h3><p>{selected_scenario}</p>
                    </div>
                    <div>
                        <h2>Damage costs map</h2>
                        {map_damage_html}
                    </div>
                    <div>
                        <h2>Damage cost table</h2>
                        {html_fig1}
                    </div>
                    <div>
                        <h2>Damage costs pie</h2>
                        {html_fig2}
                    </div>
                    <div>
                        <h2>Affected people map</h2>
                        {map_ap_html}
                    </div>
                    <div>
                        <h2>Affected people statistics</h2>
                        {html_fig3}
                    </div>
                </body>
                </html>
                """

                # Display download button
                download_html(your_html_string)


# else:
#   st.write("Not working yet")
