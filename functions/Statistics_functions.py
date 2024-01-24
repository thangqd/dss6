# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:12:09 2023

@author: esther.vanderlaan

modified: thangqd
"""

# import packages
import streamlit as st
import pandas as pd
import requests
from shapely import geometry
import os


lizard_headers = {
    "username": os.environ["USERNAME"],
    "password": os.environ["PASSWORD"],
    # "username": '__key__',
    # "password": 'dHrkmkoz.aeLBK4c0wW0z2OIQWmqWF9QajHARwDQQ',
    "Content-Type": "application/json",
}

# Statistics functions
def define_bbox(raster_url, lizard_headers):

    damage_raster = requests.get(raster_url, headers=lizard_headers)
    result = damage_raster.json()
    xmin = result["spatial_bounds"]["west"]
    ymin = result["spatial_bounds"]["south"]
    xmax = result["spatial_bounds"]["east"]
    ymax1 = result["spatial_bounds"]["north"]
    
    # define a y half way to split the polygon
    dif_y = ymax1-ymin
    ymax2 = ymin + (dif_y/2)
    
    
    # ymax1 = most north located boundary and ymax2 is located half way of total polygon
    poly_south = geometry.Polygon(
        ((xmin, ymin), (xmin, ymax2), (xmax, ymax2), (xmax, ymin))
    )
    
    poly_north = geometry.Polygon(
        ((xmin, ymax2), (xmin, ymax1), (xmax, ymax1), (xmax, ymax2))
    )

    return poly_south, poly_north

def define_coordinates_maps(raster_url, lizard_headers):
    
    damage_raster = requests.get(raster_url, headers=lizard_headers)
    result = damage_raster.json()
    xmin = result["spatial_bounds"]["west"]
    ymin = result["spatial_bounds"]["south"]
    xmax = result["spatial_bounds"]["east"]
    ymax1 = result["spatial_bounds"]["north"]
    
    # define a y half way to split the polygon
    dif_y = ymax1-ymin
    ymax2 = ymin + (dif_y/2)
    
    # define a y half way to split the polygon
    dif_x = xmax-xmin
    xmax2 = xmin + (dif_x/2)
    
    # middle location
    location = [ymax2, xmax2]
    
    # coordinates to formulate bbox in maps
    # southwest coordinates
    sw_cor = [ymin, xmin]
    
    # northeast coordinates
    ne_cor = [ymax1, xmax]
    
    bbox = [sw_cor, ne_cor]
    
    return location, bbox





def get_zonal_sum(template_url, lizard_headers, poly_wkt, pixel_size, projection):
    # used to calculate total damage in area

    params = {
        "geom": poly_wkt,
        "zonal_statistic": "sum",
        "zonal_projection": "EPSG:32648", #Always run in local Vietnamese projection to get pixels in m
        "pixel_size": pixel_size
    }

    params = {key: value for key, value in params.items() if value is not None}

    zonal_request_url = template_url + "zonal"
    zonal_request = requests.get(
        zonal_request_url, params=params, headers=lizard_headers
    )

    try:
        zonal_value = zonal_request.json()["results"][0]["value"]
    except:
        zonal_value = 0

    return zonal_value


def get_total_sum(template_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection):
    #bbox_south, bbox_north = define_bbox(template_url, lizard_headers)
    zonal_sum_south = get_zonal_sum(template_url, lizard_headers, bbox_south, pixel_size, projection)
    zonal_sum_north = get_zonal_sum(template_url, lizard_headers, bbox_north, pixel_size, projection)
    total_sum = zonal_sum_north + zonal_sum_south
    
    return total_sum

@st.cache_data(show_spinner="Calculating damage costs...")
def calculate_total_damage_per_landuse(total_url, resi_url, agri_url, com_url, indu_url, infra_url, trans_url, lizard_headers, pixel_size, total_damage, projection):
    # calculate damage statistics
     # should be 10 because that is the smallest pixel size of land use and flooding map
    bbox_south, bbox_north = define_bbox(total_url, lizard_headers)
    
    total_sum = get_total_sum(total_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    resi_sum  = get_total_sum(resi_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    agri_sum  = get_total_sum(agri_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    com_sum   = get_total_sum(com_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection) 
    indu_sum  = get_total_sum(indu_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    infra_sum = get_total_sum(infra_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    trans_sum = get_total_sum(trans_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection) 
    
    list_of_landuses = [  
                        "Residential",
                        "Agricultural",
                        "Commercial",
                        "Industrial",
                        "Infrastructure",
                        "Transport",
                        '<b>TOTAL</b>'
                          ]
    
    #Calculate damages
    damages = [resi_sum, agri_sum, com_sum, indu_sum, infra_sum, trans_sum, total_sum]
    #Values are in VND/m2, now recalculate to VND using pixel size
    damages = [pixel_size*pixel_size*d for d in damages]

        
    dict_data_landuse_statistics = {'Land use': list_of_landuses,
                 'Damage costs (VND)': damages}
    
    
    df_damage = pd.DataFrame(dict_data_landuse_statistics)
    df_damage[r"Damage costs (VND) "] = (df_damage.iloc[:,1] / 1e6).round(0)
    df_damage[r"Damage costs (VND) "] = df_damage[r"Damage costs (VND) "].astype(str) + " mil"
    df_damage.loc[df_damage.index[-1], r"Damage costs (VND) "] = '<b>'+str(df_damage.loc[df_damage.index[-1], r"Damage costs (VND) "])+'</b>'

    return df_damage


@st.cache_data(show_spinner="Calculating amount of affected people...")
def calculate_total_ap_per_breakdown(total_url, men_url, woman_url, youth_url, childeren_url, lizard_headers, pixel_size,  total_damage, projection):
    # calculate damage statistics
     # should be 10 because that is the smallest pixel size of land use and flooding map
    bbox_south, bbox_north = define_bbox(total_damage, lizard_headers)
    
    total_sum = get_total_sum(total_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    men_sum  = get_total_sum(men_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    woman_sum  = get_total_sum(woman_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)
    youth_sum   = get_total_sum(youth_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection) 
    childeren_sum  = get_total_sum(childeren_url, lizard_headers, pixel_size, bbox_south, bbox_north, projection)

    #men, women and youth are in another unit, so apply extra correction
    men_sum = men_sum/1111.11111
    woman_sum = woman_sum/1111.11111
    youth_sum = youth_sum/1111.11111

    list_of_groups = [  
                        "Men",
                        "Women",
                        "Youth",
                        "Children",
                        '<b>TOTAL</b>'
                          ]
    
    affected_people = [men_sum, woman_sum, youth_sum, childeren_sum, total_sum]
    #Values are in people/km2, now recalculate to total people using pixel size
    affected_people = [int(pixel_size*pixel_size*p/1000/1000) for p in affected_people]

    dict_data_ap_statistics = {'Population group': list_of_groups,
                 'Number of affected people': affected_people}
    
    df_damage = pd.DataFrame(dict_data_ap_statistics)
    df_damage['Number of affected people'] = df_damage['Number of affected people'].astype(str)
    df_damage.loc[df_damage.index[-1],'Number of affected people'] = '<b>'+str(df_damage.loc[df_damage.index[-1], 'Number of affected people'])+'</b>'
    
    return df_damage


