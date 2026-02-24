# Cyclistic bike-share analysis case study

## Specification

### Scenario
Cyclistic is bike-share program that features more than 5,800 bicycles and 600 docking stations. The director of marketing believes the company’s future success depends on maximizing the number of annual memberships, therefore, he wants to understand how casual riders and annual members use Cyclistic bikes differently to design a new marketing strategy to convert casual riders into annual members.

### Business Task

Identify how casual riders and annual members use Cyclistic bikes differently.

### Data Sources Used

2025 trip data from https://divvy-tripdata.s3.amazonaws.com/index.html

### Cleaning and Preprocessing

- Removed trips with invalid duration (started_at > ended_at).
- Cleaned duplicated entries.
- Included columns that list the date, month, day, and day of the week of each ride.
- Included trip duration in seconds.
- Converted rideable_type from string to number: classic_bike = 0, electric_bike = 1.
- Renamed member_casual to is_member and converted it from string to bollean values.

- Stored stations names and coordenates in a separate file.
- Concated all months into an year data file.
- Exported the processed data into two parquet format files.


## Analysis

### Summary

### Visualizations and Findings

### Recommendations