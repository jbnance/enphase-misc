#!/usr/bin/env python3

""" panel-json-to-csv.py

Read a Envoy panel.json file and write a CSV version of it.

This can be helpful when assigning row/col labels for your panels such as what
is used by Envoy Logger.

"""

import csv
import json
from collections import OrderedDict

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

with open("panel.csv", "w") as f:
    c = csv.writer(f)
    c.writerow(["Serial", "X", "Y"])
    for panel in config.items():
        c.writerow([f"'{panel[0]}", panel[1]["tags"]["x"], panel[1]["tags"]["y"]])
