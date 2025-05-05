import json, os

def load_config(name) -> dict:
    """
    Load the configuration file.
    """
    path = os.path.join(os.path.dirname(__file__), '../Configs')
    name = f"{name}.json"
    
    file_name_and_path = os.path.join(path, name)
    print(f"Looking for config file at: {file_name_and_path}")  # Debugging

    if not os.path.exists(file_name_and_path):
        raise FileNotFoundError(f"Configuration file {name} not found in {path}.")
    with open(file_name_and_path,'r') as f:
        return json.load(f)