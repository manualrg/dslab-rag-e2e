"""
Configuration loader module.

This module provides a way to load YAML configuration files into Pydantic
models and nd is designed to be easily extendable by adding new config files and models.

Usage:
    from src import conf

    # Load infrastructure configuration
    infra_conf = conf.load(file=conf.ConfigFiles.INFRA.value)

    # Load settings configuration
    settings_conf = conf.load(file=conf.ConfigFiles.SETTINGS.value)

Extending:
    1. Add a new Enum entry to `ConfigFiles`.
    2. Define a corresponding Pydantic model.
    3. Add the new mapping in `ConfigFiles.get_pydantic_models`.
    4. Place the YAML file in your `utils.path_conf` folder.

Example YAML (`infra.yaml`):
    param1: 123
"""

from pathlib import Path
from enum import Enum
import yaml
import logging
from pydantic_settings import BaseSettings

from src import utils

logger = logging.getLogger(__name__)

def example():
    logger.info("conf.example")
    print("conf.example")


class Settings(BaseSettings):
    param1: int

class Infra(BaseSettings):
    param1: int


class ConfigFiles(Enum):
    INFRA = "infra.yaml"
    SETTINGS = "settings.yaml"

    @classmethod
    def get_pydantic_models(cls):
        return {cls.INFRA: Infra,
                cls.SETTINGS: Settings,
                }
    

def load(path: Path = utils.path_conf, file: str = ConfigFiles.INFRA.value) -> BaseSettings:

    config_models = ConfigFiles.get_pydantic_models()
    filename_conf = path / file


    if not path.exists():
         raise FileNotFoundError(f"Config folder {path.as_posix()} not found!")
    
    if not filename_conf.exists():
        raise FileNotFoundError(f"Config file {filename_conf.as_posix()} not found!")
    
    try:
        config_model = ConfigFiles(file)
    except Exception as err:
        raise ValueError(f"Config file {file} not listed in `ConfigFiles`. Error: {err}")
    
    try:
        with filename_conf.open("r") as f:
            data = yaml.safe_load(f)
    except Exception as err:
        raise IOError(f"Could not read {filename_conf.as_posix()}: {err}")

    try:
        conf =  config_models[config_model](**data)
    except KeyError as err:
        raise KeyError(f"{file=} not found in {config_models=}. Error: {err}")
    except Exception as err:
        logger.error("ERROR: Failed to parse the conf file .yaml")  # catches Pydantic errors
        raise err
    
    return conf
  

