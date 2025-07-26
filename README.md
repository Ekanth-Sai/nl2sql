# File functions
## config.py
Has application configuration settings. Includes Gemini API, and MySQL db creds (Should be changed  while deployment)

## db_manager.py
Database interaction layer of the application. Handles connectivity, query execution, retireval operation for MySQL

## nl_to_sql.py
Converts user nl queries to MySQL queries

<br>

# How to execute
## Clone the repo
`git clone https://github.com/Ekanth-Sai/nl2sql.git`

## Create a virtual environment 
`python3 -m venv venvname`

## Activate the virtual environment
`source venvname/bin/activate`

## Install the libraries
Libraries have been included in the `requirements.txt`
`pip install -r requirements.txt`

## Run the application
`python3 main.py`

### `.env` file will be sent separately