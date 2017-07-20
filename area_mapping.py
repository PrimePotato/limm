import yaml
import os

fn = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(fn, 'r') as yml_file:
    cfg = yaml.load(yml_file)


def areacode_to_hood(ac):
    if ac in cfg['areacode_mapping']:
        return cfg['areacode_mapping'][ac]
    else:
        return None


def area_list():
    return cfg['areas']
