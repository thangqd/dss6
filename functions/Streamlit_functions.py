# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:09:28 2023

@author: esther.vanderlaan

modified: thangqd
"""

# Import packages
import plotly.graph_objects as go
import leafmap.foliumap as leafmap
import folium
import branca.colormap as cm
from streamlit_option_menu import option_menu
import streamlit as st
from folium.plugins import Fullscreen


# Streamlit functions
def streamlit_menu(example=3):
    if example == 1:
        # 1. as sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",  # required
                options=["Home", "Projects", "Contact"],  # required
                icons=["house", "book", "envelope"],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if example == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=["Home", "Projects", "Contact"],  # required
            icons=["house", "book", "envelope"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if example == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=[
                "Floods",
                "Drought",
                "Saline intrusion",
                "Landslide",
            ],  # required
            icons=["tsunami", "sun", "water", "cone-striped"],  # optional
            # menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "#fafafa",
                },
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "20px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {
                    "background-color": "#c7e0ba",
                    "color": "black",
                },
            },
        )
        return selected




def make_map(layer, location, bbox, colors, vmin, vmax, caption):
    folium_map = folium.Map(
        location=location,
        #zoom_start=11.4,
        tiles="CartoDB positron",
    )
    Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(folium_map)
        
    folium_map.fit_bounds(bbox)
    
    folium.raster_layers.WmsTileLayer(
        url=layer["url"],
        name=layer["name"],
        format="image/png",
        layers=layer["layers"],
        transparent=False,
        overlay=True,
        opacity=0.95,
        styles=layer["styles"],
        show=True,
        control=True,
    ).add_to(folium_map)
    
    # voeg nog color layer toe - in file constants
    colormap = cm.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax,
        caption=caption,
    )
    colormap.add_to(folium_map)
    
    return folium_map


def make_damage_curve(df_damage_curve ,df_colors_landuse,xaxis_title,invert):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Residential"],
            name="Residential damage",
            line=dict(color=df_colors_landuse.colors['Residential'], width=1), # selects correct color from dataframe with land uses and colors
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Agriculture"],
            name="Agricultural damage",
            line=dict(color=df_colors_landuse.colors['Agriculture'], width=1), 
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Commercial"],
            name="Commercial damage",
            line=dict(color=df_colors_landuse.colors['Commercial'], width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Industrial"],
            name="Industrial damage",
            line=dict(color=df_colors_landuse.colors['Industrial'], width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Infrastructure"],
            name="Infrastructural damage",
            line=dict(color=df_colors_landuse.colors['Infrastructure'], width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_damage_curve.iloc[:,0],
            y=df_damage_curve["Transport"],
            name="Transport damage",
            line=dict(color=df_colors_landuse.colors['Transport'], width=1),
        )
    )

    fig.update_layout(
        title="Damage curves per land use",
        xaxis_title=xaxis_title,
        yaxis_title="Damage (VND/m2)",
    )
    
    if invert:
        fig.update_layout(xaxis=dict(autorange="reversed"))
    
    return fig


def make_landuse_map(layer, location, labels, colors):
    st.write(layer["url"])
    st.write(layer["layers"])
    st.write(layer["styles"])
    m = leafmap.Map(
        center=location,
        zoom=10,
        draw_control=False,
        measure_control=False,
        fullscreen_control=False,
        attribution_control=True,
        tiles="CartoDB positron",
    )

    Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)
        


    # folium_map_lucl = folium.Map(location=[lat, lon], zoom_start=10)
    folium_map_lucl = folium.raster_layers.WmsTileLayer(
        url=layer["url"],
        name=layer["name"],
        format="image/png",
        layers=layer["layers"],
        transparent=True,
        overlay=True,
        opacity=0.95,
        styles=layer["styles"],
        show=True,
        control=True,
    )

    folium_map_lucl.add_to(m)


    m.add_legend(
        title="Legend", labels=labels, colors=colors
    )
    
    return m


# function to make html file and download it
def download_html(html_string, filename='download.html'):
    # Convert string to bytes
    html_bytes = html_string.encode('utf-8')
    # Create a download link
    st.download_button(
        label="Download HTML",
        data=html_bytes,
        file_name=filename,
        mime='text/html'
    )

