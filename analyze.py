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

INPUT_TRIPS = "all_trips2.parquet"
INPUT_STATIONS = "all_stations.parquet"

def main():
  parser = argparse.ArgumentParser(description='Script description')
  parser.add_argument('input', help='Input file or value')
  args = parser.parse_args()

  trips_df = pd.read_parquet(INPUT_TRIPS)
  stations_df = pd.read_parquet(INPUT_STATIONS)

  print(trips_df.info())
  print(stations_df.info())

# def avg_dist_and_duration(df):

if __name__ == '__main__':
  main()
