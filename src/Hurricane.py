# %% [markdown]
# ## Hurricane Tracking Workflow
# This notebook selects trackpoints from a features class of trackpoints for a selected storm (season & name), creates a track line, and extracts US counties that intersect that trackline. 
# 
# Fall 202X  
# John.Fay@duke.edu

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
storm_season = 2024
storm_name = "HELENE"
affected_counties = processed_folder_path / 'affected_counties.shp'

#Set model layers
ibtracs_NA_points = str(raw_folder_path /'IBTrACS_NA.shp')
usa_counties = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized_Boundaries/FeatureServer/0'
storm_track_points =  "memory\\track_points"
storm_track_line = "memory\\Tracklines"

# %% [markdown]
# #### Select point features corresponding to a specific storm (season & name)

# %%
#Select points for a given storm
arcpy.analysis.Select(
    in_features=ibtracs_NA_points, 
    out_feature_class=storm_track_points, 
    where_clause=f"SEASON = {storm_season} And NAME = '{storm_name}'"
)

# %% [markdown]
# #### Connect Points to a Track line

# %%
#Connect point to a track line
arcpy.management.PointsToLine(
    Input_Features=storm_track_points,
    Output_Feature_Class=storm_track_line,
    Sort_Field='ISO_TIME'
)

# %% [markdown]
# #### Select Counties Intersecting Point

# %%
#Select intersecting counties
select_output = arcpy.management.SelectLayerByLocation(
    in_layer=usa_counties, 
    overlap_type="INTERSECT", 
    select_features=storm_track_line, 
    )
select_result = select_output.getOutput(0)

# %%
#Copy selected counties to output feature class
arcpy.management.CopyFeatures(
    in_features = select_result, 
    out_feature_class = str(affected_counties)
)


