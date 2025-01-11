"""
config_loader.py
This module contains the Loader class
which is responsible for loading and modifying configuration files.
"""

import json

class Loader:
    """
    A class used to load and modify configuration files.

    Attributes
    ----------
    owner : object
        The owner object which contains the avatar attribute.

    Methods
    -------
    load_config(name)
        Loads the configuration file and modifies it with the owner's avatar.
    """

    def __init__(self, owner):
        """
        Parameters
        ----------
        owner : object
            The owner object which contains the avatar attribute.
        """
        self.owner = owner

    def load_config(self, name):
        """
        Loads the configuration file and modifies it with the owner's avatar.

        Parameters
        ----------
        name : str
            The name of the configuration to be loaded.

        Returns
        -------
        dict
            The modified configuration dictionary.
        """
        with open("jsons/config.json") as f:
            json_file = json.load(f)
        try:
            json_file["embed"]["embeds_footerpic"] = self.owner.avatar
        except:
            pass
        return json_file[name]
