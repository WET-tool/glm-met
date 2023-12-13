# GLM-met

A Python package for downloading meteorological data and processing it to formats required for running the <a href="https://github.com/AquaticEcoDynamics/glm-aed/tree/main/binaries" target="_blank">GLM model</a> and other water balance models.

## GLM 

GLM is a 1-dimensional lake water balance and stratification model. It is coupled with a powerful ecological modelling library to also support simulations of lake water quality and ecosystems processes.

GLM is suitable for a wide range of natural and engineered lakes, including shallow (well-mixed) and deep (stratified) systems. The model has been successfully applied to systems from the scale of individual ponds and wetlands to the scale of Great Lakes.

For more information about running GLM please see the model website's <a href="https://aed.see.uwa.edu.au/research/models/glm/overview.html" target="_blank">scientific basis description</a> and the <a href="https://aquaticecodynamics.github.io/glm-workbook/" target="_blank">GLM workbook</a>. 

The <a href="https://github.com/AquaticEcoDynamics/glm-aed/tree/main/binaries" target="_blank">GLM model</a> is available as an executable for Linux (Ubuntu), MacOS, and Windows. It is actively developed by the 
Aquatic EcoDynamics research group at The University of Western Australia.

## Install

```
pip install glm-met
```

## Use

Import the glm-met package into a Python program and use to download meteorological data from a supported data provider.

The following Jupyter notebook can be opened on Google Colab to demonstrate how glm-met can be used to download meteorological data from NASA POWER's API:

<a href="https://colab.research.google.com/github/WET-tool/glm-met/blob/main/example-use.ipynb" target="_blank">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

```
import os
import glm_met.nasa_power.nasa_power as nasa_power

# initialise a Power object
# the object attributes are set to:
# - query the NASA POWER API 
# - query for hourly met data from 2020 to 2022
# - query a location in Western Australia

power = nasa_power.Power(
    location=(116.6, -32.17), 
    date_range=("20200101", "20221231"), 
    met_data=None,
    glm_met_data=None,
    parameters=None,
)

# make a call to the NASA POWER API
# download requested data and store as DataFrame
# in the `power.met_data.data` attribute
power.get_variables(request_settings=None)

# convert downloaded data to GLM format
power.convert_to_glm()

# write downloaded data to disk
power.write_glm_met(path=os.getcwd(), zip_f=False, fname="met.csv")
```

## Data Providers

glm-met provides a base class that can be extended to support a range of meteorological data providers. 

### SILO

<a href="https://www.longpaddock.qld.gov.au/silo/" target="_blank">SILO</a> is a database of daily, pre-processed Australian climate data from 1889 to the present day. The product is hosted by the Queensland Department of Environment and Science (DES) and is based on observational data from the Bureau of Meteorology and other providers. It is made available under the <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Attribution 4.0 International (CC BY 4.0)</a> licence. 

glm-met retrieves SILO data from the patched point dataset (weather station data) and the drill down (point-like data extracted from a gridded product). 

### NASA POWER

<a href="https://power.larc.nasa.gov/docs/" target="_blank">NASA Prediction of Worldwide Energy Resources (POWER)</a> provides solar and meteorological data available at monthly, daily, and hourly time steps via the NASA POWER Data Services API. The NASA POWER project is funded by NASA's Applied Science Program and the data is available from the 1980s until near real time. The solar radiation data is derived from several remote sensing-based products at a 1.0° grid cell spatial resolution. The meteoroloical data is based on GMAO MERRA-2 reanalysis and assimilation of observations data at a 0.5° grid cell spatial resolution. 

The hourly data from NASA POWER is available from 2001. Currently, glm-met provides tools to retrieve hourly data from the NASA POWER API. 

