import os
import json


APP_TITLE = "Prok Viewer"
SETTINGS_PATH = os.path.abspath("user_settings/defaults.json")
LANGUAGE_PATH = os.path.abspath("assets/text_data.json")

with open(SETTINGS_PATH, 'r') as f:
    SETTINGS = json.load(f)

with open(LANGUAGE_PATH, 'r') as f:
    TEXT_DATA = json.load(f)

WINDOW_SHAPE = SETTINGS["window_shape"]
WINDOW_MIN_DIMS = SETTINGS["min_window"]

