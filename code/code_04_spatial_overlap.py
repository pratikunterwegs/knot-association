# import classic python libs
import numpy as np

# libs for dataframes
import pandas as pd
import geopandas as gpd

# import ckdtree
# from scipy.spatial import cKDTree
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon

# import ckdtree
# from scipy.spatial import cKDTree

# import helper functions
from helper_functions import simplify_geom, ckd_distance

# read in spatial data
patches = gpd.read_file("data/data2018/spatials/patches_2018.gpkg")
patches.head()
patches.crs = {'init': 'epsg:32631'}

# read in temporal overlaps
data_overlap = pd.read_csv("data/data2018/data_time_overlaps_patches_2018.csv")

# for each overlap uid/overlap_id get the ckd distance of
# the corresponding rows in the spatial
spatial_cross = []
for i in np.arange(len(data_overlap)):
    # get the geometries
    g_a = patches.iloc[data_overlap.iloc[i].uid]
    g_b = patches.iloc[data_overlap.iloc[i].overlap_id]
    covers = g_a.geometry.intersects(g_b.geometry)
    spatial_cross.append(covers)

# convert to series and add to data frame
data_overlap['spatial_overlap'] = pd.Series(spatial_cross)

# write to file
data_overlap.to_csv("data/data2018/data_spatio_temporal_intersection_2018.csv")

# now that we know which patches overlap in space and time
# get the extent of overlap, and the actual overlap object
data_overlap = data_overlap[data_overlap['spatial_overlap'] == True]

# in a for loop, add the extent and overlap object
overlap_extent = []
overlap_obj = []
for i in np.arange(len(data_overlap)):
    # get the geometries
    g_a = patches.iloc[data_overlap.iloc[i].uid]
    g_b = patches.iloc[data_overlap.iloc[i].overlap_id]
    # get overlap
    overlap_polygon = g_a.geometry.intersection(g_b.geometry)
    overlap_obj.append(overlap_polygon)
    overlap_extent.append(overlap_polygon.area)

# add to data
data_overlap['spatial_overlap_area'] = pd.Series(overlap_extent)
data_overlap['geometry'] = overlap_obj
