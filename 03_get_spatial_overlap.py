import os
import pandas as pd
import geopandas as gpd
import numpy as np

# import ckdtree
# from scipy.spatial import cKDTree
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon

# import helper functions
from helper_functions import simplify_geom, ckd_distance

print(os.getcwd())

# read in spatial data
patches = gpd.read_file("data/data_patches_good_2018_basic.gpkg")
patches.head()
patches.crs = {'init': 'epsg:32631'}

# read in temporal overlaps
data_overlap = pd.read_csv("data/data_time_overlaps_patches_2018.csv")

# for each overlap uid/overlap_id get the ckd distance of
# the corresponding rows in the spatial
spatial_cross = []
for i in np.arange(len(data_overlap)):
    # get the geometries
    g_a = patches[patches['uid'] == data_overlap['uid'][i]]
    g_b = patches[patches['uid'] == data_overlap['overlap_id'][i]]
    intersection = g_a.geometry.intersects(g_b.geometry)
    # overlap area
    patches_intersect = False
    for i in intersection.to_list():
        if (i):
            patches_intersect = True
    spatial_cross.append([patches_intersect, area])

# convert to series and add to data frame
data_overlap['spatial_overlap'] = pd.Series(spatial_cross)

# write to file
data_overlap.to_csv("data/data_spatio_temporal_overlap_2018.csv", index=False)

# # now that we know which patches overlap in space and time
# # get the extent of overlap, and the actual overlap object
# data_overlap = data_overlap[spatial_cross]
#
# # in a for loop, add the extent and overlap object
# overlap_extent = []
# overlap_obj = []
# for i in np.arange(len(data_overlap)):
#     # get the geometries
#     g_a = patches.iloc[data_overlap.iloc[i].uid]
#     g_b = patches.iloc[data_overlap.iloc[i].overlap_id]
#     # get overlap
#     overlap_polygon = g_a.geometry.intersection(g_b.geometry)
#     overlap_obj.append(overlap_polygon)
#     overlap_extent.append(overlap_polygon.area)
#
# # add to data
# data_overlap['spatial_overlap_area'] = np.asarray(overlap_extent)
# data_overlap['geometry'] = overlap_obj
#
# # remove spatial overlap col
# data_overlap = data_overlap.drop(columns='spatial_overlap')
#
# # make geodataframe
# overlap_spatials = gpd.GeoDataFrame(data_overlap, geometry=data_overlap['geometry'])
#
# # save into spatails
# overlap_spatials.to_file("data/data_2018/spatials/patch_overlap_2018.gpkg", layer='overlaps',
#                          driver="GPKG")
#
# # save to csv
# data_overlap = pd.DataFrame(overlap_spatials.drop(columns = 'geometry'))
# data_overlap = data_overlap.rename(columns={"overlap_extent":"temporal_overlap_seconds",
#                                             "uid":"patch_i_unique_id",
#                                             "overlap_id":"patch_j_unique_id"})

