import os
import json


_DIR = os.path.dirname(__file__)


def load_data(filename):
    path = os.path.join(_DIR, filename)
    with open(path) as json_file:
        return json.load(json_file)
