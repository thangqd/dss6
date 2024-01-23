# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:19:46 2023

@author: esther.vanderlaan

modifide: thangqd
"""

# Import packages
import pandas as pd


# Constants

monre_lulc = '67cc7ab8-f63b-4a0e-9e68-cfe9ad046eb4'
monre_lulc_name = 'MONRE LULC DSS6'
monre_lulc_layer = 'mkdc-projectteam:monre-lulc-dss-5'

# raster url's of damage maps (total and per landuse) - 
#Flood
total_url = "https://vietnam.lizard.net/api/v4/rasters/11c27acc-c031-497f-b48d-0c4d3a7ffda6/"      # Total
agri_url  = 'https://vietnam.lizard.net/api/v4/rasters/b1e04069-cf8f-4096-adbb-6a40da630093/'      # Agriculture
trans_url = 'https://vietnam.lizard.net/api/v4/rasters/757fa00b-8f53-48ef-9c09-4e37c67e3de8/'      # Transport
resi_url  = 'https://vietnam.lizard.net/api/v4/rasters/050c6657-2605-4545-a4b1-d2b9bf19172d/'      # Residential
infra_url = 'https://vietnam.lizard.net/api/v4/rasters/5b3f3af0-46d5-4367-984b-cdf608f2b145/'      # Infrastructure
indu_url  = 'https://vietnam.lizard.net/api/v4/rasters/c731f0b2-a587-4869-b37c-d8e08d88578e/'      # Industrial
com_url   = 'https://vietnam.lizard.net/api/v4/rasters/4cf2119d-78c9-4dea-9d41-3fbca8eff691/'      # Commercial

# raster url for affected people
affected_url  = 'https://vietnam.lizard.net/api/v4/rasters/f25e55f8-ea98-45a4-9cd5-7f68da6d7b2f/'
pop_all = '16171a5f-be38-4287-a8e1-4acb0c6b4879'
pop_men = '64354ad1-60b9-4c0c-b33a-f64286211f08'
pop_women = 'd3d1fc0d-b575-447e-9f84-55cbffe56bef'
pop_youth =  'ef341298-a96c-4851-966e-3f0ab08ca3e1'
pop_child = 'e246332a-e4fe-4c50-9f8f-403e0306e90c'

#Drought
total_drought_url  = "https://vietnam.lizard.net/api/v4/rasters/acd46b2f-a0b6-4925-a48f-f9e6de5a2ed6/" 
agri_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/396fec8d-c161-4d78-9583-b63a92fa9e01/" 
trans_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/c4dd45cb-5ef4-431c-a3aa-5576130d24b2/" 
resi_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/b2715131-17d0-4bea-ae16-00d495c71703/" 
infra_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/6f6166f4-edf7-4f11-8b80-ebd4e978d100/" 
indu_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/cce09b13-a8f2-4caa-a688-2a289023dc4a/" 
com_drought_url =  "https://vietnam.lizard.net/api/v4/rasters/4a4fc13a-fca1-4847-8a6c-bb5f280ccb3b/" 

#Salt Intrustion
total_salt_url  = "https://vietnam.lizard.net/api/v4/rasters/d3b7bdc7-32fb-4c2b-88bd-8093edd220e1/" 
agri_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/80c97a5a-cbd1-4096-b3da-c0c9d317a84f/" 
trans_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/ee987d30-43cd-4b22-b95c-a2c32fa63438/" 
resi_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/73c22028-2fa2-442b-8bd0-36c3657f76cc/" 
infra_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/a469d5dd-264f-4b77-8994-153a30ec0bb2/" 
indu_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/7362d292-3217-4d1b-987a-aee7b73d5e6d/" 
com_salt_url =  "https://vietnam.lizard.net/api/v4/rasters/743a1300-4a58-41f2-a0d0-526648293ea6/" 

#Landslide
total_slide_url  = "https://vietnam.lizard.net/api/v4/rasters/d0cfd2e7-0af3-4b04-9e30-b9af1509d162/" 
agri_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/637c0a12-c4e9-405f-9c5f-64ea3949cad6/" 
trans_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/637c0a12-c4e9-405f-9c5f-64ea3949cad6/" 
resi_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/637c0a12-c4e9-405f-9c5f-64ea3949cad6/" 
infra_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/ef2dbca1-b83d-44cf-a885-6e307b94aeb0/" 
indu_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/90883538-46e9-4ed3-a5c6-45cd96a83465/" 
com_slide_url =  "https://vietnam.lizard.net/api/v4/rasters/90883538-46e9-4ed3-a5c6-45cd96a83465/" 

# latitude and longitude of place of interest
lat = "10.12"
lon = "105.73"

location = [lat, lon]
location_landuse = (lat, lon)


#Styles 
flood_style = '3di-depth'
drought_style = 'RedWhiBlu:-2:2'
slide_style = 'RdYlGn_r:1:6'
salt_slide = "RdBu:-3:3"
insaline_style = 'RdBu:-3:3'
landslide_style = 'RdYlGn_r:1:6'
damage_style = '3di-damage-estim:0:1000000'
displaced_style = 'CMRmap_r:0:1000'
damage_style_drought = '3di-damage-estim:0:100'
landuse_style = 'mkdc-lulc'

# create dataframe with colors for each landuse map
labels_landuse = [
    "Agriculture",
    "Commercial",
    "Industrial",
    "Residential",
    "Infrastructure",
    "Transport",
    "Water",
    "Other",
    ]

colors_landuse = [
    "#FFFF64",
    "#FFB432",
    "#3291A8",
    "#C31400",
    "#5C1F4D",
    "#15520C",
    "#1634F7",
    "#DCDCDC",
    ]

dict_colors_landuse = {"labels": labels_landuse, 
                       'colors': colors_landuse}
df_colors_landuse = pd.DataFrame.from_dict(dict_colors_landuse)
df_colors_landuse = df_colors_landuse.set_index('labels')

# urls for colormaps of each hazard and damage and affected people (ap)
url_colormap_drought   = 'https://demo.lizard.net/api/v4/colormaps/RedWhiBlu/'
url_colormap_flood     = 'https://demo.lizard.net/api/v4/colormaps/3di-depth/'
url_colormap_insaline  = 'https://demo.lizard.net/api/v4/colormaps/RdBu/'
url_colormap_landslide = 'https://demo.lizard.net/api/v4/colormaps/RdYlGn_r/'
url_colormaps_ap       = 'https://demo.lizard.net/api/v4/colormaps/CMRmap_r/'
url_colormaps_damage   = 'https://demo.lizard.net/api/v4/colormaps/3di-damage-estim/'

# constants for calculating statistics
pixel_size = 10
pixel_size_drought = 40 