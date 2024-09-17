import typing
from typing import Dict
import requests
import os
import pytz
import datetime
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Feeding params to fetch function")
    parser.add_argument(
        "--sc_id",
        type=int,
        default=53,
        help="Study collection ID to fetch, get this from Expfactory Study Collection URL.",
    )

    parser.add_argument(
        "--battery_id",
        type=int,
        default=240,
        help="Battery ID to fetch, get this from Expfactory Deploy Battery URL.",
    )

    parser.add_argument(
        "--prolific_id",
        type=str,
        default="",
        help="Prolific ID for subject to fetch.",
    )

    parser.add_argument(
        "--exp_id",
        type=str,
        default="",
        help="Filter by exp_id.",
    )

    parser.add_argument(
        "--file_format",
        type=str,
        default="parquet",
        help="Exported data file format. Available formats include 'parquet' and 'csv'",
    )

    return parser.parse_args()

def fetch_data(SC_ID, BATTERY_ID, PROLIFIC_ID):
    API_TOKEN = os.getenv("API_TOKEN")
    tokens = [API_TOKEN]

    base_url = "https://deploy.expfactory.org/api/results/"

    params  ={}

    if SC_ID:
        params['sc_id'] = SC_ID
    if BATTERY_ID:
        params['battery_id'] = BATTERY_ID
    if PROLIFIC_ID:
        params['prolific_id'] = PROLIFIC_ID
    

    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    
    url = f"{base_url}?{query_string}" if query_string else base_url

    print(f"Fetching data from Experiment Factory... using endpoint {url}")

    with requests.Session() as sess:
        for token in tokens:
            sess.headers.update(
                {"Authorization": f"token {token}", "Cache-Control": "no-cache"}
            )
            while url:
                try:
                    response = sess.get(url)
                    response.raise_for_status()
                    data = response.json()
                    yield data
                    url = data.get("next")
                except requests.HTTPError as e:
                    if e.response.status_code == 403:
                        print(
                            f"Access forbidden with token, trying next token: {token}"
                        )
                        break
                    else:
                        print(f"HTTP error fetching data from {url}: {e}")
                        yield None
                except requests.RequestException as e:
                    print(f"Error fetching data from {url}: {e}")
                    yield None


def get_date(data: Dict) -> str:
    if "dateTime" not in data.keys():
        print("dateTime does not exist in date.keys()")
        return "N/A"
    timestamp_ms = data["dateTime"]
    timestamp_s = timestamp_ms / 1000
    # Convert to datetime
    date_time = datetime.datetime.fromtimestamp(timestamp_s)

    # Format as mm/dd/yy
    formatted_date = date_time.strftime("%m/%d/%y")
    return formatted_date