# GLM-met

A Python package for downloading meteorological data and processing it to formats required for running the <a href="https://github.com/AquaticEcoDynamics/glm-aed/tree/main/binaries" target="_blank">GLM model</a>.

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

The following Jupyter notebook can be opened on Google Colab to demonstrate how glm-met can be used to download meteorological data from open-meteo's Historical API:

<a href="https://colab.research.google.com/github/WET-tool/glm-met/blob/main/example-use.ipynb" target="_blank">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

```
import os
import glm_met.openmeteo.historical as historical

# initialise a Historical object
# the object attributes are set to:
# - query the open-meteo Historical API 
# - query for hourly met data from 1970 to 2022
# - query a location in Western Australia
hist = historical.Historical(
            location=(116.691155, -34.225812),
            date_range=("1970-01-01", "2022-12-31"),
            variables=["temperature_2m", "relativehumidity_2m"],
            met_data=None,
            glm_met_data=None
        )

# make a call to the open-meteo Historical API
# download requested data and store as DataFrame
# in the `hist.met_data.data` attribute
hist.get_variables()

# convert downloaded data to GLM format
hist.convert_to_glm()

# write downloaded data to disk
hist.write_glm_met(path=os.getcwd(), zip_f=False, fname="met.csv")
```

## Data Providers

glm-met provides a base class that can be extended to support a range of meteorological data providers. 

### open-meteo

Currently, the <a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank">open-meteo Historical API</a> and <a href="https://open-meteo.com/en/docs/climate-api" target="_blank">open-meteo Climate API</a> are supported.

The **Historical API** can be used to download daily and hourly data for any location since 1940. It provides access to a range of weather variables including air temperature, relative humidity, dewpoint temperature, apparent temperature, precipitation, sealevel and surface pressure, cloud cover, evapotranspiration, vapor pressure deficit, and wind speed. The data is based on the ERA5 (25 km Global coverage), ERA5-Land (10 km Global land coverage), and CERRA (5 km Europe) reanalysis models. 

The **Climate API** provides access to downscaled data from seven climate models. Daily future climate data can be accessed through till 2050. 

The open-meteo API is available for non-commericial use for up to 10,000 daily API calls under a <a href="https://open-meteo.com/en/terms" target="_blank">CC-BY 4.0 license</a>. For commericail uses, pass in an API key to calls to the open-meteo API via the `get_variables()` method of the `Historical` and `ClimateChange` classes.  
