import pandas as pd
import os

# Get the base path of the current script
BasePath = os.path.dirname(os.path.abspath(__file__))

# Define the path to the CSV file
data1_path = os.path.join(BasePath, 'Population.csv')

# Load the psd_grains_pulses dataset
try:
    data_in1 = pd.read_csv(data1_path, encoding='utf-8')
    
    # Extract unique Country_Name and Country_Code pairs
    unique_countries = data_in1[['Country', 'Country_Code']].drop_duplicates().sort_values(by='Country')
    
    # Display the unique list of country names and country codes
    print(unique_countries)
    
    # Optionally, save this list to a CSV file
    output_path = os.path.join(BasePath, 'unique_countries_pop.csv')
    unique_countries.to_csv(output_path, index=False)
    print(f"Unique countries list saved to {output_path}")
except FileNotFoundError as e:
    print(f"Error: {e}")
except pd.errors.EmptyDataError as e:
    print(f"Error: Population.csv is empty. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
