"""
Test open-meteo historical API:

test 1 - test initialisation of Historical object.
test 2 - test download of hourly data from open-meteo Historical API.
test 3 - test download of data from open meteo Historical API 
    with custom request settings passed in as query parameters
    and changing timezone.
test 4 - test download of daily data from open-meteo Historical API.
test 5 - test download of daily data from open-meteo Historical API
    with user selected weather variables.
test 6 - test write raw downloaded meteorological data to file.
test 7 - test convert data from open-meteo Historical API to GLM format.
test 8 - test writing GLM formatted data to a zipfile.
test 9 - test writing GLM formatted data to file.
"""

import pytest
import tempfile
import os
import pandas as pd
import zipfile

from glm_met.openmeteo import historical

def test_historical_init(valid_openmeteo_historical_init):
    """Test initialise histoical object"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    assert isinstance(tmp_historical, historical.Historical)

def test_historical_get_data(valid_openmeteo_historical_init):
    """Test download of data from open-meteo Historical API"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_historical.get_variables(request_settings=None)

    assert isinstance(tmp_historical.met_data.metadata, dict) and isinstance(tmp_historical.met_data.data, pd.core.frame.DataFrame)

def test_historical_get_data_custom_settings(valid_openmeteo_historical_init):
    """Test download of data from open-meteo Historical API
    
    Pass in custom settings and set timezone.

    """
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None,
        timezone="Australia/Sydney"
    )

    settings = {
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch" 
    }

    tmp_historical.get_variables(request_settings=settings)

    assert isinstance(tmp_historical.met_data.metadata, dict) and isinstance(tmp_historical.met_data.data, pd.core.frame.DataFrame)

def test_historical_get_data_daily(valid_openmeteo_historical_init):
    """Test download of daily data from open-meteo Historical API

    Get daily data using default daily variables from settings.py. 
    """
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=None,
        met_data=None,
        glm_met_data=None,
        timezone="Australia/Sydney",
        hourly=False
    )

    tmp_historical.get_variables(request_settings=None)

    target_cols = [
    "shortwave_radiation_sum",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "windspeed_10m_max",
    "precipitation_sum",
    "et0_fao_evapotranspiration"
    ]   

    src_cols = tmp_historical.met_data.data.columns

    matching_cols = [c for c in src_cols if c in target_cols]


    assert isinstance(tmp_historical.met_data.metadata, dict) \
        and isinstance(tmp_historical.met_data.data, pd.core.frame.DataFrame) \
        and (len(matching_cols) == 7)
    
def test_historical_get_data_daily_custom_variables(valid_openmeteo_historical_init):
    """Test download of daily data from open-meteo Historical API

    Get daily data using default daily variables from settings.py. 
    """
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=["shortwave_radiation_sum"],
        met_data=None,
        glm_met_data=None,
        timezone="Australia/Sydney",
        hourly=False
    )

    tmp_historical.get_variables(request_settings=None)

    target_cols = [
    "shortwave_radiation_sum"
    ]   

    src_cols = tmp_historical.met_data.data.columns

    matching_cols = [c for c in src_cols if c in target_cols]


    assert isinstance(tmp_historical.met_data.metadata, dict) \
        and isinstance(tmp_historical.met_data.data, pd.core.frame.DataFrame) \
        and (len(matching_cols) == 1)
        
def test_historical_write_met(valid_openmeteo_historical_init):
    """Test writing data downloaded from open-meteo Historical API to file"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_historical.get_variables(request_settings=None)
    
    with tempfile.TemporaryDirectory() as f:
        tmp_historical.write_met(path=f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_raw.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_raw.zip" in f_files) and ("met_raw.csv" in f_namelist)

def test_historical_convert_to_glm(valid_openmeteo_historical_init):
    """Test converting downloaded met data to GLM format"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_historical.get_variables(request_settings=None)
    tmp_historical.convert_to_glm()
    src_glm_cols = tmp_historical.glm_met_data.columns
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
    
    assert (len(matching_cols) == 7) and (tmp_historical.met_data.data.shape[0] == tmp_historical.glm_met_data.shape[0])

def test_historical_write_glm_zip(valid_openmeteo_historical_init):
    """Test writing GLM formatted data file - zip"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_historical.get_variables(request_settings=None)
    tmp_historical.convert_to_glm()
    
    with tempfile.TemporaryDirectory() as f:
        tmp_historical.write_glm_met(f, True, None)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_glm.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_glm.zip" in f_files) and ("met.csv" in f_namelist)

def test_historical_write_glm(valid_openmeteo_historical_init):
    """Test writing GLM formatted data file"""
    tmp_historical = historical.Historical(
        location=(valid_openmeteo_historical_init["longitude"], valid_openmeteo_historical_init["latitude"]),
        date_range=valid_openmeteo_historical_init["date_range"],
        variables=valid_openmeteo_historical_init["variables"],
        met_data=None,
        glm_met_data=None
    )

    tmp_historical.get_variables(request_settings=None)
    tmp_historical.convert_to_glm()
    
    with tempfile.TemporaryDirectory() as f:
        tmp_historical.write_glm_met(f, False, "test.csv")
        f_files = os.listdir(f)
    
    assert ("test.csv" in f_files)