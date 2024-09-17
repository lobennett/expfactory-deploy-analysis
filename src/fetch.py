import pandas as pd
import ast
import json
import os
import numpy as np
from dotenv import load_dotenv
from utils import fetch_data, get_date, create_parser

def robust_converter(item):
    if isinstance(item, list):
        return str(item) 
    elif isinstance(item, np.ndarray):
        return item.tolist()  
    else:
        return item if pd.isna(item) else str(item)

def preprocess_data(data: dict, outdir: str, file_format: str, target_exp_id: str):
    """
    Preprocess fetched JSON data from the Expfactory Deploy API and save each
    experiment's results as a CSV file in the specified output directory.

    This is an example of how I might go about fetching and preprocessing data
    for the sc with ID 52 (called "[main] RDoC Set 1").

    PS: I wrote this pretty quickly so it might not be entirely robust,
    just think of it as template for getting started.

    """

    results = data.get("results", [])

    for res in results:
        prolific_id = res.get("prolific_id", "")
        battery_name = res.get("battery_name", "").replace("[main] Set 1 ", "").replace(" ", "_")

        # Attempt to parse the data field into a dictionary
        try:
            data_dict = ast.literal_eval(res.get("data", ""))
        except ValueError as e:
            print(f"Failed to parse data for {prolific_id}: {e}. Skipping.")
            continue

        print(f"Processing: {prolific_id} - {battery_name}")

        # Date when subject submitted battery data
        date = get_date(data_dict)
     
      
        try:
            # Check if 'trialdata' is a string and parse it
            trial_data_raw = data_dict.get("trialdata", "{}")
            if isinstance(trial_data_raw, str):
                trialdata = json.loads(trial_data_raw)
                df = pd.DataFrame(trialdata)
                if not df.empty:
                    if "exp_id" in df.columns and not df['exp_id'].isna().all():
                        exp_id = df.get("exp_id", "").dropna().iloc[0]
                    else:
                        print("Warnings: exp_id not found in task df. Using expfactory deploy object instead.")
                        exp_id = res.get("exp_name", "na")
                        

                    if target_exp_id:
                        if target_exp_id != exp_id:
                            continue

                    print(f"Processing experiment: {exp_id}")

                    ## OPTIONAL: Appending completion date to dataframe from expfactory deploy object
                    if date:
                        df['completion_date'] = np.nan
                        df['completion_date'] = df['completion_date'].astype('object')
                        df.iloc[0, df.columns.get_loc('completion_date')] = date

                    if file_format == "csv":
                        filename = f'{battery_name}_{prolific_id}_{exp_id}.csv'
                        filepath = os.path.join(outdir, filename)
                        df.to_csv(filepath, index=False)
                        print(f"Saved data file to {filepath}")
                    elif file_format == "parquet":
                        filename = f'{battery_name}_{prolific_id}_{exp_id}.parquet'
                        filepath = os.path.join(outdir, filename)
                        if df['response'].apply(lambda x: isinstance(x, dict)).any():
                            df['response'] = df['response'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)

                        df['stimulus'] = df['stimulus'].apply(robust_converter)
                        df.to_parquet(filepath, index=False)
                        print(f"Saved data file to {filepath}")
                    else: 
                        print("Invalid file format. Use 'csv' or 'parquet'.")
            else:
                print(
                    f"Unexpected type for trialdata in data for {prolific_id}. Expected a JSON string."
                )
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {prolific_id}: {e}")
        except KeyError as e:
            print(f"Key error: {e} - Possible missing keys in data for {prolific_id}")


def main():
    """

    Fetch data from Expfactory Deploy API. Ping me (Logan) for API_TOKEN. 

    """

    outdir = "./out/"

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Parse the arguments
    args = create_parser()

    load_dotenv()

    for data in fetch_data(args.sc_id, args.battery_id, args.prolific_id):
        preprocess_data(data, outdir, args.file_format, args.exp_id)


if __name__ == "__main__":
    main()
