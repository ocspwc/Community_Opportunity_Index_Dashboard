import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium 
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from folium.plugins import MeasureControl
import streamlit.components.v1 as components
import os
import re

# Set up the Streamlit page 
#st.image("static/logo2.png", width=200)
st.set_page_config(
        page_title="Community Opportunity Index -- Prince William County",
        page_icon="https://github.com/JiaqinWu/GRIT_Website/raw/main/logo1.png", 
        layout="wide",
        initial_sidebar_state="collapsed"
    ) 
#st.image("static/logo1.png", use_column_width=True)
#st.title("Community Opportunity Index -- Prince William County")

# Load Data
profile_data = pd.read_csv('PWC_Census_Tract_Opportunity_Profile.csv')
with open("geojson_data.geojson") as f:
    prince_william_tracts = json.load(f)

census_tracts = gpd.read_file("Demographic_files/tl_2024_51_tract.shp")
if 'GEOID' not in profile_data.columns:
    # Assuming CensusTract from the CSV is the GEOID
    profile_data["GEOID"] = profile_data["CensusTract"].astype(str)

# Ensure GEOID is string type in both datasets
census_tracts["GEOID"] = census_tracts["GEOID"].astype(str)
profile_data["GEOID"] = profile_data["GEOID"].astype(str)

variable_name_map = {
    # Socioeconomic
    "LOWINCPCT": "Low Income Population",
    "UNEMPPCT": "Unemployment Rate",
    "LINGISOPCT": "Limited English Proficiency",
    "LESSHSPCT": "Less than High School Education",
    "E_POV150_P": "Population Below 150% Poverty Level",
    "With_PublicAssIncome_P": "Public Assistance Income",
    "With_SSI_P": "Supplemental Security Income",
    "E_UNINSUR_P": "Uninsured Population",
    "With_Medicaid_P": "Medicaid Coverage",
    "percent_food_insecure": "Food Insecurity Rate",
    "LIFEEXPPCT": "Life Expectancy",

    # Housing
    "PRE1960PCT": "Housing Built Before 1960",
    "E_HBURD_P": "Housing Cost Burden",
    "House_Vacant_P": "Vacant Housing",
    "E_MUNIT_P": "Multi-Unit Housing",
    "E_MOBILE_P": "Mobile Homes",
    "E_CROWD_P": "Crowded Housing",
    "Owner_occupied_P": "Owner-Occupied Housing",
    "Mean_Proportion_HHIncome": "Housing Cost as % of Income",
    "percent_homeowners": "Homeownership Rate",

    # Mobility (formerly Transportation)
    "PTRAF": "Traffic Volume",
    "E_NOVEH_P": "No Vehicle Access",
    "Mean_Transportation_time(min)": "Average Commute Time",
    "Work_Drivealone_P": "Drive Alone to Work",
    "Work_Carpooled_P": "Carpool to Work",
    "Work_PublicTransportation_P": "Public Transit to Work",
    "Work_Walk_P": "Walk to Work",
    "Work_Fromhome_P": "Work from Home",

    # Transportation Safety (formerly TransportationSafety)
    "Percent_Severe/Fatal": "Severe/Fatal Crashes",
    "Avg_Person_Injured/Kill": "Person Injuries/Fatalities",
    "Avg_Pedestrian_Injured/Kill": "Pedestrian Injuries/Fatalities",
    "Percent_Alcohol_Related": "Alcohol-Related Crashes",
    "Percent_Distracted_Related": "Distracted Driving Crashes",
    "Percent_Drowsy_Related": "Drowsy Driving Crashes",
    "Percent_Drug_Related": "Drug-Related Crashes",
    "Percent_Speed_Related": "Speed-Related Crashes",
    "Percent_Hitrun_Related": "Hit and Run Crashes",
    "Percent_Schoolzone_Related": "School Zone Crashes",
    "Percent_Lgtruck_Related": "Large Truck Crashes",
    "Percent_Young_Related": "Young Driver Crashes",
    "Percent_Senior_Related": "Senior Driver Crashes",
    "Percent_Bike_Related": "Bicycle Crashes",
    "Percent_Night_Related": "Nighttime Crashes",
    "Percent_Workzone_Related": "Work Zone Crashes",

    # Environmental
    "PM25": "Fine Particulate Matter",
    "OZONE": "Ozone Level",
    "DSLPM": "Diesel Particulate Matter",
    "NO2": "Nitrogen Dioxide",
    "CANCER": "Cancer Risk",
    "RESP": "Respiratory Hazard",
    "PTRAF": "Traffic Proximity",
    "PWDIS": "Wastewater Discharge",
    "PNPL": "Superfund Sites",
    "PRMP": "RMP Facilities",
    "PTSDF": "Hazardous Waste Sites",
    "UST": "Underground Storage Tanks",
    "WATR": "Water Discharge Sites",
    "RSEI_AIR": "Air Releases",

    # Public Health (formerly PublicHealth)
    "Total_Calls": "Fire and EMS Incidents",
    "Chronic_History": "Chronic Health Conditions",
    "Violence_Calls": "Violence-Related Calls",
    "CPR_Calls": "Cardiac Arrests",
    "Homeless": "Homelessness-Related Calls",
    "Domestic": "Domestic-Related Calls",
    "Opioid_Calls": "Opioid-Related Emergency Calls",
    "Calls_Per_HVU_Caller": "Calls per High Volume User",

    # Demographics
    "DISABILITYPCT": "Disability Rate",
    "UNDER5PCT": "Under 5 Years Old",
    "OVER64PCT": "Over 64 Years Old",
    "E_SNGPNT_P": "Single Parent Households",
    "E_GROUPQ_P": "Group Quarters Population",
    "Total_Population": "Total Population",
    "Median_Age": "Median Age",
    "Age_Dependency_Ratio": "Age Dependency Ratio",
    "Old-age_Dependency_Ratio": "Old-Age Dependency Ratio",
    "Child_Dependency_Ratio": "Child Dependency Ratio",
    "Prop_White": "White Population",
    "Sex_Ratio(males per 100 females)": "Sex Ratio (males per 100 females)",
    "Prop_Black": "Black Population",
    "Prop_Hisp": "Hispanic Population"
}

# Enhanced domain categorization with updated domain names
domain_categories = {
    "Socioeconomic": [
        "LOWINCPCT", "UNEMPPCT", "LINGISOPCT", "LESSHSPCT", "E_POV150_P",
        "With_PublicAssIncome_P", "With_SSI_P", "E_UNINSUR_P", "With_Medicaid_P",
        "percent_food_insecure", "LIFEEXPPCT"
    ],
    "Housing": [
        "PRE1960PCT", "E_HBURD_P", "House_Vacant_P", "E_MUNIT_P", "E_MOBILE_P",
        "E_CROWD_P", "Owner_occupied_P", "Mean_Proportion_HHIncome", "percent_homeowners"
    ],
    "Mobility": [  # Changed from Transportation
        "PTRAF", "E_NOVEH_P", "Mean_Transportation_time(min)", "Work_Drivealone_P",
        "Work_Carpooled_P", "Work_PublicTransportation_P", "Work_Walk_P", "Work_Fromhome_P"
    ],
    "Transportation Safety": [  # Changed from TransportationSafety (added space)
        "Percent_Severe/Fatal", "Avg_Person_Injured/Kill", "Avg_Pedestrian_Injured/Kill",
        "Percent_Alcohol_Related", "Percent_Distracted_Related", "Percent_Drowsy_Related",
        "Percent_Drug_Related", "Percent_Speed_Related", "Percent_Hitrun_Related",
        "Percent_Schoolzone_Related", "Percent_Lgtruck_Related", "Percent_Young_Related",
        "Percent_Senior_Related", "Percent_Bike_Related", "Percent_Night_Related",
        "Percent_Workzone_Related"
    ],
    "Environmental": [
        "PM25", "OZONE", "DSLPM", "NO2", "CANCER", "RESP", "PTRAF", "PWDIS",
        "PNPL", "PRMP", "PTSDF", "UST", "WATR", "RSEI_AIR"
    ],
    "Public Health": [  # Changed from PublicHealth (added space)
        "Total_Calls", "Chronic_History", "Violence_Calls", "CPR_Calls", "Homeless", "Domestic", "Opioid_Calls", "Calls_Per_HVU_Caller",
    ],
    "Demographics": [
        "DISABILITYPCT", "UNDER5PCT", "OVER64PCT", "E_SNGPNT_P", "E_GROUPQ_P",
        "Total_Population", "Median_Age", "Age_Dependency_Ratio",
        "Old-age_Dependency_Ratio", "Child_Dependency_Ratio", "Prop_White",
        "Sex_Ratio(males per 100 females)", "Prop_Black", "Prop_Hisp"
    ]
}

# Filter domain categories to only include variables that exist in the data
print("Filtering variables to only include those that exist in the data...")
filtered_domain_categories = {}
for domain_name, variables in domain_categories.items():
    existing_variables = [var for var in variables if var in profile_data.columns]
    filtered_domain_categories[domain_name] = existing_variables
    print(f"{domain_name}: {len(existing_variables)}/{len(variables)} variables found")

# Variables where higher values are better (reverse scoring for opportunity interpretation)
reverse_variables = [
    'percent_homeowners', 'Owner_occupied_P', 'Work_Carpooled_P', 'Work_PublicTransportation_P',
    'Work_Walk_P', 'Work_Fromhome_P', 'Total_Population', 'LIFEEXPPCT'
]

# Calculate percentile-based thresholds for each variable
print("Calculating percentile-based thresholds...")
variable_thresholds = {}

for domain_name, variables in filtered_domain_categories.items():
    for variable in variables:
        if variable in profile_data.columns:
            values = profile_data[variable].dropna()
            if len(values) > 0:
                if variable in reverse_variables:
                    variable_thresholds[variable] = {
                        'p33': values.quantile(0.33),
                        'p67': values.quantile(0.67),
                        'reverse': True
                    }
                else:
                    variable_thresholds[variable] = {
                        'p33': values.quantile(0.33),
                        'p67': values.quantile(0.67),
                        'reverse': False
                    }

print(f"Calculated thresholds for {len(variable_thresholds)} variables")

# Function to get a readable variable name
def get_readable_name(var_name):
    return variable_name_map.get(var_name, var_name.replace('_', ' '))


# Create GEOID column in profile data if needed - using CensusTract
if 'GEOID' not in profile_data.columns:
    profile_data["GEOID"] = profile_data["CensusTract"].astype(str)

# Ensure GEOID is string type in both datasets
census_tracts["GEOID"] = census_tracts["GEOID"].astype(str)
profile_data["GEOID"] = profile_data["GEOID"].astype(str)

# Filter census tracts to just Prince William County if needed (COUNTYFP = 153 for Prince William)
if 'COUNTYFP' in census_tracts.columns:
    pwc_tracts = census_tracts[census_tracts['COUNTYFP'] == '153']
    if len(pwc_tracts) > 0:
        print(f"Filtering to {len(pwc_tracts)} Prince William County census tracts")
        census_tracts = pwc_tracts

# Merge data
print("Merging data with boundaries...")
merged_data = profile_data.merge(
    census_tracts,
    on="GEOID",
    how="left"
)

# Convert to GeoDataFrame
merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')

# Check for missing merges
missing = merged_data.loc[merged_data.geometry.isna()].shape[0]
print(f"\nUnmatched tracts: {missing}")

if missing > 0:
    print("Warning: Some census tracts couldn't be matched to shapefile geometries.")
    merged_data = merged_data.dropna(subset=['geometry'])

if len(merged_data) == 0:
    st.error("No data available after merging. Please check your data files.")
    st.stop()

# Function to combine districts for tracts that span multiple districts
def combine_districts_for_tract(tract_df):
    """
    Combine district information for tracts that appear multiple times.
    Returns a single row with combined district information.
    """
    if len(tract_df) == 1:
        # Single entry, no combination needed
        row = tract_df.iloc[0]
        # If District_combined doesn't exist, create it from District
        if 'District_combined' not in row or pd.isna(row['District_combined']):
            row['District_combined'] = row['District'] if pd.notna(row['District']) else 'Not Available'
        return row
    
    # Multiple entries - combine district information
    row = tract_df.iloc[0].copy()  # Use first row as base
    
    # Check if District_combined already exists with proportions
    if 'District_combined' in tract_df.columns:
        district_combined_values = tract_df['District_combined'].dropna()
        if len(district_combined_values) > 0:
            # Use the first non-null District_combined value
            row['District_combined'] = district_combined_values.iloc[0]
            return row
    
    # Fallback to old logic if District_combined doesn't exist
    districts = tract_df['District'].dropna()
    districts = districts[districts.str.strip() != '']
    unique_districts = districts.unique()
    
    if len(unique_districts) > 1:
        # Combine districts with comma separation
        combined_districts = ', '.join(sorted(unique_districts))
        row['District_combined'] = combined_districts
    else:
        # Single district or no districts
        row['District_combined'] = unique_districts[0] if len(unique_districts) > 0 else 'Not Available'
    
    return row

# Group by CensusTract and combine districts for tracts with multiple entries
print("Combining district information for tracts with multiple entries...")
grouped_data = merged_data.groupby('CensusTract').apply(combine_districts_for_tract).reset_index(drop=True)

# Function to parse district information with proportions
def parse_district_info(district_str):
    """Parse district string that may contain proportions like 'WOODBRIDGE:100%' or 'COLES:39.91%,POTOMAC:60.09%' or 'GAINESVILLE15.18%'"""
    
    if district_str == 'Not Available' or not district_str:
        return {
            'districts': [],
            'proportions': {},
            'display_text': 'Not Available',
            'is_multi_district': False,
            'primary_district': 'Not Available'
        }
    
    # Split by comma to handle multiple districts
    district_parts = [part.strip() for part in district_str.split(',')]
    
    districts = []
    proportions = {}
    
    for part in district_parts:
        if ':' in part:
            # Format: "DISTRICT:PROPORTION%"
            district_name, proportion_str = part.split(':', 1)
            district_name = district_name.strip()
            proportion_str = proportion_str.strip().replace('%', '')
            
            try:
                proportion = float(proportion_str)
                districts.append(district_name)
                proportions[district_name] = proportion
            except ValueError:
                # If proportion parsing fails, treat as district name only
                districts.append(district_name)
                proportions[district_name] = 100.0
        else:
            # Check if there's a percentage without a colon (e.g., "GAINESVILLE15.18%")
            # Use regex to find digits followed by %
            match = re.search(r'(\d+\.?\d*)%$', part)
            if match:
                # Extract district name (everything before the percentage)
                proportion_str = match.group(1)
                district_name = part[:match.start()].strip()
                
                try:
                    proportion = float(proportion_str)
                    districts.append(district_name)
                    proportions[district_name] = proportion
                except ValueError:
                    # If proportion parsing fails, treat as district name only
                    districts.append(part)
                    proportions[part] = 100.0
            else:
                # Format: "DISTRICT" (no proportion)
                districts.append(part)
                proportions[part] = 100.0
    
    # Determine primary district (highest proportion)
    primary_district = max(proportions.keys(), key=lambda k: proportions[k]) if proportions else 'Not Available'
    
    # Create display text
    if len(districts) == 1:
        display_text = districts[0]
    else:
        # Sort by proportion (descending) for display
        sorted_districts = sorted(districts, key=lambda d: proportions[d], reverse=True)
        display_parts = []
        for district in sorted_districts:
            prop = proportions[district]
            if prop == 100.0:
                display_parts.append(district)
            else:
                display_parts.append(f"{district} ({prop:.2f}%)")
        display_text = ', '.join(display_parts)
    
    is_multi_district = len(districts) > 1
    
    return {
        'districts': districts,
        'proportions': proportions,
        'display_text': display_text,
        'is_multi_district': is_multi_district,
        'primary_district': primary_district
    }

# Create a dictionary to prepare our tract data for JavaScript
tract_data = {}
for idx, row in grouped_data.iterrows():
    tract_id = row['CensusTract']

    # Domain rankings - need to map old names to new names for lookup
    domain_ranks = {}
    # Map old domain names from CSV to new display names
    old_to_new_domain_map = {
        'Socioeconomic': 'Socioeconomic',
        'Housing': 'Housing',
        'Transportation': 'Mobility',
        'TransportationSafety': 'Transportation Safety',
        'Environmental': 'Environmental',
        'PublicHealth': 'Public Health'
    }

    old_domains = ['Socioeconomic', 'Housing', 'Transportation', 'TransportationSafety', 'Environmental', 'PublicHealth']
    for old_domain in old_domains:
        rank_col = f"{old_domain}_Rank"
        if rank_col in row and pd.notna(row[rank_col]):
            new_domain = old_to_new_domain_map[old_domain]
            domain_ranks[new_domain] = int(row[rank_col])

    # Top variables by domain
    domain_variables = {}
    for old_domain in old_domains:
        domain_vars = []
        for i in range(1, 4):
            var_col = f"{old_domain}_Var{i}"
            if var_col in row and pd.notna(row[var_col]) and row[var_col]:
                domain_vars.append(get_readable_name(row[var_col]))
        if domain_vars:
            new_domain = old_to_new_domain_map[old_domain]
            domain_variables[new_domain] = domain_vars

    # Geographic identifiers
    def safe_get(column_name, default="Not Available"):
        if column_name in row and pd.notna(row[column_name]) and str(row[column_name]).strip():
            return str(row[column_name]).strip()
        return default

    # Use District_combined if available, otherwise fall back to District
    district_raw = safe_get('District_combined') if 'District_combined' in row else safe_get('District')
    
    district_info = parse_district_info(district_raw)
    
    # Add asterisk to tract ID if it spans multiple districts
    display_tract_id = f"{tract_id}*" if district_info['is_multi_district'] else tract_id

    tract_data[tract_id] = {
        'opportunity_index': float(row['PWC_Opportunity_Index']),  # Updated column name
        'opportunity_tier': row['Opportunity_Tier'] if 'Opportunity_Tier' in row else '',  # Updated
        'top_domain': old_to_new_domain_map.get(row['Top_Domain'], row['Top_Domain']) if 'Top_Domain' in row else '',
        'domain_ranks': domain_ranks,
        'domain_variables': domain_variables,
        'district': district_info['display_text'],  # Updated to use parsed district info
        'district_raw': district_raw,  # Keep original raw data
        'districts': district_info['districts'],  # List of district names
        'proportions': district_info['proportions'],  # Dictionary of district:proportion
        'primary_district': district_info['primary_district'],  # Primary district (highest proportion)
        'neighborhood': safe_get('Neighborhood'),
        'first_due': safe_get('1st Due'),
        'display_tract_id': display_tract_id,
        'is_multi_district': district_info['is_multi_district']
    }

# Add opportunity_index to the GeoJSON properties
grouped_data['opportunity_index'] = grouped_data['PWC_Opportunity_Index']

# Create map file
print("Creating modern opportunity index map with multi-select interactive legend...")

# Prepare GeoJSON
geo_data = grouped_data.to_json()
tract_data_json = json.dumps(tract_data).replace("'", "\\'")

# Prepare domain categories and thresholds for JavaScript
domain_categories_json = json.dumps(filtered_domain_categories)
variable_thresholds_json = json.dumps(variable_thresholds)
variable_name_map_json = json.dumps(variable_name_map)

# HTML file name - UPDATED
output_file = "PWC_Community_Opportunity_Index_Multi_Select_Legend_Map.html"

# Write HTML file
with open(output_file, "w") as f:
    # Write the complete HTML file
    bounds = grouped_data.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PWC Community Opportunity Index Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', sans-serif;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}

        body {{
            display: flex;
            height: 100vh;
            width: 100vw;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #1f2937;
            color: #f3f4f6;
            position: fixed;
            top: 0;
            left: 0;
        }}

        #map {{
            flex: 1;
            height: 100vh;
            width: calc(100vw - 400px);
            z-index: 1;
            position: absolute;
            top: 0;
            left: 0;
        }}

        #panel {{
            width: 400px;
            height: 100vh;
            padding: 20px;
            background-color: #1f2937;
            box-shadow: -3px 0 10px rgba(0,0,0,0.2);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            z-index: 2;
            border-left: 1px solid #374151;
            position: fixed;
            right: 0;
            top: 0;
        }}

        #panel.hidden {{
            display: none;
        }}

        h1 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 22px;
            font-weight: 500;
            text-align: center;
            color: #f3f4f6;
        }}

        h2 {{
            margin-top: 0;
            font-size: 18px;
            font-weight: 500;
            color: #f3f4f6;
        }}

        h3 {{
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 16px;
            font-weight: 500;
            color: #f3f4f6;
        }}

        hr {{
            border: 0;
            height: 1px;
            background: #374151;
            margin: 15px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            background-color: #283548;
            border-radius: 8px;
            overflow: hidden;
        }}

        td {{
            padding: 10px;
            border-bottom: 1px solid #374151;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        ul {{
            margin-top: 8px;
            margin-bottom: 15px;
            padding-left: 25px;
        }}

        li {{
            margin-bottom: 6px;
            color: #e5e7eb;
        }}

        .info {{
            padding: 8px 10px;
            font: 14px/16px 'Roboto', sans-serif;
            background: #283548;
            color: #f3f4f6;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 8px;
            border: 1px solid #374151;
            min-width: 200px;
            width: auto;
        }}

        .info h4 {{
            margin: 0 0 8px;
            color: #9ca3af;
            font-weight: 500;
        }}

        .legend {{
            line-height: 20px;
            color: #e5e7eb;
        }}

        .legend i {{
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.85;
        }}

        /* Interactive legend styles */
        .legend {{
            min-width: 220px;
            max-width: 280px;
            width: auto;
        }}
        
        .legend h4 {{
            white-space: nowrap;
            overflow: visible;
            text-overflow: unset;
            width: 100%;
            margin: 0 0 8px 0;
            padding: 0;
            font-size: 14px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 2px 0;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}

        .legend-item:hover {{
            background-color: rgba(55, 65, 81, 0.5);
        }}

        .legend-item.active {{
            background-color: rgba(96, 165, 250, 0.3);
            border: 1px solid #60a5fa;
        }}

        .legend-color {{
            width: 18px;
            height: 18px;
            margin-right: 8px;
            border: 1px solid #374151;
            flex-shrink: 0;
        }}

        .legend-text {{
            flex: 1;
        }}

        .legend-reset {{
            background: #374151;
            color: #f3f4f6;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 8px;
            transition: background-color 0.2s;
        }}

        .legend-reset:hover {{
            background: #4b5563;
        }}

        /* District filter styles - exactly matching legend styles */
        .district-filter {{
            line-height: 20px;
            color: #e5e7eb;
            width: 320px; /* Match legend width exactly */
        }}

        .district-filter-item {{
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 2px 0;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}

        .district-filter-item:hover {{
            background-color: rgba(55, 65, 81, 0.5);
        }}

        .district-filter-item.active {{
            background-color: rgba(96, 165, 250, 0.3);
            border: 1px solid #60a5fa;
        }}

        .district-filter-color {{
            width: 18px;
            height: 18px;
            margin-right: 8px;
            border: 1px solid #374151;
            flex-shrink: 0;
            background: #6b7280; /* Gray color for districts */
        }}

        .district-filter-text {{
            flex: 1;
        }}

        .district-filter-reset {{
            background: #374151;
            color: #f3f4f6;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 8px;
            transition: background-color 0.2s;
        }}

        .district-filter-reset:hover {{
            background: #4b5563;
        }}

        .place-label {{
            background-color: transparent;
            border: none;
            white-space: nowrap;
        }}

        .subtitle {{
            text-align: center;
            font-size: 14px;
            margin-bottom: 20px;
            color: #9ca3af;
            font-weight: 300;
        }}

        .panel-header {{
            text-align: center;
            margin-bottom: 25px;
        }}

        .district-note {{
            background-color: #283548;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            font-size: 12px;
            line-height: 1.4;
        }}

        .district-note p {{
            margin: 0;
            color: #e5e7eb;
        }}

        .district-note strong {{
            color: #f3f4f6;
            font-weight: 500;
        }}

        .panel-content {{
            flex: 1;
        }}

        .info-box {{
            background-color: #283548;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}

        .info-box p {{
            margin-bottom: 8px;
            color: #e5e7eb;
        }}

        .info-box p:last-child {{
            margin-bottom: 0;
        }}

        .info-box strong {{
            color: #f3f4f6;
            font-weight: 500;
        }}

        .domain-section {{
            background-color: #283548;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }}

        .domain-section strong {{
            color: #f3f4f6;
            font-weight: 500;
        }}

        .welcome-message {{
            padding: 30px;
            text-align: center;
            font-size: 16px;
            color: #9ca3af;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 300;
        }}

        .close-button {{
            position: absolute;
            top: 15px;
            right: 15px;
            border: none;
            background: none;
            font-size: 20px;
            font-weight: 300;
            color: #9ca3af;
            cursor: pointer;
            transition: color 0.2s;
        }}

        .close-button:hover {{
            color: #f3f4f6;
        }}

        .opportunity-value {{
            display: flex;
            align-items: center;
            margin: 15px 0;
        }}

        .opportunity-value-number {{
            font-size: 24px;
            font-weight: 700;
            margin-right: 10px;
            color: #f3f4f6;
        }}

        .opportunity-value-label {{
            font-size: 14px;
            color: #9ca3af;
        }}

        .opportunity-tier {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            margin-top: 5px;
            margin-bottom: 10px;
        }}

        .tier-less {{
            background-color: rgba(220, 38, 38, 0.2);
            color: #ef4444;
        }}

        .tier-moderate {{
            background-color: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }}

        .tier-high {{
            background-color: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }}

        .tier-exceptional {{
            background-color: rgba(5, 150, 105, 0.2);
            color: #059669;
        }}

        .rank-number {{
            display: inline-block;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: #374151;
            color: #f3f4f6;
            text-align: center;
            line-height: 24px;
            margin-right: 8px;
            font-weight: 500;
        }}

        .geographic-info {{
            background-color: #374151;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
        }}

        .geographic-info .geo-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            padding: 2px 0;
        }}

        .geographic-info .geo-item:last-child {{
            margin-bottom: 0;
        }}

        .geographic-info .geo-label {{
            font-weight: 500;
            color: #9ca3af;
            min-width: 120px;
        }}

        .geographic-info .geo-value {{
            color: #f3f4f6;
            text-align: right;
            flex: 1;
        }}

        .leaflet-container {{
            background-color: #111827;
        }}

        .leaflet-control-zoom a {{
            background-color: #283548;
            color: #f3f4f6;
            border-color: #374151;
        }}

        .leaflet-control-zoom a:hover {{
            background-color: #374151;
        }}

        .leaflet-control-attribution {{
            background-color: rgba(40, 53, 72, 0.8) !important;
            color: #9ca3af !important;
        }}

        .leaflet-control-attribution a {{
            color: #60a5fa !important;
        }}

        .district-label {{
            font-weight: bold;
            font-size: 18px; /* Increased from 15px */
            background-color: rgba(40, 53, 72, 0.85);
            border: 1px solid #4b5563;
            border-radius: 4px;
            padding: 6px 10px; /* Increased padding */
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}

        .tab-container {{
            margin-top: 20px;
            background-color: #283548;
            border-radius: 8px;
            overflow: hidden;
        }}

        .tab-header {{
            display: flex;
            flex-wrap: wrap;
            background-color: #1f2937;
            border-bottom: 1px solid #374151;
        }}

        .tab-button {{
            flex: 1;
            min-width: 85px;
            padding: 8px 6px;
            border: none;
            background: none;
            color: #9ca3af;
            cursor: pointer;
            font-size: 10px;
            font-weight: 500;
            transition: all 0.2s;
            border-bottom: 2px solid transparent;
        }}

        .tab-button:hover {{
            color: #f3f4f6;
            background-color: rgba(55, 65, 81, 0.3);
        }}

        .tab-button.active {{
            color: #f3f4f6;
            border-bottom-color: #60a5fa;
            background-color: rgba(55, 65, 81, 0.5);
        }}

        .tab-content {{
            display: none;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}

        .tab-content.active {{
            display: block;
        }}

        .variable-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #374151;
        }}

        .variable-item:last-child {{
            border-bottom: none;
        }}

        .variable-name {{
            font-size: 13px;
            color: #e5e7eb;
            flex: 1;
            margin-right: 10px;
        }}

        .variable-value {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .value {{
            font-weight: 600;
            color: #f3f4f6;
            min-width: 50px;
            text-align: right;
        }}

        .risk-direction {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .risk-arrow {{
            font-size: 12px;
            font-weight: bold;
        }}

        .above-average {{
            color: #10b981;
        }}

        .below-average {{
            color: #9ca3af;
        }}

        .near-average {{
            color: #9ca3af;
        }}

        .risk-text {{
            font-size: 9px;
            font-weight: 500;
        }}

        .demographic-value {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .demographic-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #374151;
        }}

        .demographic-item:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div id="panel">
        <button class="close-button" onclick="document.getElementById('panel').classList.add('hidden')">X</button>
        <div class="panel-header">
            <h1>PWC Community Opportunity Index</h1>
            <div class="subtitle">Census Tract Details</div>
            <div class="district-note">
                <p><strong>District Categorization:</strong> Census tracts are assigned to districts based on the proportion of area within each district. The primary district is the one with the highest proportion. Tracts marked with * span multiple districts and show the detailed percentage breakdown below.</p>
            </div>
        </div>
        <div class="panel-content" id="panel-content">
            <div class="welcome-message">
                Click on a census tract to view detailed information
            </div>
        </div>
    </div>

    <script>
        var map = L.map('map', {{
            center: [{center_lat}, {center_lon}],
            zoom: 10,
            zoomControl: false
        }});

        L.tileLayer('https://cartodb-basemaps-{{s}}.global.ssl.fastly.net/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        L.control.zoom({{position: 'topright'}}).addTo(map);

        var selectedLayer = null;
        var domainCategories = {domain_categories_json};
        var variableThresholds = {variable_thresholds_json};
        var variableNameMap = {variable_name_map_json};
        var activeFilters = []; // Track multiple selected score ranges
        var activeDistrictFilters = []; // Track multiple selected districts
        var currentActiveTab = 'socioeconomic'; // Track the currently active tab

        function getOpportunityDirection(value, domain, variable) {{
            var numValue = parseFloat(value);
            if (isNaN(numValue)) {{
                return {{ arrow: '→', text: 'Average', class: 'near-average' }};
            }}

            var threshold = variableThresholds[variable];
            if (!threshold) {{
                return {{ arrow: '→', text: 'Average', class: 'near-average' }};
            }}

            var median = (threshold.p33 + threshold.p67) / 2;

            if (threshold.reverse) {{
                if (numValue > median) {{
                    return {{ arrow: '↑', text: 'Above Average', class: 'above-average' }};
                }} else {{
                    return {{ arrow: '↓', text: 'Below Average', class: 'below-average' }};
                }}
            }} else {{
                if (numValue > median) {{
                    return {{ arrow: '↑', text: 'Above Average', class: 'above-average' }};
                }} else {{
                    return {{ arrow: '↓', text: 'Below Average', class: 'below-average' }};
                }}
            }}
        }}

        function showTab(tabName) {{
            var contents = document.querySelectorAll('.tab-content');
            contents.forEach(function(content) {{
                content.classList.remove('active');
            }});

            var buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(function(button) {{
                button.classList.remove('active');
            }});

            document.getElementById(tabName + '-content').classList.add('active');
            document.getElementById(tabName + '-button').classList.add('active');

            // Update the current active tab variable
            currentActiveTab = tabName;
        }}

        // YlGnBu color scheme: Light Yellow to Dark Blue
        function getColor(d) {{
            return d > 7 ? '#08519c' :   // Darkest blue
                   d > 6 ? '#3182bd' :   // Dark blue
                   d > 5 ? '#6baed6' :   // Medium blue
                   d > 4 ? '#9ecae1' :   // Light blue
                   d > 3 ? '#c7e9b4' :   // Light green
                   d > 2 ? '#edf8b1' :   // Yellow-green
                   d > 1 ? '#ffffcc' :   // Light yellow
                            '#ffffe5';   // Lightest yellow
        }}

        // Function to determine if feature matches any of the selected score ranges
        function matchesAnyScoreRange(score, activeFilters) {{
            if (activeFilters.length === 0) {{
                return true; // No filters active, show all
            }}

            return activeFilters.some(function(filter) {{
                return Math.floor(score) === filter.value;
            }});
        }}

        // Function to determine if feature matches any of the selected districts
        function matchesAnyDistrict(districtData, activeDistrictFilters) {{
            if (activeDistrictFilters.length === 0) {{
                return true; // No filters active, show all
            }}

            // Check if any of the tract's districts match the selected filters
            return activeDistrictFilters.some(function(filter) {{
                // Check if the selected district is in the tract's districts list
                return districtData.districts && districtData.districts.includes(filter.value);
            }});
        }}

        function style(feature) {{
            var score = feature.properties.opportunity_index;
            var tractData = tractDataLookup[feature.properties.CensusTract];

            var baseStyle = {{
                fillColor: getColor(score),
                weight: 1.5,
                opacity: 1,
                color: '#1f2937',
                fillOpacity: 0.85
            }};

            // Check both score and district filters
            var matchesScore = matchesAnyScoreRange(score, activeFilters);
            var matchesDistrict = matchesAnyDistrict(tractData, activeDistrictFilters);

            // If any filters are active, adjust opacity for non-matching tracts
            if (activeFilters.length > 0 || activeDistrictFilters.length > 0) {{
                if (!matchesScore || !matchesDistrict) {{
                    baseStyle.fillOpacity = 0.1;
                    baseStyle.opacity = 0.3;
                }}
            }}

            return baseStyle;
        }}

        function highlightFeature(e) {{
            var layer = e.target;
            layer.setStyle({{
                weight: 3,
                color: '#f3f4f6',
                dashArray: '',
                fillOpacity: 0.9
            }});
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {{
                layer.bringToFront();
            }}
            info.update(layer.feature.properties);
        }}

        function resetHighlight(e) {{
            if (selectedLayer !== e.target) {{
                geojson.resetStyle(e.target);
            }}
            info.update();
        }}

        function getTierClass(tier) {{
            if (tier.includes('Less')) return 'tier-less';
            if (tier.includes('Moderate')) return 'tier-moderate';
            if (tier.includes('High') && !tier.includes('Exceptional')) return 'tier-high';
            if (tier.includes('Exceptional')) return 'tier-exceptional';
            return '';
        }}

        // Function to toggle filter selection for score value
        function toggleScoreFilter(scoreValue, legendItem) {{
            // Check if this filter is already active
            var filterIndex = activeFilters.findIndex(function(filter) {{
                return filter.value === scoreValue;
            }});

            if (filterIndex !== -1) {{
                // Filter is active, remove it
                activeFilters.splice(filterIndex, 1);
                legendItem.classList.remove('active');
            }} else {{
                // Filter is not active, add it
                activeFilters.push({{ value: scoreValue }});
                legendItem.classList.add('active');
            }}

            // Update all tract styles
            geojson.eachLayer(function(layer) {{
                layer.setStyle(style(layer.feature));
            }});

            // Update district label visibility
            updateDistrictLabels();
        }}

        // Function to toggle filter selection for district
        function toggleDistrictFilter(districtValue, filterItem) {{
            // Check if this filter is already active
            var filterIndex = activeDistrictFilters.findIndex(function(filter) {{
                return filter.value === districtValue;
            }});

            if (filterIndex !== -1) {{
                // Filter is active, remove it
                activeDistrictFilters.splice(filterIndex, 1);
                filterItem.classList.remove('active');
            }} else {{
                // Filter is not active, add it
                activeDistrictFilters.push({{ value: districtValue }});
                filterItem.classList.add('active');
            }}

            // Update all tract styles
            geojson.eachLayer(function(layer) {{
                layer.setStyle(style(layer.feature));
            }});

            // Update district label visibility
            updateDistrictLabels();
        }}

        // Function to update district label visibility based on active filters
        function updateDistrictLabels() {{
            var districtLabels = document.querySelectorAll('.district-label');
            districtLabels.forEach(function(label) {{
                var districtName = label.textContent;

                // Show label only if its district is selected (or no district filters active)
                if (activeDistrictFilters.length === 0) {{
                    // No district filters active, show all labels
                    label.style.display = 'block';
                }} else {{
                    // Check if this district is in active filters
                    var isActive = activeDistrictFilters.some(function(filter) {{
                        return filter.value === districtName.toUpperCase();
                    }});

                    label.style.display = isActive ? 'block' : 'none';
                }}
            }});
        }}

        // Function to reset all filters
        function resetAllFilters() {{
            activeFilters = [];
            activeDistrictFilters = [];
            document.querySelectorAll('.legend-item').forEach(function(item) {{
                item.classList.remove('active');
            }});
            document.querySelectorAll('.district-filter-item').forEach(function(item) {{
                item.classList.remove('active');
            }});
            geojson.eachLayer(function(layer) {{
                layer.setStyle(style(layer.feature));
            }});
            updateDistrictLabels();
        }}

        // Function to reset district filters only
        function resetDistrictFilters() {{
            activeDistrictFilters = [];
            document.querySelectorAll('.district-filter-item').forEach(function(item) {{
                item.classList.remove('active');
            }});
            geojson.eachLayer(function(layer) {{
                layer.setStyle(style(layer.feature));
            }});
            updateDistrictLabels();
        }}

        function createVariableList(properties, domain) {{
            var html = '';
            var variables = domainCategories[domain];

            if (variables && variables.length > 0) {{
                variables.forEach(function(variable) {{
                    var value = properties[variable];
                    var displayName = variableNameMap[variable] || variable;
                    var displayValue = 'N/A';

                    if (value !== null && value !== undefined && value !== '') {{
                        var numValue = parseFloat(value);
                        if (!isNaN(numValue)) {{
                            var isPercentage = (variable.includes('PCT') || variable.includes('_P') ||
                                              variable.includes('Percent_') || variable.includes('percent_') ||
                                              variable.includes('Work_') || variable.includes('With_') ||
                                              variable.includes('Owner_occupied') || variable.includes('House_Vacant') ||
                                              variable.includes('Prop_')) &&
                                              !variable.includes('Calls') && !variable.includes('_Calls') &&
                                              !variable.includes('EMS') && !variable.includes('Medical') &&
                                              !variable.includes('Violence') && !variable.includes('Opioid') &&
                                              !variable.includes('Fires') && !variable.includes('Homeless') &&
                                              !variable.includes('VMC') && !variable.includes('SFPC') &&
                                              !variable.includes('Vegetation') && !variable.includes('LIFEEXPPCT') &&
                                              !variable.includes('PM25') && !variable.includes('OZONE') &&
                                              !variable.includes('NO2') && !variable.includes('PTRAF') &&
                                              !variable.includes('Total_Population') && !variable.includes('Median_Age');

                            if (isPercentage && numValue < 1) {{
                                displayValue = Math.round(numValue * 100) + '%';
                            }} else if (isPercentage && numValue >= 1) {{
                                displayValue = Math.round(numValue) + '%';
                            }} else if (variable === 'Median_Age') {{
                                displayValue = Math.round(numValue) + ' years';
                            }} else if (variable.includes('Ratio')) {{
                                displayValue = numValue.toFixed(2);
                            }} else {{
                                displayValue = Math.round(numValue * 100) / 100;
                            }}
                        }} else {{
                            displayValue = value;
                        }}
                    }}

                    if (domain === 'Demographics') {{
                        html += `
                            <div class="demographic-item">
                                <div class="variable-name">${{displayName}}</div>
                                <div class="demographic-value">
                                    <span class="value">${{displayValue}}</span>
                                </div>
                            </div>`;
                    }} else {{
                        var opportunityDir = getOpportunityDirection(value, domain, variable);

                        html += `
                            <div class="variable-item">
                                <div class="variable-name">${{displayName}}</div>
                                <div class="variable-value">
                                    <span class="value">${{displayValue}}</span>
                                    <div class="risk-direction">
                                        <span class="risk-arrow ${{opportunityDir.class}}">${{opportunityDir.arrow}}</span>
                                        <span class="risk-text ${{opportunityDir.class}}">${{opportunityDir.text}}</span>
                                    </div>
                                </div>
                            </div>`;
                    }}
                }});
            }} else {{
                html = '<div class="variable-item"><div class="variable-name">No variables available for this domain</div></div>';
            }}

            return html;
        }}

        function clickFeature(e) {{
            var properties = e.target.feature.properties;
            var tractId = properties.CensusTract;
            var tractData = tractDataLookup[tractId];

            if (selectedLayer) {{
                geojson.resetStyle(selectedLayer);
            }}

            selectedLayer = e.target;
            selectedLayer.setStyle({{
                weight: 4,
                color: '#60a5fa',
                dashArray: '',
                fillOpacity: 0.9
            }});

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {{
                selectedLayer.bringToFront();
            }}

            document.getElementById('panel').classList.remove('hidden');
            var panelContent = document.getElementById('panel-content');

            var html = `
                <div class="info-box">
                    <h2>Census Tract: ${{tractData.display_tract_id}}</h2>
                    <div class="opportunity-value">
                        <div class="opportunity-value-number">${{tractData.opportunity_index.toFixed(1)}}</div>
                        <div class="opportunity-value-label">Service Opportunity Score<br/>(1-8 scale, higher = more opportunity)</div>
                    </div>
                    <div class="opportunity-tier ${{getTierClass(tractData.opportunity_tier)}}">${{tractData.opportunity_tier}}</div>
                    <p><strong>Primary Contributing Factor:</strong> ${{tractData.top_domain}}</p>
                </div>

                <div class="geographic-info">
                    <div class="geo-item">
                        <span class="geo-label">Census Tract:</span>
                        <span class="geo-value">${{tractId}}</span>
                    </div>
                    <div class="geo-item">
                        <span class="geo-label">${{tractData.is_multi_district ? 'Primary District:' : 'District:'}}</span>
                        <span class="geo-value">${{tractData.primary_district}}</span>
                    </div>`;
            
            // Add detailed district breakdown only if tract spans multiple districts
            if (tractData.is_multi_district && tractData.districts && tractData.districts.length > 1) {{
                html += `
                    <div class="geo-item">
                        <span class="geo-label">District Breakdown:</span>
                        <span class="geo-value">`;
                
                tractData.districts.forEach(function(district, index) {{
                    var proportion = tractData.proportions[district];
                    if (index > 0) html += '<br/>';
                    html += `${{district}}: ${{proportion.toFixed(2)}}%`;
                }});
                
                html += `</span>
                    </div>`;
            }}
            
            html += `
                    <div class="geo-item">
                        <span class="geo-label">Neighborhood:</span>
                        <span class="geo-value">${{tractData.neighborhood}}</span>
                    </div>
                    <div class="geo-item">
                        <span class="geo-label">Primary Fire Station:</span>
                        <span class="geo-value">${{tractData.first_due}}</span>
                    </div>
                </div>

                <h3>Impact on Opportunity Score (by Category)</h3>
                <table>`;

            // Create static ranking display (Option A: 1,2,3 | 4,5,6)
            var domainsByRank = [];
            var domains = Object.keys(tractData.domain_ranks);

            // Sort domains by their ranking
            domains.forEach(function(domain) {{
                var rank = tractData.domain_ranks[domain];
                domainsByRank[rank - 1] = domain; // rank 1 goes to index 0
            }});

            // Fill empty slots with placeholders
            for (var i = 0; i < 6; i++) {{
                if (!domainsByRank[i]) {{
                    domainsByRank[i] = "N/A";
                }}
            }}

            // Create the static 3x2 table layout
            for (var i = 0; i < 3; i++) {{
                html += '<tr>';
                // Left column: ranks 1, 2, 3
                var leftRank = i + 1;
                var leftDomain = domainsByRank[i];
                html += `<td><span class="rank-number">${{leftRank}}</span> ${{leftDomain}}</td>`;

                // Right column: ranks 4, 5, 6
                var rightRank = i + 4;
                var rightDomain = domainsByRank[i + 3];
                html += `<td><span class="rank-number">${{rightRank}}</span> ${{rightDomain}}</td>`;
                html += '</tr>';
            }}

            html += `</table>
                    <h3>Strongest Opportunity Indicators</h3>`;

            var domainVars = Object.keys(tractData.domain_variables);
            for (var j = 0; j < domainVars.length; j++) {{
                var domain = domainVars[j];
                var variables = tractData.domain_variables[domain];
                html += `
                    <div class="domain-section">
                        <strong>${{domain}}:</strong>
                        <ul>`;
                for (var k = 0; k < variables.length; k++) {{
                    html += `<li>${{variables[k]}}</li>`;
                }}
                html += `</ul></div>`;
            }}

            html += `
                <h3>All Domain Variables</h3>
                <div class="tab-container">
                    <div class="tab-header">
                        <button id="socioeconomic-button" class="tab-button" onclick="showTab('socioeconomic')">Socioeconomic</button>
                        <button id="housing-button" class="tab-button" onclick="showTab('housing')">Housing</button>
                        <button id="mobility-button" class="tab-button" onclick="showTab('mobility')">Mobility</button>
                        <button id="transportation-safety-button" class="tab-button" onclick="showTab('transportation-safety')">Transportation Safety</button>
                        <button id="environmental-button" class="tab-button" onclick="showTab('environmental')">Environmental</button>
                        <button id="public-health-button" class="tab-button" onclick="showTab('public-health')">Public Health</button>
                        <button id="demographics-button" class="tab-button" onclick="showTab('demographics')">Demographics</button>
                    </div>

                    <div id="socioeconomic-content" class="tab-content">
                        ${{createVariableList(properties, 'Socioeconomic')}}
                    </div>
                    <div id="housing-content" class="tab-content">
                        ${{createVariableList(properties, 'Housing')}}
                    </div>
                    <div id="mobility-content" class="tab-content">
                        ${{createVariableList(properties, 'Mobility')}}
                    </div>
                    <div id="transportation-safety-content" class="tab-content">
                        ${{createVariableList(properties, 'Transportation Safety')}}
                    </div>
                    <div id="environmental-content" class="tab-content">
                        ${{createVariableList(properties, 'Environmental')}}
                    </div>
                    <div id="public-health-content" class="tab-content">
                        ${{createVariableList(properties, 'Public Health')}}
                    </div>
                    <div id="demographics-content" class="tab-content">
                        ${{createVariableList(properties, 'Demographics')}}
                    </div>
                </div>`;

            panelContent.innerHTML = html;

            // Show the previously selected tab instead of defaulting to socioeconomic
            showTab(currentActiveTab);

            // Pan to center on the clicked tract (but keep current zoom level)
            var center = e.target.getBounds().getCenter();
            map.panTo(center, {{
                animate: true,
                duration: 0.8
            }});
        }}

        function onEachFeature(feature, layer) {{
            layer.on({{
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: clickFeature
            }});
        }}

        var tractDataLookup = {tract_data_json};
        var geoData = {geo_data};

        var geojson = L.geoJSON(geoData, {{
            style: style,
            onEachFeature: onEachFeature
        }}).addTo(map);

        var info = L.control({{position: 'topright'}});

        info.onAdd = function (map) {{
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        }};

        info.update = function (props) {{
            this._div.innerHTML = '<h4>PWC Community Opportunity Index</h4>' +  (props ?
                '<b>Census Tract: ' + props.CensusTract + '</b><br />' +
                'Opportunity Index: ' + (props.opportunity_index ? props.opportunity_index.toFixed(1) : 'N/A') + '/8'
                : 'Hover over a census tract');
        }};

        info.addTo(map);

        // District filter control - positioned on bottom (no offset)
        var districtFilter = L.control({{position: 'bottomleft'}});

        districtFilter.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'info district-filter');

            div.innerHTML = '<h4>District Filter</h4>' +
                           '<div style="margin-bottom:8px;font-size:11px;color:#9ca3af;">Click to select multiple districts:</div>';

            var districts = ['BRENTSVILLE', 'COLES', 'GAINESVILLE', 'NEABSCO', 'OCCOQUAN', 'POTOMAC', 'WOODBRIDGE'];

            districts.forEach(function(district) {{
                var filterItem = L.DomUtil.create('div', 'district-filter-item');
                filterItem.innerHTML =
                    '<div class="district-filter-color"></div>' +
                    '<div class="district-filter-text">' + district + '</div>';

                filterItem.onclick = function() {{
                    toggleDistrictFilter(district, filterItem);
                }};

                div.appendChild(filterItem);
            }});

            // Add reset button
            var resetButton = L.DomUtil.create('button', 'district-filter-reset');
            resetButton.innerHTML = 'Show All';
            resetButton.onclick = resetDistrictFilters;
            div.appendChild(resetButton);

            return div;
        }};

        districtFilter.addTo(map);

        // Service Opportunity Score Legend - positioned on top (with offset)
        var legend = L.control({{position: 'bottomleft', offset: [0, 280]}});

        legend.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'info legend');

            div.innerHTML = '<h4>Service Opportunity Score</h4>' +
                           '<div style="text-align:center;margin-bottom:8px;font-size:12px;">(higher = more opportunity)</div>' +
                           '<div style="margin-bottom:8px;font-size:11px;color:#9ca3af;">Click to select multiple scores:</div>';

            var grades = [1, 2, 3, 4, 5, 6, 7, 8];

            grades.forEach(function(grade) {{
                var legendItem = L.DomUtil.create('div', 'legend-item');
                legendItem.innerHTML =
                    '<div class="legend-color" style="background:' + getColor(grade) + '"></div>' +
                    '<div class="legend-text">' + grade + '</div>';

                legendItem.onclick = function() {{
                    toggleScoreFilter(grade, legendItem);
                }};

                div.appendChild(legendItem);
            }});

            // Add reset button
            var resetButton = L.DomUtil.create('button', 'legend-reset');
            resetButton.innerHTML = 'Show All';
            resetButton.onclick = resetAllFilters;
            div.appendChild(resetButton);

            return div;
        }};

        legend.addTo(map);

        // District coordinates
        var placeLabels = {{
            districts: [
                {{name: "Brentsville", location: [38.712300, -77.556700]}},
                {{name: "Coles", location: [38.670800, -77.405200]}},
                {{name: "Gainesville", location: [38.789200, -77.623400]}},
                {{name: "Neabsco", location: [38.645600, -77.335400]}},
                {{name: "Occoquan", location: [38.678900, -77.256700]}},
                {{name: "Potomac", location: [38.567800, -77.324500]}},
                {{name: "Woodbridge", location: [38.623400, -77.289100]}}
            ]
        }};

        var labelLayers = {{
            districts: L.layerGroup()
        }};

        function createLabels() {{
            placeLabels.districts.forEach(function(place) {{
                var icon = L.divIcon({{
                    className: 'place-label',
                    html: '<div class="district-label">' + place.name + '</div>',
                    iconSize: [130, 38],
                    iconAnchor: [65, 19]
                }});

                L.marker(place.location, {{
                    icon: icon,
                    interactive: false,
                    keyboard: false
                }}).addTo(labelLayers.districts);
            }});

            labelLayers.districts.addTo(map);
        }}

        createLabels();
        updateDistrictLabels();

        map.on('zoomend', function() {{
            var zoom = map.getZoom();
            map.addLayer(labelLayers.districts);
        }});
    </script>
</body>
</html>'''

    f.write(html_content)

# Display the map
# Ensure the HTML file exists before trying to display it
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        html_content = f.read()
    # Add CSS to remove Streamlit margins
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    components.html(html_content, width=None, height=700, scrolling=False)
else:
    st.error(f"Map HTML file not created: {output_file}")
