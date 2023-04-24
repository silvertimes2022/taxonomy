import numpy as np
import pandas as pd
import geopandas as gpd

# path2 = "test1.gpkg"
layer = "buildings"
path3 = "test2.gpkg"
buildings = gpd.read_file('buildings1128.shp')
buildings=buildings.loc[:,['Elevation','材质大','geometry']]
buildings['木']=0
buildings.loc[buildings['材质大']=='木','木']=1
buildings['涂料']=0
buildings.loc[buildings['材质大']=='涂料','涂料']=1
buildings['红砖']=0
buildings.loc[buildings['材质大']=='红砖','红砖']=1
buildings['金属']=0
buildings.loc[buildings['材质大']=='金属','金属']=1
buildings['面砖']=0
buildings.loc[buildings['材质大']=='面砖','面砖']=1
buildings['玻璃']=0
buildings.loc[buildings['材质大']=='玻璃','玻璃']=1
buildings['青砖']=0
buildings.loc[buildings['材质大']=='青砖','青砖']=1
buildings=buildings.drop(['材质大'],axis=1)
buildings=buildings.rename({'Elevation':'height'},axis=1)
# buildings2['geometry']=buildings2.envelope



print(1)