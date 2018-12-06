# -*- coding: utf-8 -*-
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
    device_dist = (linestring.length)/days
    line_string_op = transform(project_mercator,linestring)
    linestring_op = geopandas.GeoSeries(linestring_op)
    #gdf_buffer['name'] = 'Main Equipment'
    linestring_gdf = geopandas.GeoDataFrame(geopandas.GeoSeries(linestring_op),crs={'init': 'epsg:4326'})
    linestring_gdf = gdf_buffer.rename(columns={0:'geometry'}).set_geometry('geometry')
    linestring_gdf.to_file(driver = 'ESRI Shapefile', filename= r"D:\intern_exam\invento_labs\results\linestring_{0}.shp".format(item))
    """
    df_plot = df_plot.append({
     "Device_ID": device_id,
     "Distance_covered":  device_dist,
    "TimeON": df_time,
        "daysLogged": days
      }, ignore_index=True)
    
    
    
    df_gpd = geopandas.GeoDataFrame(df_item, geometry=geometry)
    
    # main equipment location coordinates
    lat_center,lon_center = 28.09029007,77.33970642
    main_eqpmnt = Point(lon_center,lat_center)
    
    main_eqpmnt = transform(project,main_eqpmnt)
    buffer = main_eqpmnt.buffer(100)
    
    project_mercator = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:32643'), # source coordinate system
    pyproj.Proj(init='epsg:4326'))
    
    buffer_mercator = transform(project_mercator,buffer)
    
    #print (buffer)
    #buffer = transform(project, buffer)
    lat = []
    lon = []
    for x,y in buffer_mercator.exterior.coords:
        print(x,y)
        lat.append(y)
        lon.append(x)
    #buffer = Polygon(zip(lat, lon))
    # Edit: Following Tim C's comment below, this line sets geometry for resulting geodataframe
    #buffer = transform(project, buffer)
    gdf_buffer = geopandas.GeoSeries(buffer_mercator)
    #gdf_buffer['name'] = 'Main Equipment'
    gdf_buffer = geopandas.GeoDataFrame(geopandas.GeoSeries(gdf_buffer),crs={'init': 'epsg:4326'})
    gdf_buffer = gdf_buffer.rename(columns={0:'geometry'}).set_geometry('geometry')
    gdf_buffer.to_file(driver = 'ESRI Shapefile', filename= r"D:\intern_exam\invento_labs\results\result{0}_{1}.shp".format(9999,999))
    #gdf_buffer['geometry'] = gdf_buffer['geometry'].to_crs(epsg=4326)
    
    for index, row in (df_item.iterrows()):
        
        point = Point(row['longitude_gps'],row['latitude_gps'])
        point = transform(project,point)
        #print (point)
        #point = transform(project_mercator,point)
        #if point.within(buffer) == True:
        #print ("point is in buffer")
        #time.sleep(1)
        
        day = row['date'].day
        hour = row['date'].hour
        minute = row['date'].minute
        if (hour == start_hour ) & (minute <= end_minute) :
            
            if day_prev == 0:
                df_daywise_devices = df_daywise_devices.append(df_item.loc[index], ignore_index=False)
                day_prev = day
            
            elif day == day_prev :
                df_daywise_devices = df_daywise_devices.append(df_item.loc[index], ignore_index=False)
                day_prev = day
        
            elif day> day_prev:
                lat_bok = []
                lon_bok = []
                
                #p_df = df_daywise_devices
                
                
                
                
                p_df = GeoDataFrame(df_daywise_devices, geometry ='geometry',crs={'init': 'epsg:4326'} )
                
                p_df = p_df[['device_id_x','device_time_stamp','geometry']]
                p_df['device_time_stamp'] = p_df['device_time_stamp'].astype(str)
                p_df.dropna(inplace=True)
                
                #p_df.to_file(driver = 'ESRI Shapefile', filename= r"D:\intern_exam\invento_labs\results\result_{0}_{1}.shp".format(item,day))
                
                """
                """
                index_list = [x for x in p_df.index]
                for i in range(0,len(p_df)):
                    
                    
                    
                    row = p_df.iloc[i]
                    d_id_x = row[0]
                    d_ts = row[1]
                    d_geom = row[2]
                    df_point = pd.DataFrame([[d_id_x,d_ts,d_geom]],columns=[x for x in p_df.columns])
                    
                    
                    #row_df = pd.DataFrame(data=row.T,columns=p_df.columns)
                    #print (row_df)
                    
                    
                    point_shp = df_point
                    #x = row[index:index+1]
                    
                    #point_shp = x 
                    
                    #point_shp = pd.DataFrame(point_shp,columns=p_df.columns)
                    
                    point_shp2 = geopandas.GeoDataFrame(point_shp,geometry='geometry', crs={'init': 'epsg:4326'})
                    
                # save the GeoDataFrame
                    point_shp2.to_file(driver = 'ESRI Shapefile', filename= r"D:\intern_exam\invento_labs\results\result_{0}_{1}_{2}.shp".format(item,day,i))
                    """
               # or directly
               #gdf.to_file("result2.shp"
                
                
                
               

                
                
                
                
                
                
                
"""                  
            
        else:
            print ("not in range")
        
        #else:
            #print ("point not in geofence")
                   
                    
                    
           
            
    
   #print ("Device ID: {0},     Device Time Stamps: {1},     Device distance travelled: {2} metres".format(df_item['device_id_x'].unique(),df_item['device_time_stamp'].unique(),linestring.length))

plt.figure(figsize=(20,10))
df_plot_time = df_plot[['TimeON','Device_ID']]
df_plot_time.set_index('Device_ID',inplace=True)

df_plot_dist = df_plot[['Distance_covered','Device_ID']]
df_plot_dist.set_index('Device_ID',inplace=True)

df_plot_time.plot(kind="bar", title="Invento Labs",figsize=(15,7.5))
df_plot_dist.plot(kind="bar", title="Invento Labs",figsize=(15,7.5))
plt.show()
"""