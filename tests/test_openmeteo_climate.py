"""
Test open-meteo climate API:

test 1 - test initialisation of ClimateChange object.
test 2 - test download of data from open-meteo Climate API.
test 3 - test download of data from open-meteo Climate API with custom variables.
test 4 - test download of data from open-meteo Climate API with custom climate models.
test 5 - test download of data from open-meteo Climate API with custom request parameters.
test 6 - test write of downloaded Climate Change data to file.
test 7 - test conversion of downloaded Climate Change data to GLM format.
test 8 - test write of GLM formatted data to a zipfile.
test 9 - test write of GLM formatted to file. 
"""

import pytest
import tempfile
import os
import pandas as pd
import zipfile

from glm_met.openmeteo import climate_change as climate

def test_climate_init(valid_openmeteo_climate_init):
    """Test initialise climate change object"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    assert isinstance(tmp_climate, climate.ClimateChange)

def test_climate_get_data(valid_openmeteo_climate_init):
    """Test download of data from open-meteo Climate API"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)

    assert isinstance(tmp_climate.met_data.metadata, dict) and isinstance(tmp_climate.met_data.data, pd.core.frame.DataFrame)

def test_climate_get_data_custom_variables(valid_openmeteo_climate_init):
    """Test download of data from open-meteo Climate API with custom variables"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=["dewpoint_2m_min", "pressure_msl_mean"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)

    assert isinstance(tmp_climate.met_data.metadata, dict) and isinstance(tmp_climate.met_data.data, pd.core.frame.DataFrame)

def test_climate_get_data_custom_models(valid_openmeteo_climate_init):
    """Test download of data from open-meteo Climate API with custom variables"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=["dewpoint_2m_min", "pressure_msl_mean"],
        models=["CMCC_CM2_VHR4", "FGOALS_f3_H"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)

    meta_units = list(tmp_climate.met_data.metadata["daily_units"].keys())

    if ("pressure_msl_mean_CMCC_CM2_VHR4" in meta_units) and \
            ("pressure_msl_mean_FGOALS_f3_H" in meta_units) and \
                ("dewpoint_2m_min_CMCC_CM2_VHR4" in meta_units) and \
                    ("dewpoint_2m_min_FGOALS_f3_H" in meta_units):
                var_check = 1 


    assert isinstance(tmp_climate.met_data.metadata, dict) and \
          isinstance(tmp_climate.met_data.data, pd.core.frame.DataFrame) and \
          var_check == 1
    
def test_climate_get_data_custom_settings(valid_openmeteo_climate_init):
    """Test download of data from open-meteo Climate API with custom request parameters"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    settings = {
        "temperature_unit": "fahrenheit"
    }

    tmp_climate.get_variables(request_settings=settings)

    assert isinstance(tmp_climate.met_data.metadata, dict) and isinstance(tmp_climate.met_data.data, pd.core.frame.DataFrame)

def test_climate_write_met(valid_openmeteo_climate_init):
    """Test writing data downloaded from open-meteo Climate API to file"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)
    
    with tempfile.TemporaryDirectory() as f:
        tmp_climate.write_met(path=f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_raw.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_raw.zip" in f_files) and ("met_raw.csv" in f_namelist)

def test_climate_convert_to_glm(valid_openmeteo_climate_init):
    """Test converting downloaded met data to GLM format"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)
    tmp_climate.convert_to_glm()

    # check correct columns generated in DataFrames for all climate models
    matching_cols_all_models = 0
    for m in tmp_climate.models:
        src_glm = tmp_climate.glm_met_data[m]
        src_glm_cols = src_glm.columns
        target_glm_cols = [
            "time",
            "ShortWave",
            "Cloud",
            "AirTemp",
            "RelHum",
            "WindSpeed",
            "Rain"
        ]
        matching_cols = [c for c in src_glm_cols if c  in target_glm_cols]
        if len(matching_cols) == 7:
             matching_cols_all_models += 1
    
    assert (matching_cols_all_models == len(tmp_climate.models)) 

def test_climate_write_glm_zip(valid_openmeteo_climate_init):
    """Test writing GLM formatted data file - zip"""
    tmp_climate = climate.ClimateChange(
        location=(valid_openmeteo_climate_init["longitude"], valid_openmeteo_climate_init["latitude"]),
        date_range=valid_openmeteo_climate_init["date_range"],
        variables=valid_openmeteo_climate_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_climate.get_variables(request_settings=None)
    tmp_climate.convert_to_glm()
    
    with tempfile.TemporaryDirectory() as f:
        tmp_climate.write_glm_met(f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_glm.zip"), "r") as ff:
            f_namelist = ff.namelist()
            model_check = True
            for m in tmp_climate.models:
                 if f"met_{m}.csv" not in f_namelist:
                      model_check = False
    
    assert ("met_glm.zip" in f_files) and (model_check)

