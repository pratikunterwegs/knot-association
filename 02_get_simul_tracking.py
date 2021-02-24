import os
import pandas as pd
import geopandas as gpd
import numpy as np
from ncls import NCLS

print(os.getcwd())

# in this section, we quanitify the temporal overlap between individuals
# at the global scale, so, how long were two individuals tracked together

# read in the data again
# group by id and get the first time_start and the final time_end
data = pd.read_csv("data/data_2018_id_tracking_interval.csv")
# get integer series of start and end times of patches
t_start = data.loc[:,'time_start'].astype(np.int64)  # indexing from 1
t_end = data.loc[:,'time_end'].astype(np.int64)  # indexing from 1
t_id = data.loc[:,'id']  # indexing from 1

# total overlap
data_list = []
for i in np.arange(1, len(t_id)+1):
    ncls = NCLS(t_start[i:].values, t_end[i:].values, t_id[i:])
    it = ncls.find_overlap(t_start[i], t_end[i])
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
