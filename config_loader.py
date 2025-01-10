import json


class Loader:
    def __init__(self, owner):
        self.owner = owner

    def load_config(self, name):
        with open("jsons/config.json") as f:
            json_file = json.load(f)
        try:
            json_file["embed"]["embeds_footerpic"] = self.owner.avatar
        except:
            pass
        return json_file[name]
