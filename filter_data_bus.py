import os
import pandas as pd
from datetime import datetime,time, timedelta

# midnight
time_start = time(0, 0)

# 5am
time_end = time(5, 0)

# function to get all subdirs in the MTA data folder
def get_data_paths(main_dir):
    data_paths = []
    for root, dirs, files in os.walk(main_dir):
        for dir in dirs:
            data_paths.append(os.path.join(root, dir))
        break
    
    return data_paths
            

# function to reformat the time scale
def parse_time(curr_time):
    if curr_time == '24:00:00':
        return time(0, 0)
    else:
        try:
            return pd.to_datetime(time, format='%H:%M:%S').time()
        
        except ValueError:
            h, m, s = map(int, curr_time.split(':'))
            h = h % 24
            return (datetime(2024, 1, 1, h, m, s) + timedelta(days=h // 24)).time()


# function to filter out trips that have a departure time after 12am and end before 5am
def filter_trip(trip):
    trip_start_time = trip["departure_time"].iloc[0]
    trip_end_time = trip["arrival_time"].iloc[-1]
    
    if trip_start_time>time_start and trip_end_time<time_end:
        return pd.DataFrame()
    return trip


paths = get_data_paths(r'C:\Users\baodu\Dropbox\Summer_research_2024\MTA_data')

for base_path in paths:
    trips = pd.read_csv(f'{base_path}\\trips.txt')
    stop_times = pd.read_csv(f'{base_path}\\stop_times.txt')
  
    merged_trips = trips.merge(stop_times, on='trip_id')
    
    # convert time
    merged_trips['arrival_time'] = merged_trips['arrival_time'].apply(parse_time)
    merged_trips['departure_time'] = merged_trips['departure_time'].apply(parse_time)

    filtered_trips = merged_trips.groupby('trip_id').apply(filter_trip)
    
    filtered_trips['stop_sequence'] = filtered_trips['stop_sequence'].astype(int)

    filtered_path = f'{base_path}/updated_trips.txt'

    filtered_trips = filtered_trips.drop_duplicates(subset='trip_id', keep='first')

    # save the filtered data
    filtered_trips[['route_id', 'service_id', 'trip_id', 'trip_headsign', 'direction_id', 'block_id', 'shape_id']].to_csv(filtered_path, index=False)




