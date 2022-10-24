# -*- coding: utf-8 -*-
"""
        @Author: Patty Jula
        @Date created: 3/2022
        @Date updated: 9/30/2022
        @Description: This script takes a data wrangled/prepared shapefile, 
        converts to a json and overwrites an existing feature layer on 
        ArcGIS Online. ARL stands for Automatic Resource Locator (ARL) in this
        example.
"""

import os
import sys

import arcgis
import arcpy
from arcgis.gis import GIS

arcpy.env.overwriteOutput = True

# profile var
ws = sys.argv[1]
loc = ws
pth = os.chdir(loc)
output_feature_class = "ARL_data.shp"
localJSON = ws + "./arl_content.json"
try:
    if os.path.isfile(localJSON):
        os.remove(localJSON)

except FileNotFoundError:
    print("Wrong file or file path")


# Truncate the existing feature layer
def TruncateWebLayer(gis=None, target=None):

    try:
        lyr = arcgis.features.FeatureLayer(target, gis)
        lyr.manager.truncate()
        print("Successfully truncated layer: " + str(target))
    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])


try:

    # LAPD log in, create a profile so you don't need to show un/pw
    mygis = GIS("https://lapd.maps.arcgis.com/", profile=sys.argv[2], verify_cert=False)

    # publishedWebLayer is the URL of a single feature layer within a collection in
    # an AGOL portal
    publishedWebLayer = r"https://services6.arcgis.com/Q18o8KwHjFGbEc4j/arcgis/rest/services/ARL_data/FeatureServer/0"

    # a feature class on the local system with the same schema as the
    # portal layer
    updateFeatures = os.path.join("E:/batch/arl/content/" + output_feature_class)

    # remove all features from the already published feature layer
    TruncateWebLayer(mygis, publishedWebLayer)

    # reference the empty layer as FeatureLayer object from the ArcGIS Python API
    fl = arcgis.features.FeatureLayer(publishedWebLayer, mygis)

    # create a JSON object from the local features
    jSON = arcpy.FeaturesToJSON_conversion(updateFeatures, localJSON)

    # create a FeatureSet object from the JSON
    fs = arcgis.features.FeatureSet.from_json(open(localJSON).read())

    # add/append the local features to the hosted feature layer
    fl.edit_features(adds=fs)

except arcpy.ExecuteError:
    print(arcpy.GetMessages())
