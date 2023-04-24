import warnings
import shapely
from shapely.geometry import Polygon
from factor_analyzer import calculate_kmo,FactorAnalyzer
import geopandas as gpd
import libpysal
import mapclassify
import matplotlib.pyplot as plt
import momepy as mm
import numpy as np
import math
import pandas as pd
import scipy as sp
import scipy.spatial.distance
import seaborn as sns
import factor_analyzer
from factor_analyzer.factor_analyzer import calculate_kmo,calculate_bartlett_sphericity
from tqdm.auto import tqdm
from sklearn import preprocessing
from sklearn.cluster import KMeans,DBSCAN,SpectralClustering
from sklearn.mixture import GaussianMixture
from scipy.cluster import hierarchy
from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
# we are using bleeding edge software that emits some warnings irrelevant for the current runtime
warnings.filterwarnings('ignore', message='.*initial implementation of Parquet.*')
warnings.filterwarnings('ignore', message='.*overflow encountered*')
warnings.filterwarnings('ignore', message='.*index_parts defaults to True')
warnings.filterwarnings('ignore', message='.*`op` parameter is deprecated*')
def _azimuth(point1, point2):
    """azimuth between 2 shapely points (interval 0 - 180)"""
    angle = np.arctan2(point2[0] - point1[0], point2[1] - point1[1])
    return np.degrees(angle) if angle > 0 else np.degrees(angle) + 180


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])
path = "./files/buildings_230221.shp"
buildings = gpd.read_file(path)
buildings=buildings.rename({'Elevation':'height'},axis=1)
buildings['height']=np.round(buildings['height'],2)
buildings["uID"] = range(len(buildings))

check = mm.CheckTessellationInput(buildings,shrink=0.1)

limit = mm.buffered_limit(buildings, 10)

tessellation = mm.Tessellation(buildings, "uID", limit, verbose=False,shrink=0.1)
tessellation = tessellation.tessellation


tessellation.to_file("./files/geometry.gpkg", layer="tessellation")

path = "./files/streets.shp"
streets = gpd.read_file(path)
streets=gpd.GeoDataFrame(streets['geometry'])

streets.plot()

extended = mm.extend_lines(streets, tolerance=120, target=gpd.GeoSeries([limit.boundary]), barrier=buildings)
#%%
blocks = mm.Blocks(tessellation, edges=extended, buildings=buildings, id_name='bID', unique_id='uID')
blocks_df = blocks.blocks  # get blocks df
buildings['bID'] = blocks.buildings_id.values  # get block ID
tessellation['bID'] = blocks.tessellation_id.values  # get block ID

path = './files/geometry.gpkg'
tessellation.to_file(path, layer='tessellation', driver='GPKG')
buildings.to_file(path, layer='buildings', driver='GPKG')
blocks_df.to_file(path, layer='blocks', driver='GPKG')

buildings['floor_area'] = (buildings["height"] / 3.5) * buildings.area

buildings_box=gpd.GeoDataFrame()

buildings['Area'] = mm.Area(buildings).series
buildings['Peri'] = mm.Perimeter(buildings).series
rect_area_list=[]
rect_peri_list=[]
rect_ori_list=[]
for geom in tqdm(buildings.geometry):
    polygon=Polygon(geom)
    min_rect=polygon.minimum_rotated_rectangle
    bbox = list(min_rect.exterior.coords)
    axis1 = _dist(bbox[0], bbox[3])
    axis2 = _dist(bbox[0], bbox[1])

    if axis1 <= axis2:
        az = _azimuth(bbox[0], bbox[1])
    else:
        az = _azimuth(bbox[0], bbox[3])
    rect_ori_list.append(az)
    rect_area_list.append(min_rect.area)
    rect_peri_list.append(min_rect.length)
buildings_box['Area']=rect_area_list
buildings_box['Peri']=rect_peri_list
buildings_box['MBG_L']=(buildings_box['Peri']+np.sqrt(np.square(buildings_box['Peri'])-16*buildings_box['Area']))/4
buildings_box['MBG_W']=buildings_box['Area']/buildings_box['MBG_L']

buildings['MBG_L']=buildings_box['MBG_L']
buildings['MBG_W']=buildings_box['MBG_W']
buildings['REC_A']=buildings['Area']/buildings_box['Area']
buildings['REC_P']=buildings['Peri']/buildings_box['Peri']
#
# buildings['sdbVol'] = mm.Volume(buildings, 'height', 'sdbAre').series
#
# buildings['sdbCoA'] = mm.CourtyardArea(buildings, 'sdbAre').series
#
# buildings['ssbFoF'] = mm.FormFactor(buildings, 'sdbVol', 'sdbAre').series
# buildings['ssbVFR'] = mm.VolumeFacadeRatio(buildings, 'height', 'sdbVol', 'sdbPer').series
# buildings['ssbCCo'] = mm.CircularCompactness(buildings, 'sdbAre').series
# buildings['ssbCor'] = mm.Corners(buildings, verbose=False).series
# buildings['ssbSqu'] = mm.Squareness(buildings, verbose=False).series
# buildings['ssbERI'] = mm.EquivalentRectangularIndex(buildings, 'sdbAre', 'sdbPer').series
# buildings['ssbElo'] = mm.Elongation(buildings).series