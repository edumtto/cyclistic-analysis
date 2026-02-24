#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd
import os
import pandavro as pdx

# Basic color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

all_trips = []
all_stations = []

OUTPUT_TRIPS = "dataset/all_trips.parquet"
OUTPUT_STATIONS = "dataset/all_stations.parquet"

rideable_type_map = {
    "classic_bike": 0,
    "electric_bike": 1
}

member_casual_map = {
    "member": True,
    "casual": False
}

def main():
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('input', help='Input file or value')
    args = parser.parse_args()
    
    files = os.listdir(str(args.input))
    non_hiden_files = [f for f in files if not f.startswith('.')]

    print(f"\nProcessing {GREEN}{str(len(non_hiden_files))} files{RESET}")

    for file in non_hiden_files:
      process_file(args.input + '/' + file)

    # Concating data frames
    all_trips_df = pd.concat(all_trips, ignore_index=True)
    all_stations_df = pd.concat(all_stations, ignore_index=True).drop_duplicates(subset=['id'])


    # Saving to parquet
    all_trips_df.to_parquet(OUTPUT_TRIPS, engine='pyarrow', index=False)
    all_stations_df.to_parquet(OUTPUT_STATIONS, engine='pyarrow', index=False)

    # pdx.to_avro(OUTPUT_STATIONS, all_stations_df)
    print(f"\n✔ Saved to:\n{GREEN}- {OUTPUT_TRIPS}\n- {OUTPUT_STATIONS}{RESET}")

    print(f"\n{BLUE}Sample Data Trips:{RESET}")
    print(all_trips_df.head())
    print(f"\n{BLUE}Sample Data Stations:{RESET}")
    print(all_stations_df.head())


def process_file(file_path):
    
    df = pd.read_csv(file_path)

    print(f"\nProcessing {YELLOW}{len(df)} entries from {file_path}\n{RESET}")

    # Drop entries with null values and duplicates
    df = df.dropna(subset=['start_station_id', 'end_station_id', 'ride_id', 'started_at', 'ended_at'])
    print(f"\nDropped empty entries. Now: {YELLOW}{len(df)} entries \n{RESET}")
    df = df.drop_duplicates()
    print(f"\nDropped duplicates. Now: {YELLOW}{len(df)} entries \n{RESET}")

    print_info(df)
    
    df["rideable_type"] = df["rideable_type"].str.strip().str.lower().map(rideable_type_map).astype(int)
    df["is_member"] = df["member_casual"].str.strip().str.lower().map(member_casual_map).astype(bool)
    df["start_station_id"] = df["start_station_id"].astype("string").str.strip()
    df["end_station_id"] = df["end_station_id"].astype("string").str.strip()
    df["ride_id"] = df["ride_id"].astype("string").str.strip()
    df['started_at'] = pd.to_datetime(df['started_at'], format='%Y-%m-%d %H:%M:%S.%f')
    df['ended_at'] = pd.to_datetime(df['ended_at'], format='%Y-%m-%d %H:%M:%S.%f')
    df = df[df['started_at'] < df['ended_at']]  # Remove rides with invalid duration
    
    # Add columns that list the date, month, day, and year of each ride
    df['date'] = df['started_at'].dt.date
    df['time'] = df['started_at'].dt.time
    df['month'] = df['started_at'].dt.month
    df['day'] = df['started_at'].dt.day
    df['day_of_week'] = df['started_at'].dt.day_name()

    df['duration'] = (df['ended_at'] - df['started_at']).dt.total_seconds().astype(int)
    df['dist_km_simple'] = quick_distance(df, 'start_lat', 'start_lng', 'end_lat', 'end_lng')

    # Extract Station Data for the Lookup Table (Normalization)
    start_stations_df = df[['start_station_id', 'start_station_name', 'start_lat', 'start_lng']].rename(
        columns={'start_station_id': 'id', 'start_station_name': 'name', 'start_lat': 'lat', 'start_lng': 'lng'}
    )

    end_stations_df = df[['end_station_id', 'end_station_name', 'end_lat', 'end_lng']].rename(
        columns={'end_station_id': 'id', 'end_station_name': 'name', 'end_lat': 'lat', 'end_lng': 'lng'}
    )

    union_stations = pd.concat([start_stations_df, end_stations_df], ignore_index=True).drop_duplicates(subset=['id'])
    union_stations['id'] = union_stations['id'].astype("string")
    union_stations['name'] = union_stations['name'].str.strip()
    union_stations['lat'] = union_stations['lat'].astype(float)
    union_stations['lng'] = union_stations['lng'].astype(float)
    all_stations.append(union_stations)


    df.drop(columns=['member_casual', 'start_station_name', 'end_station_name', 'start_lat', 'start_lng', 'end_lat', 'end_lng'], inplace=True)
    # print(df.head())
    all_trips.append(df)

def print_info(df):
    print("\nColumns:")
    print(*df.columns, sep=', ')

    unique_rideable_type = df['rideable_type'].unique()
    # print("\nrideable_type:")
    # print(*unique_rideable_type, sep=', ')
    if len(unique_rideable_type) > 2:
        print(f"{RED}✖ Error: rideable_type has more than 2 unique values{RESET}")
        exit(1)

    unique_member_casual = df['member_casual'].unique()
    # print("\nmember_casual:")
    # print(*unique_member_casual, sep=', ')
    if len(unique_member_casual) > 2:
        print(f"{RED}✖ Error: member_casual has more than 2 unique values{RESET}")
        exit(1)

def quick_distance(df, lat1_col, lon1_col, lat2_col, lon2_col):
    # Mean latitude in radians for the cosine correction
    mean_lat = np.radians((df[lat1_col] + df[lat2_col]) / 2)
    
    # 1 degree of latitude is roughly 111.32 km
    # Longitude distance shrinks as we move toward the poles
    dx = (df[lon1_col] - df[lon2_col]) * np.cos(mean_lat)
    dy = df[lat1_col] - df[lat2_col]
    
    # Distance in km
    return 111.32 * np.sqrt(dx**2 + dy**2)

if __name__ == '__main__':
    main()
