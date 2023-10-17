import glm_met.silo.silo as silo
import pandas as pd
from io import StringIO

s = silo.Silo(
    location=(116.6, -32.17), 
    date_range=("20220101", "20220131"), 
    met_data=None, 
    format="csv",
    comment="rxel",
    username="john.duncan@uwa.edu.au", 
    api="data_drill"
)

s.get_variables(request_settings=None)

print(s.met_data.data)
print(s.met_data.metadata)

s = silo.Silo(
    location=31011, 
    date_range=("20220101", "20220131"), 
    met_data=None, 
    format="csv",
    comment="rxel",
    username="john.duncan@uwa.edu.au", 
    api="patch_point"
)

s.get_variables(request_settings=None)

print(s.met_data.data)
print(s.met_data.metadata)

