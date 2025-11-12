import json
import os
import yaml
from dotenv import load_dotenv

load_dotenv()


_config = None

def load_config():
    """
    Loads the configuration file for the application, caching it after the first read.

    This function reads the 'config.yaml' file located in the same directory as this script.
    On the first call, it loads the file, caches it, and returns the result. On subsequent
    calls, it returns the cached configuration object directly without re-reading the file.
    
    The configuration file is expected to be in YAML format. The function logs the process
    and returns the configuration as a dictionary. If an error occurs during the initial load,
    it is logged and a RuntimeError is raised.

    Returns
    -------
    dict
        The configuration data loaded from the YAML file.

    Raises
    ------
    RuntimeError
        If there is an error reading or parsing the configuration file on the first attempt.
    """
    global _config

    # If the config has already been loaded, return the cached version.
    if _config is not None:
        return _config

    # The rest of the function executes only on the first call.
    try:
        # config.yaml will be replaced from 'cgf-ckms-config' repository at the time of deployment
        SCRIPT_DIR_MAIN = os.path.dirname(os.path.abspath(__file__))
        CONFIG_PATH = os.path.join(SCRIPT_DIR_MAIN, 'config.yaml')

        with open(CONFIG_PATH, "r", encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)
        
        # Cache the loaded config in the module-level variable
        _config = config
        
        return _config

    except Exception as e:
        # Use print instead of logger to avoid circular dependency
        print(f"ERROR: An {type(e).__name__} occurred while reading config: {str(e)}")
        raise RuntimeError(f"An error occurred while reading config : {str(e)}")
    
    
    
# config = load_config()
# print(config)