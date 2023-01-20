import os.path
import yaml
import types

def load_config():
    yaml_fname = 'config.yaml'
    cfg = {}

    if not os.path.isfile(yaml_fname):
        print(f"ERROR: file '{yaml_fname}' does not exist")
        return None

    with open(yaml_fname, 'r') as stream:
        try:
            cfg = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None
    
    return types.SimpleNamespace(**cfg)

cfg = load_config()



