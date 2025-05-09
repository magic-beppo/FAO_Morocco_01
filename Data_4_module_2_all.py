import os
import pandas as pd

# Define the path to the CSV files
BasePath = os.path.dirname(os.path.abspath(__file__))
PathData = os.path.join(BasePath, '..', 'data', 'psd_alldata.csv')
PathPopulationData = os.path.join(BasePath, '..', 'data', 'Population.csv')

# Read the CSV files
df = pd.read_csv(PathData)
population_df = pd.read_csv(PathPopulationData)

# Step 1: Subset the dataset to include the observations where the country_codes are 'MO', 'EG', 'LY', 'TS', 'AG', 'MR'
subset_df = df[df['Country_Code'].isin(['MO', 'EG', 'LY', 'TS', 'AG', 'MR', 'JO', 'MU'])].copy()

# Strip any whitespace from the Country_Code column to avoid hidden characters
subset_df['Country_Code'] = subset_df['Country_Code'].str.strip()

# Step 2: Replace country_code AL with DZ, TS with TN, and MO with MA
subset_df['Country_Code'] = subset_df['Country_Code'].replace({'AG': 'DZ', 'TS': 'TN', 'MO': 'MA', 'MU': 'OM'})

# Verify replacement
# print("Unique country codes after replacement:", subset_df['Country_Code'].unique())

# Step 3: Eliminate the observations for Attribute_ID=184, Attribute_Description=Yield
subset_df = subset_df[subset_df['Attribute_ID'] != 184]

# Step 4: Eliminate the variables Calendar_Year and Month
subset_df = subset_df.drop(columns=['Calendar_Year', 'Month'])

# Function to create commodity aggregates
def aggregate_commodities(df, codes, new_code, new_description, divide_by=1):
    agg_columns = ['Country_Code', 'Country_Name', 'Market_Year', 'Attribute_ID', 'Attribute_Description', 'Unit_ID', 'Unit_Description']
    agg_df = df[df['Commodity_Code'].isin(codes)].copy()
    agg_df['Value'] = agg_df['Value'] / divide_by
    agg_df = agg_df.groupby(agg_columns)['Value'].sum().reset_index()
    agg_df['Commodity_Code'] = new_code
    agg_df['Commodity_Description'] = new_description
    return pd.concat([df, agg_df], ignore_index=True)

# Create all commodity aggregates
subset_df = aggregate_commodities(subset_df, [430000, 440000, 459100, 452000, 422110, 459200, 410000], 400000, 'Cereals')
subset_df = aggregate_commodities(subset_df, [430000, 440000, 459100, 452000, 459200], 490000, 'Coarse Grains')
subset_df = aggregate_commodities(subset_df, [2223000, 2221000, 2226000, 2222000, 2224000], 2200000, 'Oilseeds, Total')
subset_df = aggregate_commodities(subset_df, [4233000, 4235000, 4243000, 4239100, 4232000, 4236000], 4200000, 'Vegetable Oils, Total')
subset_df = aggregate_commodities(subset_df, [813300, 814200, 813200, 813600, 813100], 810000, 'Oilmeals, Total')
subset_df = aggregate_commodities(subset_df, [571120, 579220, 574000, 571220, 575100], 570000, 'Fresh Fruit', divide_by=1000)
subset_df = aggregate_commodities(subset_df, [577901, 577907, 577400], 570001, 'Nuts, Total', divide_by=1000)
subset_df = aggregate_commodities(subset_df, [111000, 115000, 113000, 114200], 110000, 'Meat, Total')

# Step 5: Create country aggregate for "North Africa" with country code "NN"
country_agg_columns = ['Commodity_Code', 'Commodity_Description', 'Market_Year', 'Attribute_ID', 'Attribute_Description', 'Unit_ID', 'Unit_Description']
north_africa_countries = ['MA', 'EG', 'LY', 'TN', 'DZ']
north_africa_aggregated_df = subset_df[subset_df['Country_Code'].isin(north_africa_countries)].groupby(country_agg_columns)['Value'].sum().reset_index()
north_africa_aggregated_df['Country_Code'] = 'NN'
north_africa_aggregated_df['Country_Name'] = 'North Africa'

# Step 6: Create country aggregate for "SNE" with country code "SNE"
sne_countries = ['MR', 'MA', 'DZ', 'LY', 'TN']
sne_aggregated_df = subset_df[subset_df['Country_Code'].isin(sne_countries)].groupby(country_agg_columns)['Value'].sum().reset_index()
sne_aggregated_df['Country_Code'] = 'SNE'
sne_aggregated_df['Country_Name'] = 'SNE Countries'

# Append the country aggregated data to the final aggregated dataframe
final_aggregated_df = pd.concat([subset_df, north_africa_aggregated_df, sne_aggregated_df], ignore_index=True)

# Ensure uniqueness to avoid duplicates
final_aggregated_df = final_aggregated_df.drop_duplicates(subset=['Country_Code', 'Country_Name', 'Commodity_Code', 'Commodity_Description', 'Market_Year', 'Attribute_ID', 'Attribute_Description'])

# Step 7: (Re)Calculate yield including for the country and commodity aggregate
# Note: Yield calculation is Production / Area Harvested with the unit_id 26 and unit_description (MT/HA)
pivot_df = final_aggregated_df.pivot(index=['Country_Code', 'Country_Name', 'Commodity_Code', 'Commodity_Description', 'Market_Year'], columns='Attribute_Description', values='Value').reset_index()
print("Columns in pivot_df:", pivot_df.columns)
print("Sample data in pivot_df:", pivot_df.head())

if 'Production' in pivot_df.columns and 'Area Harvested' in pivot_df.columns:
    pivot_df['Yield'] = pivot_df['Production'] / pivot_df['Area Harvested']
    yield_df = pivot_df.melt(id_vars=['Country_Code', 'Country_Name', 'Commodity_Code', 'Commodity_Description', 'Market_Year'], value_vars=['Yield'], var_name='Attribute_Description', value_name='Value')
    yield_df['Attribute_ID'] = 184
    yield_df['Unit_ID'] = 26
    yield_df['Unit_Description'] = '(MT/HA)'
    final_aggregated_df = pd.concat([final_aggregated_df, yield_df], ignore_index=True)

# Step 8: Merge the Population file by Country_Code and Market_year
merged_df = pd.merge(final_aggregated_df, population_df, how='left', left_on=['Country_Code', 'Market_Year'], right_on=['Country_Code', 'Market_Year'])

# Calculate population aggregate for North Africa
north_africa_population = population_df[population_df['Country_Code'].isin(north_africa_countries)].groupby('Market_Year')['Population'].sum().reset_index()
north_africa_population['Country_Code'] = 'NN'
north_africa_population['Country_Name'] = 'North Africa'

# Merge the North Africa population data back to the main population dataframe
population_df = pd.concat([population_df, north_africa_population], ignore_index=True)

# Calculate population aggregate for SNE
sne_population = population_df[population_df['Country_Code'].isin(sne_countries)].groupby('Market_Year')['Population'].sum().reset_index()
sne_population['Country_Code'] = 'SNE'
sne_population['Country_Name'] = 'SNE Countries'

# Merge the SNE population data back to the main population dataframe
population_df = pd.concat([population_df, sne_population], ignore_index=True)

# Step 9: Ensure Population data for cereals in North Africa and SNE is included
merged_df = pd.merge(final_aggregated_df, population_df, how='left', left_on=['Country_Code', 'Market_Year'], right_on=['Country_Code', 'Market_Year'])

# Drop Country_Name_y and rename Country_Name_x to Country_Name
merged_df = merged_df.drop(columns=['Country_Name_y'])
merged_df = merged_df.rename(columns={'Country_Name_x': 'Country_Name'})

# Ensure Population is retained
merged_df['Population'] = merged_df['Population']

# Reapply the country filter to ensure only the specified countries are included
final_countries = ['MR', 'MA', 'LY', 'DZ', 'TN', 'EG', 'JO', 'OM', 'NN', 'SNE']
merged_df = merged_df[merged_df['Country_Code'].isin(final_countries)]

# Aggregate to ensure uniqueness
agg_columns = ['Country_Code', 'Country_Name', 'Commodity_Code', 'Commodity_Description', 'Market_Year', 'Attribute_Description']
merged_df = merged_df.groupby(agg_columns, as_index=False).agg({'Value': 'sum', 'Population': 'first', 'Attribute_ID': 'first', 'Unit_ID': 'first', 'Unit_Description': 'first'})

# Step 10: Sort the DataFrame by Commodity_Code, Country_Code, and Market_Year
merged_df = merged_df.sort_values(by=['Commodity_Code', 'Country_Code', 'Market_Year'])

# Step 11: Create a CSV output file called psd_north_africa.csv
output_path = os.path.join(BasePath, 'psd_north_africa.csv')
merged_df.to_csv(output_path, index=False)

print(f"CSV output file created: {output_path}")
