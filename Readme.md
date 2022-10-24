# Stock Trade

## Pre-requisites

This application is supported on all the platforms, provided docker is installed.
Download and Install Docker from https://docs.docker.com/get-docker/

###    For macOS and Linux

Execute _./run.sh_ 

###    For Windows

Execute _./run.ps1_ file

Access the application at http://127.0.0.1:5001


#### In case docker is not available, 
 
1. Download and Install PostgreSQL from https://www.postgresql.org/download/
2. Create a DB user "admin" and a database "stock_trade"
3. Run _config/init_db.sql_ file
4. Download and Install Python from https://www.python.org/downloads/
5. Execute _pip3 install --user -r requirements.txt_
6. Run _python3 main.py_
