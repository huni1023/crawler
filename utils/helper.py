import json
import yaml
import pickle


def load_config(config_path: str) -> dict:
    r"""A simple function to load yaml configuration file
    Parameters
    ----------
    config_path : str
        the path of yaml configuration file
    """
    with open(config_path) as file:
        config = yaml.safe_load(file)

    return config


def load_json(json_path: str) -> dict:
    r"""A simple function to load json file
    Parameters
    ----------
    json_path : str
        the path of json file
    """
    with open(json_path) as openfile:
        json_obj = json.load(openfile)
    
    return json_obj


def load_pickle(pickle_path: str):
    r"""A simple function to load pickle file
    Parameters
    ----------
    pickle_path : str
        the path of pickle file
    """
    pk = open(pickle_path, 'rb')
    pk_obj = pickle.load(pk)
    pk.close()

    return 