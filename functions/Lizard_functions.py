# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 09:36:42 2023
@author: Kizje.Marif
Modified: thangqd
"""

import pandas as pd
import requests
import streamlit as st
import os
from input.Constants import *


HEADERS = {
    "username": os.environ["USERNAME"],
    "password": os.environ["PASSWORD"],
    # "username": '__key__',
    # "password": 'dHrkmkoz.aeLBK4c0wW0z2OIQWmqWF9QajHARwDQQ',
    "Content-Type": "application/json",
}

def generate_scenario(
    hazard,
    template_url,
    uuid
):
    
    json = {hazard: uuid}
    params = {
        "parameters": {key: value for key, value in json.items() if value is not None}
    }

    r = requests.post(url=template_url, json=params, headers=HEADERS)
    results = r.json()
    damage_map = results["wms_info"]["layer"]
    damage_url = results["url"]
    damage_uuid = results["uuid"]

    return damage_map, damage_url, damage_uuid


def generate_displaced(
    template_url,
    population_uuid,
    damage_uuid
):

    
    json = {"damage_map": damage_uuid, 'population_map':population_uuid}
    params = {
        "parameters": {key: value for key, value in json.items() if value is not None}
    }

    r = requests.post(url=template_url, json=params, headers=HEADERS)
    results = r.json()

    damage_map = results["wms_info"]["layer"]
    damage_url = results["url"]

    return damage_map, damage_url


def format_wms(name, layer,style):
    wms_layer_temp =  {
            "url": "https://demo.lizard.net/wms/verdamping/?SERVICE=WMS",
            "name": name,
            "layers": layer,
            "styles": style
          }
    return wms_layer_temp


@st.cache_data(show_spinner="Fetching data from Lizard...")
def create_affected_breakdown(uuid_scenario):
    total_affected = generate_displaced(f'{affected_url}template/',pop_all ,uuid_scenario)
    men_affected = generate_displaced(f'{affected_url}template/',pop_men ,uuid_scenario)
    women_affected = generate_displaced(f'{affected_url}template/',pop_women ,uuid_scenario)
    youth_affected = generate_displaced(f'{affected_url}template/',pop_youth ,uuid_scenario)
    children_affected = generate_displaced(f'{affected_url}template/',pop_child ,uuid_scenario)
    
    result = {
       'total_affected': {'wms_info': total_affected[0], 'url': total_affected[1]},
       'men_affected': {'wms_info': men_affected[0], 'url': men_affected[1]},
       'women_affected': {'wms_info': women_affected[0], 'url': women_affected[1]},
       'youth_affected': {'wms_info': youth_affected[0], 'url': youth_affected[1]},
       'children_affected': {'wms_info': children_affected[0], 'url': children_affected[1]}
   }

    return result

@st.cache_data(show_spinner="Fetching data from Lizard...")
def create_lizard_scenario(hazard, uuid_scenario,total_url, resi_url, agri_url, com_url, indu_url,infra_url,trans_url):

    """
    This function creates an new scenario by patching 

    Returns
    -------
    dic with new url nand wms layer.

    """
    total_damage = generate_scenario(hazard, f'{total_url}template/', uuid_scenario)
    resi_damage =  generate_scenario(hazard,f'{resi_url}template/', uuid_scenario)
    agri_damage = generate_scenario(hazard,f'{agri_url}template/', uuid_scenario)
    com_damage =  generate_scenario(hazard,f'{com_url}template/', uuid_scenario)
    indu_damage =  generate_scenario(hazard,f'{indu_url}template/', uuid_scenario)
    infra_damage =  generate_scenario(hazard,f'{infra_url}template/', uuid_scenario)
    trans_damage =  generate_scenario(hazard,f'{trans_url}template/', uuid_scenario)
    
    
    result = {
        'total': {'wms_info': total_damage[0], 'url': total_damage[1], 'uuid': total_damage[2]},
        'residential': {'wms_info': resi_damage[0], 'url': resi_damage[1], 'uuid': resi_damage[2]},
        'agricultural': {'wms_info': agri_damage[0], 'url': agri_damage[1], 'uuid': agri_damage[2]},
        'commercial': {'wms_info': com_damage[0], 'url': com_damage[1], 'uuid': com_damage[2]},
        'industrial': {'wms_info': indu_damage[0], 'url': indu_damage[1], 'uuid': indu_damage[2]},
        'infrastructure': {'wms_info': infra_damage[0], 'url': infra_damage[1], 'uuid': infra_damage[2]},
        'transportation': {'wms_info': trans_damage[0], 'url': trans_damage[1], 'uuid': trans_damage[2]}
    }
    
    return result

@st.cache_data(show_spinner= False)
def find_scenarios(observation_type_code):
    url = "https://vietnam.lizard.net/api/v4/rasters/"
    
    # Add filter for name attribute 
    params= {'observation_type__code': observation_type_code,'organisation__uuid':"905acb81-6738-46f3-b2f9-70e83b3af32a"}
    
    r = requests.get(url,headers=HEADERS, params=params)
    results = r.json()['results']
    # Retrieve the 'results' attribute using a JSON interpreter
    rasters_list = pd.DataFrame(results)
    return rasters_list

def define_color_legenda(url_colormap):
    # manually define url colormap in constants
    # labels are also defined and returned, but not also correct since there scaled 
    r = requests.get(url = url_colormap)
    results = r.json()
    data = results['definition']['data']
    
    labels =[]
    colors = []
    for i in data:
        #print(i[0])
        labels +=[int(i[0])]
        #print(i[1])
        colors += [i[1]]
        
        dict_colors = {"labels": labels, 
                               'colors': colors}
        df_colors = pd.DataFrame.from_dict(dict_colors)
        df_colors = df_colors.set_index('labels')
        
    return df_colors

