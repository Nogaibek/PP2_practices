from configparser import ConfigParser
import os

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)

    print("Reading config from:", full_path) 

    parser.read(full_path)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {full_path}')

    return config