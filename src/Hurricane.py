# %% [markdown]
# ## Hurricane Tracking Workflow
# This notebook selects trackpoints from a features class of trackpoints for a selected storm (season & name), creates a track line, and extracts US counties that intersect that trackline. 
# 
# Fall 2026
# Peter.Sukstorf@duke.edu

# %%
#Import package
import arcpy
from pathlib import Path

#Set paths
raw_folder_path = Path.cwd().parent / 'data' / 'raw'
processed_folder_path = Path.cwd().parent / 'data' / 'processed'

#Arcpy environment settings
arcpy.env.workspace = str(raw_folder_path)
arcpy.env.overwriteOutput = True

# %%
#Set storm variable
storm_season = 2000
out_file = processed_folder_path / 'output.csv'

#Set model layers
ibtracs_NA_points = str(raw_folder_path /'IBTrACS_NA.shp')
usa_counties = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized_Boundaries/FeatureServer/0'
storm_track_points =  "memory\\track_points"
storm_track_line = "memory\\Tracklines"

#%%
storm_dict = {}

for storm_season in range(2000, 2024):
    # Create list of storm names from the IBtracs feature class in the selected season
    storm_names = [row[0] for row in arcpy.da.SearchCursor(ibtracs_NA_points, "NAME", f"SEASON = {storm_season}")]
    # Now I want only the unique values in storm_names
    storm_names = list(set(storm_names))

    print(f"Storms in {storm_season}: {storm_names}")

storm_dict[storm_season] = storm_names




# %% [markdown]
# #### Select point features corresponding to a specific storm (season & name)

# %%

for storm_season in storm_dict.keys():
    TotalCountyCount = 0
    for storm_name in storm_dict[storm_season]:
        print(f"Processing storm: {storm_name}")
        #Select points for a given storm
        arcpy.analysis.Select(
        in_features=ibtracs_NA_points, 
        out_feature_class=storm_track_points, 
        where_clause=f"SEASON = {storm_season} And NAME = '{storm_name}'"
        )

        # #### Connect Points to a Track line

        #Connect point to a track line
        arcpy.management.PointsToLine(
        Input_Features=storm_track_points,
        Output_Feature_Class=storm_track_line,
        Sort_Field='ISO_TIME'
        )

        # #### Select Counties Intersecting Point

        #Select intersecting counties
        select_output = arcpy.management.SelectLayerByLocation(
        in_layer=usa_counties, 
        overlap_type="INTERSECT", 
        select_features=storm_track_line, 
        )
        select_result = select_output.getOutput(0)

        # Print the count
        CountyCount = int(str(arcpy.management.GetCount(select_result)))
        print(f"Counties intersecting track for {storm_name}: {CountyCount}")
        TotalCountyCount += CountyCount
        
    print(TotalCountyCount)
    out_file.write(f'{storm_season},{TotalCountyCount}/n')
    # %%
