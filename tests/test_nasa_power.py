import pytest
import tempfile
import os
import pandas as pd
import zipfile

import glm_met.nasa_power.nasa_power as nasa_power

def test_np_init():
    """Test initialise Power object"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None,
    )

    assert isinstance(tmp_power, nasa_power.Power)


def test_nasa_power_download():
    """Test download of data from NASA POWER"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None,
    )

    tmp_power.get_variables(request_settings=None)

    assert isinstance(tmp_power.met_data.metadata, dict) and isinstance(tmp_power.met_data.data, pd.core.frame.DataFrame)


def test_nasa_power_write_met():
    """Test writing data downloaded from NASA POWER to file"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None, 
    )

    tmp_power.get_variables(request_settings=None)
    
    with tempfile.TemporaryDirectory() as f:
        tmp_power.write_met(path=f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_raw.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_raw.zip" in f_files) and ("met_raw.csv" in f_namelist)


def test_nasa_power_convert_to_glm():
    """Test converting downloaded met data to GLM format"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None, 
    )

    tmp_power.get_variables(request_settings=None)
    tmp_power.convert_to_glm()
    src_glm_cols = tmp_power.glm_met_data.columns
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
    
    assert (len(matching_cols) == 7) and (tmp_power.met_data.data.shape[0] == tmp_power.glm_met_data.shape[0])

def test_nasa_power_write_glm_zip():
    """Test writing GLM formatted data file - zip"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None, 
    )

    tmp_power.get_variables(request_settings=None)
    tmp_power.convert_to_glm()
    
    with tempfile.TemporaryDirectory() as f:
        tmp_power.write_glm_met(f, True, None)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_glm.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_glm.zip" in f_files) and ("met.csv" in f_namelist)

def test_nasa_power_write_glm():
    """Test writing GLM formatted data file"""
    tmp_power = nasa_power.Power(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        glm_met_data=None,
        parameters=None, 
    )

    tmp_power.get_variables(request_settings=None)
    tmp_power.convert_to_glm()
    
    with tempfile.TemporaryDirectory() as f:
        tmp_power.write_glm_met(f, False, "test.csv")
        f_files = os.listdir(f)
    
    assert ("test.csv" in f_files)