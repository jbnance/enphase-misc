#!/usr/bin/env python3

""" envoy.py

Read data from a local Enphase Envoy and write it to stdout (print it)

Usage:

    envoy.py <endpoint>

...where <endpoint> is one of:

    meter_details
    meter_readings
    inverter_production_data
    meter_live_data
    load_consumption_data
    home_json
    production_json
    production_json_details
    inventory_json
    inventory_json_deleted

Before running this script you must create a ".env" file in the same directory
as this script with:

    ENLIGHTEN_USERNAME="Enlighten username (email address)"
    ENLIGHTEN_PASSWORD="Enlighten password"
    ENVOY_SERIAL="serial number of your Envoy"
    ENVOY_HOSTNAME="hostname or IP address of your Envoy/Gateway"

Alternatively, you can use environment variables of the same names.

!!! SECURITY WARNING !!!

This script will create a "credentials.json" file in the same directory as this
script that includes an API token that can be used to access your Envoy/Gateway.
Additionally, the .env file has similar credentials.  Be careful!!  You may want
to create an additional Enlighten account and grant it read-only access to your
Envoy.

"""

import datetime
import json
import os
import sys
import traceback
from typing import Any

import jwt
import requests
from dotenv import dotenv_values
from urllib3.exceptions import InsecureRequestWarning

# Envoy uses self-signed SSL certificate
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DATA_URIS = {
    "meter_details": "/ivp/meters",
    "meter_readings": "/ivp/meters/readings",
    "inverter_production_data": "/api/v1/production/inverters",
    "meter_live_data": "/ivp/livedata/status",
    "load_consumption_data": "/ivp/meters/reports/consumption",
    "home_json": "/home.json",
    "production_json": "/production.json",
    "production_json_details": "/production.jsoni?details=1",
    "inventory_json": "/inventory.json",
    "inventory_json_deleted": "/inventory.json?deleted=1",
}

CREDENTIALS_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "credentials.json"
)


def get_token(config: dict = dotenv_values()) -> dict:
    s = requests.Session()

    # Initiate a login session
    # This is a form post, hence "data=" (not "json=")
    # A JSON string is returned in the response body
    r = s.post(
        "https://enlighten.enphaseenergy.com/login/login.json?",
        data={
            "user[email]": config["ENLIGHTEN_USERNAME"],
            "user[password]": config["ENLIGHTEN_PASSWORD"],
        },
    )

    # Example Response JSON:
    #
    # {
    #     "message": "success",
    #     "session_id": "blahblahblahhexstring",
    #     "manager_token": "big.old_long_jwt_token_here",
    #     "is_consumer": True
    # }
    login_json = json.loads(r.text)

    # Retrieve a token
    r = s.post(
        "https://entrez.enphaseenergy.com/tokens",
        json={
            "session_id": login_json["session_id"],
            "serial_num": config["ENVOY_SERIAL"],
            "username": config["ENLIGHTEN_USERNAME"],
        },
    )

    token = r.text

    # Extract the expiration
    decoded = jwt.decode(
        token,
        options={"verify_signature": False},
    )

    expiration = datetime.datetime.fromtimestamp(decoded["exp"])

    # Write credentials file
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "token": token,
                "expires": str(expiration),
                "expires_epoch": decoded["exp"],
            },
            f,
            ensure_ascii=False,
            indent=4,
        )

    return {
        "token": token,
        "expires": str(expiration),
        "expires_epoch": decoded["exp"],
    }


def read_token(config: dict = dotenv_values()) -> dict:
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        credentials = json.load(f)

    expiration = datetime.datetime.fromtimestamp(credentials["expires_epoch"])

    if expiration <= datetime.datetime.now():
        # Token is expired, attempt refresh
        credentials = get_token(config)

    return credentials


def get_data(envoy_hostname: str, endpoint: str, token: str) -> Any:
    r = requests.get(
        f"https://{envoy_hostname}{DATA_URIS[endpoint]}",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        verify=False,
    )
    return r.json()


def main(endpoint: str, config: dict = dotenv_values()) -> None:
    if endpoint not in DATA_URIS.keys():
        raise RuntimeError("Unknown endpoint")

    if os.path.isfile(CREDENTIALS_FILE):
        credentials = read_token(config)
    else:
        credentials = get_token(config)

    print(
        json.dumps(
            get_data(
                envoy_hostname=config["ENVOY_HOSTNAME"],
                endpoint=endpoint,
                token=credentials["token"],
            )
        )
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(
            f"""
Usage:
    {__file__} <endpoint>

"""
        )
        sys.exit(1)

    try:
        main(endpoint=sys.argv[1])
    except:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
