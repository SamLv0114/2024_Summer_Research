import os
import pandas as pd
from datetime import datetime,time, timedelta

# Define time constants
evening_start = time(18, 0)  # 6 PM
morning_end = time(9, 0)  # 9 AM

# function to get all subdirs in the MTA data folder
def get_data_paths(main_dir):
    data_paths = []
    for root, dirs, files in os.walk(main_dir):
        for dir in dirs:
            data_paths.append(os.path.join(root, dir))
        break
    
    return data_paths


# Function to reformat the time scale
def parse_time(curr_time):
    if curr_time == '24:00:00':
        return time(0, 0)
    else:
        try:
            return pd.to_datetime(curr_time, format='%H:%M:%S').time()
        except ValueError:
            h, m, s = map(int, curr_time.split(':'))
            h = h % 24
            return (datetime(2024, 1, 1, h, m, s) + timedelta(days=h // 24)).time()

# Function to filter out trips that start after 6 PM and end before 9 AM next day
def filter_trip(trip):
    trip_start_time = parse_time(trip["departure_time"].iloc[0])
    trip_end_time = parse_time(trip["arrival_time"].iloc[-1])

    # Check if the trip starts after 6 PM and ends before 9 AM
    if trip_start_time >= evening_start or trip_end_time <= morning_end:
        return pd.DataFrame()  # Exclude this trip
    
    return trip  # Keep the trip if it does not fall within the excluded range

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

    filtered_path = f'{base_path}/filtered_trips.txt'

    filtered_trips = filtered_trips.drop_duplicates(subset='trip_id', keep='first')

    # save the filtered data
    filtered_trips[['route_id', 'service_id', 'trip_id', 'trip_headsign', 'direction_id', 'block_id', 'shape_id']].to_csv(filtered_path, index=False)




