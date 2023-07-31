#!/usr/bin/env python3

""" panel-json-to-yaml.py

Read a Envoy panel.json file and write YAML version of it.

This can be helpful when generating an Envoy Logger configuration file.

"""

import json
from collections import OrderedDict

import yaml

with open("panel.json", "r") as f:
    panel_json = json.load(f)

config = {}

for module in panel_json["arrays"][0]["modules"]:
    config[module["inverter"]["serial_num"]] = {
        "tags": {
            "module_id": module["module_id"],
            "x": module["x"],
            "y": module["y"],
            "inverter_id": module["inverter"]["inverter_id"],
        },
    }

# Sort by x then y
# This returns a list of tuples for some reason
sorted_config = sorted(
    config.items(), key=lambda i: (i[1]["tags"]["y"], i[1]["tags"]["x"])
)

config = OrderedDict()

for c in sorted_config:
    config[c[0]] = c[1]

print(yaml.dump(config))
