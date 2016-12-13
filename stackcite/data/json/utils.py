import json
import pkg_resources


def load_data(filename):
    path = 'data/json/' + filename
    json_data = pkg_resources.resource_string('stackcite', path)
    return json.loads(json_data.decode('utf-8'))
