# GLM-met

## Developing

### Environment

A Docker container can be used to create a development environment. You can either build the Docker image:

```
docker build -t glm-met-dev .devcontainer
```
Or, you can develop glm-met using a dev container. 

### Code style

Code linting and formatting uses ruff and black. A script to format the glm-met repository can be run: `./scripts/format.sh`. 

pre-commit is used to run ruff and black. 

## Tests

<a href="https://docs.pytest.org/en/7.4.x/" target="_blank">pytest</a> is used for testing glm-met. 

If testing, please add tests under the `tests` directory. If you need test data for running tests, add them as `pytest.fixtures` in `conftest.py`. 

## Extending

The glm-met package can be extended to support downloading data from a range of meteorological data providers. 

There are two base classes that can be extended to provide with functionality for a new meteorological data provider. Theses base classes can be found in `glm_met/glm_met.py`.

Specifically, there is a base class `GlmMet` that should be extended to define a class that comprises attributes and methods necessary to retrieve meteorological data from a specific data provider. This base class has four abstract methods that any class inheriting `GlmMet` must override and provide an implementation for:

* `get_variables()` - a method to download requested weather variables from a data provider.
* `write_met()` - a method to write data downloaded from a data provider to disk.
* `convert_to_glm()` - a method to convert data downloaded from a data provider to GLM format.
* `write_glm_met()` - a method to write meteorological data in GLM format to disk. 

Overriding, and providing an implementation for these methods, these methods ensures that the class for a new meteorological data provider offers functionality to retrieve user / client requested data and format this data ready for GLM. 

The typical development pattern for a new meteorological data provider (e.g. open-meteo's Climate API) is:

Create a new directory and package for the new data provider inside the `glm_met` directory:

```
glm_met/
    openmeteo/
        __init__.py
    __init__.py
    glm_met.py
```

Create a new module within the `openmeteo` directory (e.g. named `climate.py`):

```
glm_met/
    openmeteo/
        __init__.py
        climate.py
    __init__.py
    glm_met.py
```

In `climate.py` create a new class that extends the `GlmMet` base class (which is defined in `glm_met.py`):

```
# add to climate.py
from glm_met import glm_met

class MetData(glm_met.MetData):
    def __init__(self, metadata: dict, data: pd.DataFrame):
        """
        Class for meteorological data and its associated metadata.

        Used within instances of `ClimateChange` class to store
        meteoroligcal data downloaded from the open-meteo
        climate API.
        """
        self.metadata = metadata
        self.data = data


class ClimateChange(glm_met.GlmMet):
    """
    Class for retrieving and processing daily climate change data from
    open-meteo's Climate API.
    """


    def __init__(
        self,
    ):
        """
        Initialize the `ClimateChange` object for retrieving and storing
        meteorological data from open-meteo's Climate API.
        """
    
        def get_variables(self) -> None:
            """Override GlmMet.get_variables() with implementation to 
            get variables from weather data provider."""
            # implementation here

        def write_met(self) -> None:
            """Override GlmMet.write_met() with implementation to
            save weather data from data provider."""
            # implementation here

        def convert_to_glm(self) -> None:
            """Override GlmMet.convert_to_glm() with implementation to
            convert weather data to GLM format."""
            # implementation here

        def write_glm_met(self) -> None:
            """Override GlmMet.write_glm_met() with implementation to
            save weather data in GLM format."""
            # implementation here

```