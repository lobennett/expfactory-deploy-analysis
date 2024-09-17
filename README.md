# Expfactory Deploy Factory Analysis

> This repository contains scripts to fetch and export data by study collection, battery ID, and/or prolific ID from [Expfactory Deploy](https://deploy.expfactory.org/).

## Steps to run locally

### 1. Clone the Repository

Clone the project repository from GitHub to your local machine using the following command:

```sh
git clone https://github.com/lobennett/expfactory-deploy-analysis.git
```

### 2. Set Up the Environment File

Navigate into the cloned directory:

```sh
cd expfactory-deploy-analysis
```

Create an .env file to store private API tokens:

```sh
touch .env
```

Open this .env file in a text editor and add the following lines, replacing [token] with actual token value from Ross/Logan:

```sh
API_TOKEN=[token]
```

### 3. Create and Activate the Virtual Environment

```sh
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### 4. Execute the script to fetch data, specifying the study collection id using --sc_id, optionally use other flags like --battery_id:

```sh
python src/fetch.py --sc_id 53 --battery_id 240
```

Note: To find the study collection ID, for example, look in the URL of the study collection page. 

For the URL https://deploy.expfactory.org/prolific/collection/53/subjects, the study collection ID is 53.

### 4. Finally, edit `preprocess_data` to handle the fetched data in whatever way you need
