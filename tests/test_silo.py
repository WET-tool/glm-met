import pytest
import tempfile
import os
import pandas as pd
import zipfile

import glm_met.silo.silo as silo

def test_silo_init():
    """Test initialise Silo object"""
    tmp_silo = silo.Silo(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None, 
        comment="rxel",
        username="testing-glm-met@pytest.com", 
        api="data_drill"
    )

    assert isinstance(tmp_silo, silo.Silo)


def test_silo_drill_down():
    """Test download of data from SILO drill down"""
    tmp_silo = silo.Silo(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None, 
        comment="rxel",
        username="testing-glm-met@pytest.com", 
        api="data_drill"
    )

    tmp_silo.get_variables(request_settings=None)

    assert isinstance(tmp_silo.met_data.metadata, dict) and isinstance(tmp_silo.met_data.data, pd.core.frame.DataFrame)


def test_silo_patch_point():
    """Test download of data from SILO patch point"""
    tmp_silo = silo.Silo(
        location=31011, 
        date_range=("20220101", "20220131"), 
        met_data=None, 
        comment="rxel",
        username="testing-glm-met@pytest.com", 
        api="patch_point"
    )

    tmp_silo.get_variables(request_settings=None)

    assert isinstance(tmp_silo.met_data.metadata, dict) and isinstance(tmp_silo.met_data.data, pd.core.frame.DataFrame)


def test_silo_drill_down_write_met():
    """Test writing data downloaded from SILO API to file"""
    tmp_silo = silo.Silo(
        location=(116.6, -32.17), 
        date_range=("20220101", "20220131"), 
        met_data=None,
        comment="rxel",
        username="testing-glm-met@pytest.com", 
        api="data_drill"
    )

    tmp_silo.get_variables(request_settings=None)
    
    with tempfile.TemporaryDirectory() as f:
        tmp_silo.write_met(path=f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_raw.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_raw.zip" in f_files) and ("met_raw.csv" in f_namelist)


def test_silo_patch_point_write_met():
    """Test writing data downloaded from SILO API to file"""
    tmp_silo = silo.Silo(
        location=31011, 
        date_range=("20220101", "20220131"), 
        met_data=None, 
        comment="rxel",
        username="testing-glm-met@pytest.com", 
        api="patch_point"
    )

    tmp_silo.get_variables(request_settings=None)
    
    with tempfile.TemporaryDirectory() as f:
        tmp_silo.write_met(path=f)
        # check zipfile in tmp dir
        f_files = os.listdir(f)
        with zipfile.ZipFile(os.path.join(f, "met_raw.zip"), "r") as ff:
            f_namelist = ff.namelist()
    
    assert ("met_raw.zip" in f_files) and ("met_raw.csv" in f_namelist)