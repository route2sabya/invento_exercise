# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 01:35:08 2018

@author: WELCOME
"""


"""
Created on Tue Dec  4 19:53:51 2018

@author: WELCOME
"""
import pandas as pd
import numpy as np
import geopandas
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, save
from bokeh.tile_providers import CARTODBPOSITRON
import time
import folium


#from shapely.wkt import loads

df = pd.read_csv(r"D:\intern_exam\invento_labs\DIP.csv",low_memory=False,parse_dates=['device_time_stamp'])
#print (df.columns)
cols = [x for x in df.columns]

df['latitude_gps'].value_counts()

#print (df.head(10))
df.dropna(inplace=True)

unique_device_ids = [ udid for udid in df.device_id_x.unique()]
#print (len(unique_device_ids))
df_daywise_devices = pd.DataFrame(columns=df.columns)   
start_hour = 9
start_minute = 0
end_hour = 9
end_minute = 10

day_prev = 0
# df_analysis = df.groupby(['device_id_x'])['geometry'].apply(lambda x: LineString(x.tolist()) if x.size > 1 else x.tolist())
counter = 0
coords = []

df_plot = pd.DataFrame(columns=["Device_ID", "Distance_covered","TimeON","daysLogged"])

for item in unique_device_ids:
    
      
    #item = str(item)
    df_item = pd.DataFrame()
    df_item_update = pd.DataFrame()
    df_item = df.loc[df['device_id_x'] == item]
    
    
    #print ("Deleting {0} rows because longitude_gps had 0 values".format(len(df_item[df_item['longitude_gps'] == '0'])))
    df_item = df_item.loc[df['latitude_gps'] != '0']
    df_item = df_item.loc[df_item['longitude_gps'] != 0]
    df_item = df_item.loc[df['latitude_gps'] != 'a']
    df_item = df_item.loc[df_item['longitude_gps'] != 'a']
    df_item = df_item.loc[df['latitude_gps'] != 'latitude_gps']
    df_item = df_item.loc[df_item['longitude_gps'] != 'longitude_gps']
    df_item = df_item.loc[df_item['device_time_stamp'] != 'device_time_stamp']
    df_item.dropna(axis=0,subset=['device_id_x','device_time_stamp'],inplace=True)
    #df_item.dropna(subset=['device_time_stamp'],inplace=True)
    
    df_item['latitude_gps'] = df_item['latitude_gps'].str.strip("'")
    df_item['longitude_gps'] = df_item['longitude_gps'].str.strip("'")
    
    df_item['latitude_gps'] = df_item['latitude_gps'].astype(float)
    df_item['longitude_gps'] = df_item['longitude_gps'].astype(float)
    df_item.sort_values(by=['device_time_stamp'])
    
    df_item['date']  = pd.to_datetime(df_item['device_time_stamp'])
    from shapely.geometry import Point

    # combine lat and lon column to a shapely Point() object
    geometry = [Point(xy) for xy in zip(df_item.longitude_gps,df_item.latitude_gps)]
    
    df_item['device_time_stamp'] = df_item['device_time_stamp'].astype(str)
    df_item['geometry'] = geometry
    df_daywise_devices = pd.DataFrame(columns=df_item.columns) 
    
    #print (df_item['date'].max(),df_item['date'].min())
    
    dtype_df = df_item['date'].dtype
    #if dtype_df == NaT
    #print (dtype_df)
    max_date =  (df_item['date'].max()) # .str.split('/')[1])
    
    min_date = (df_item['date'].min())#.str.split('/')[1])
    days = (max_date - min_date).days
    if days == 0:
        days = 1
    #print (days)
    
    

    df_time = (df_item['track_num1'].astype(int).sum())/3600
    from functools import partial
    import pyproj
    from shapely.ops import transform

    project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'), # source coordinate system
    pyproj.Proj(init='epsg:32643')) # destination coordinate system

    
    
    for i, rowl in df_item.iterrows():
        coords.append((rowl['longitude_gps'], rowl['latitude_gps']))
    linestring = LineString(coords)
    linestring = transform(project, linestring)  # apply projection
    
    for id in df_item['device_id_x'].unique():
        device_id = str(id).strip()
    
    if device_id is not None:
        device_id = device_id
    else:
        device_id = counter
    counter = counter + 1
    
    
    project_mercator = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:32643'), # source coordinate system
    pyproj.Proj(init='epsg:4326'))
    device_dist = (linestring.length)/days
    linestring_op = transform(project_mercator,linestring)
    linestring_op = geopandas.GeoSeries(linestring_op)
    #gdf_buffer['name'] = 'Main Equipment'
    linestring_gdf = geopandas.GeoDataFrame(geopandas.GeoSeries(linestring_op),crs={'init': 'epsg:4326'})
    linestring_gdf = linestring_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')
    linestring_gdf.to_file(driver = 'ESRI Shapefile', filename= r"D:\intern_exam\invento_labs\results\linestring_{0}.shp".format(item))