#' ---
#' editor_options: 
#'   chunk_output_type: console
#' ---
#' 
#' # Cleaning data
#' 
#' This section is about cleaning downloaded data using the `cleanData` function in the [WATLAS Utilities package](https://github.com/pratikunterwegs/watlastools).
#' 
#' **Workflow**
#' 
#' 1. Prepare required libraries.
#' 2. Read in data, apply the cleaning function, and overwrite local data.
#' 
#' ## Prepare `watlastools` and other libraries
#' 
## ----install_watlastools_2, message=FALSE, warning=FALSE----
# watlastools assumed installed from the previous step
# if not, install from the github repo as shown below

devtools::install_github("pratikunterwegs/watlastools")
library(watlastools)

# libraries to process data
library(data.table)
library(purrr)
library(glue)
library(fasttime)
library(bit64)
library(stringr)

#' 
#' ## Prepare to remove attractor points
#' 
## ----read_attractors, message=FALSE, warning=FALSE-----
# read in identified attractor points
atp <- fread("data/data2018/attractor_points.txt")

#' 
#' ## Read, clean, and write data
#' 
## ----read_in_raw_data, message=FALSE, warning=FALSE----
# make a list of data files to read
data_files <- list.files(path = "data/data2018/locs_raw", pattern = "whole_season*", full.names = TRUE)

data_ids <- str_extract(data_files, "(tx_\\d+)") %>% str_sub(-3,-1)

# read deployment data from local file in data folder
tag_info <- fread("data/data2018/SelinDB.csv")

# filter out NAs in release date and time
tag_info <- tag_info[!is.na(Release_Date) & !is.na(Release_Time),]

# make release date column as POSIXct
tag_info[,Release_Date := as.POSIXct(paste(Release_Date, Release_Time, sep = " "), format = "%d.%m.%y %H:%M", tz = "CET")]

# sub for knots in data
data_files <- data_files[as.integer(data_ids) %in% tag_info$Toa_Tag]

# map read in, cleaning, and write out function over vector of filenames
map(data_files, function(df){
  
  temp_data <- fread(df, integer64 = "numeric")
  
  # filter for release date + 24 hrs
  {
    temp_id <- str_sub(temp_data[1, TAG], -3, -1)
    
    rel_date <- tag_info[Toa_Tag == temp_id, Release_Date]
    
    temp_data <- temp_data[TIME/1e3 > as.numeric(rel_date + (24*3600)),]
  }
  tryCatch(
    {
      temp_data <- wat_rm_attractor(df = temp_data,
                                    atp_xmin = atp$xmin,
                                    atp_xmax = atp$xmax,
                                    atp_ymin = atp$ymin,
                                    atp_ymax = atp$ymax)
      
      clean_data <- wat_clean_data(somedata = temp_data,
                                   moving_window = 3,
                                   nbs_min = 0,
                                   sd_threshold = 100,
                                   filter_speed = TRUE,
                                   speed_cutoff = 150)
      
      agg_data <- wat_agg_data(df = clean_data,
                               interval = 30)
      
      message(glue('tag {unique(agg_data$id)} cleaned with {nrow(agg_data)} fixes'))
      
      fwrite(x = agg_data, file = glue('data/data2018/locs_proc/id_{temp_id}.csv'), dateTimeAs = "ISO")
      rm(temp_data, clean_data, agg_data)
      },
    error = function(e){
      message(glue('tag {unique(temp_id)} failed'))
    })
})


#' 
