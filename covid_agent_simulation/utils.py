import yaml


def get_config(path):
    with open(path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as err:
            print(err)
        return config
