import os
import pandas as pd
import geopandas as gpd
import numpy as np
from ncls import NCLS

print(os.getcwd())
# re-read csv data because of integer handling differences
data = pd.read_csv("data/data_2018_good_patches.csv")

# use a subset
data = data.loc[1:1000,]

# get integer series of start and end times of patches
t_start = data['time_start'].astype(np.int64)
t_end = data['time_end'].astype(np.int64)
patch_uid = data['uid']
t_id = np.arange(0, len(t_start))

# trial ncls
# only works on pandas and not geopandas else throws error!
# this is very weird behaviour, pd and gpd must differ in int implementation
ncls = NCLS(t_start.values, t_end.values, t_id.values)

# look at all the overlaps in time
# get a dataframe of the overlapping pairs and the extent of overlap
data_list = []
for i in np.arange(1, len(t_id)+1):
    ncls = NCLS(t_start[i:].values, t_end[i:].values, t_id[i-1:])  # id needs to be from an array
    it = ncls.find_overlap(t_start[i], t_end[i])
    # get the unique patch ids overlapping
    overlap_id = []
    overlap_extent = []
    # get the extent of overlap
    for x in it:
        overlap_id.append(patch_uid[x[2]])  # x[2] is the t_id index
        overlap_extent.append(min(x[1], t_end[i]) - max(x[0], t_start[i]))
    # add the overlap id for each obs
    uid = [patch_uid[i]] * len(overlap_id)
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
data_overlap.to_csv("data/data_time_overlaps_patches_2018.csv", index=False)
# ends here