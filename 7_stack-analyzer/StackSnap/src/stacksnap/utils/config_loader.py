import os
import yaml

def load_config(config_file_path: str = r"stacksnap\config\config.yaml") -> dict:
    with open(config_file_path, "r") as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    cfg = load_config()
    print("✅ Loaded config:", cfg)
