import json
from pathlib import Path

CONFIG_PATH = Path.home() / '.flight_alerts_config.json'

DEFAULT = {
    'gmail': '',
    'gmail_app_password': '',
    'alerts': [],
    'check_interval_hours': 4,
    'pos_x': 100,
    'pos_y': 100,
}

def load():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return {**DEFAULT, **json.load(f)}
    return DEFAULT.copy()

def save(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
