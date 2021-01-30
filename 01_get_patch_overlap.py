import os
import pandas as pd
import geopandas as gpd
import numpy as np
from ncls import NCLS

print(os.getcwd())

# read in the SPATIAL data
# because the patch data has some spatials missing
# ie patches are described but not made
patches = gpd.read_file("data/data_2018/spatials/patches_2018.gpkg")

# plot patches for a sanity check
subset = patches.iloc[0:1000]
subset.plot(linewidth=0.5,
            column='id',
            alpha=0.2,
            cmap='tab20b', edgecolor='black')

# convert to dataframe, export, and read in again
data = pd.DataFrame(patches.drop(columns='geometry'))

# assign unique patch id
data['uid'] = np.arange(0, data.shape[0])

# overwrite data with uid
data.to_csv("data/data_2018/data_2018_patch_summary_has_patches.csv",
            index=False)

# remove from memory
del patches

# re-read csv data because of integer handling differences
data = pd.read_csv("data/data_2018/data_2018_patch_summary_has_patches.csv")
# get integer series of start and end times of patches
t_start = data['time_start'].astype(np.int64)
t_end = data['time_end'].astype(np.int64)
t_id = data['uid']

# trial ncls
# only works on pandas and not geopandas else throws error!
# this is very weird behaviour, pd and gpd must differ in int implementation
ncls = NCLS(t_start.values, t_end.values, t_id.values)

# look at all the overlaps in time
# get a dataframe of the overlapping pairs and the extent of overlap
data_list = []
for i in np.arange(len(t_id)):
    ncls = NCLS(t_start[i:].values, t_end[i:].values, t_id[i:].values)
    it = ncls.find_overlap(t_start[i],
                           t_end[i])
    # get the unique patch ids overlapping
    overlap_id = []
    overlap_extent = []
    # get the extent of overlap
    for x in it:
        overlap_id.append(x[2])
        overlap_extent.append(min(x[1], t_end[i]) - max(x[0], t_start[i]))
    # add the overlap id for each obs
    uid = [i] * len(overlap_id)
    # zip the tuples together
    tmp_data = list(zip(uid, overlap_id, overlap_extent))
    # convert to lists
    tmp_data = list(map(list, tmp_data))
    tmp_data = list(filter(lambda x: x[0] != x[1], tmp_data))
    # tmp_data = tmp_data[tmp_data.uid != tmp_data.overlap_id]
    data_list = data_list + tmp_data

# concatenate to dataframe
data_overlap = pd.DataFrame(data_list,
                         columns=['uid', 'overlap_id', 'overlap_extent'])

# save data
data_overlap.to_csv("data/data_2018/data_time_overlaps_patches_2018.csv", index=False)

# in this section, we quanitify the temporal overlap between individuals
# at the global scale, so, how long were two individuals tracked together

# read in the data again
# group by id and get the first time_start and the final time_end
data = pd.read_csv("data/data_2018/data_2018_id_tracking_interval.csv")
# get integer series of start and end times of patches
t_start = data['time_start'].astype(np.int64)
t_end = data['time_end'].astype(np.int64)
t_id = data['id']

# total overlap
data_list = []
for i in np.arange(len(t_id)):
    ncls = NCLS(t_start[i:].values, t_end[i:].values, t_id[i:].values)
    it = ncls.find_overlap(t_start[i],
                           t_end[i])
    # get the unique patch ids overlapping
    overlap_id = []
    overlap_extent = []
    # get the extent of overlap
    for x in it:
        overlap_id.append(x[2])
        overlap_extent.append(min(x[1], t_end[i]) - max(x[0], t_start[i]))
    # add the overlap id for each obs
    uid = [t_id[i]] * len(overlap_id)
    # zip the tuples together
    tmp_data = list(zip(uid, overlap_id, overlap_extent))
    # convert to lists
    tmp_data = list(map(list, tmp_data))
    tmp_data = list(filter(lambda x: x[0] != x[1], tmp_data))
    # tmp_data = tmp_data[tmp_data.uid != tmp_data.overlap_id]
    data_list = data_list + tmp_data

# concatenate to dataframe
data_overlap = pd.DataFrame(data_list,
                         columns=['uid', 'overlap_id', 'total_simul_tracking'])


# write total simul tracking data
data_overlap.to_csv("data/data_2018/data_2018_id_simul_tracking.csv", index=False)

# wip

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
patches = gpd.read_file("data/data_2018/spatials/patches_2018.gpkg")
patches.head()
patches.crs = {'init': 'epsg:32631'}

# read in temporal overlaps
data_overlap = pd.read_csv("data/data_2018/data_time_overlaps_patches_2018.csv")

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

# now that we know which patches overlap in space and time
# get the extent of overlap, and the actual overlap object
data_overlap = data_overlap[spatial_cross]

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
data_overlap['spatial_overlap_area'] = np.asarray(overlap_extent)
data_overlap['geometry'] = overlap_obj

# remove spatial overlap col
data_overlap = data_overlap.drop(columns='spatial_overlap')

# make geodataframe
overlap_spatials = gpd.GeoDataFrame(data_overlap, geometry=data_overlap['geometry'])

# save into spatails
overlap_spatials.to_file("data/data_2018/spatials/patch_overlap_2018.gpkg", layer='overlaps',
                         driver="GPKG")

# save to csv
data_overlap = pd.DataFrame(overlap_spatials.drop(columns = 'geometry'))
data_overlap = data_overlap.rename(columns={"overlap_extent":"temporal_overlap_seconds",
                                            "uid":"patch_i_unique_id",
                                            "overlap_id":"patch_j_unique_id"})

# write to file
data_overlap.to_csv("data/data_2018/data_spatio_temporal_overlap_2018.csv", index=False)

# ends here