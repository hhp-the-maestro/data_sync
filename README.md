# Data Sync
## *syncs data between two structured data sources*

*The Data Sync Application Syncs the data between two structured data sources having different schemas with same data.*

*The application can be run via host as well as in docker*

*In order to run the application in host , there is a requirement of rabbitmq-server to run async tasks.* 

## Configuration Files

The application has 3 json files for configuration: db_config.json, map_config.json, db_data.json

db_config.json - to write the schema for the tables in the database

map_config.json - has the mapping for source and destination data

db_data.json - has mock data for the database

## Schemas

### Source Data

![image](https://user-images.githubusercontent.com/68218986/199896057-0e5559ac-fa3d-4d3a-8380-9905965c95be.png)

### Destination Data

![image](https://user-images.githubusercontent.com/68218986/199896754-0dc8f95c-f99f-4c15-b4d4-af4c25ae560c.png)

## Working
*the databse is split into source and destination , using the tables [prospect, location, email_address, phone_numbers, company_detail] for source data
and [contact, emails, phones, company] for destination data.

There are a total of 6 commands and extendable 
1. To create the tables required for source and destination. The configuration of the tables are provided in db_config.json

2. To populate the databse tables with mock data. eventough the data is same the relation id between the data changes as it inserts async at once creating a huge diff between the source and destination data

3. To Map, Compare, generate diff and patch/update the dest data with respect to the source data for a single record

4. To Map, Compare, generate diff and patch/update the dest data with respect to the source data for multiple record (default=20)

5. To Drop all the tables in the database

6. To Insert a new row in the Source Tables and map it with the dest data, where it will trigger a insert in dest data by mapping the datas of src insertion map fn to generate dest data which has to be inserted



## Running On Host

Install rabbitmq-server

Install python dependencies using 'pip3 install -r requirements.txt'

From the base of the application where the main.py is , start celery with "celery -A config worker --loglevel=INFO"(without rabbitmq celery won't start)

Start the Application with "python3 main.py"

## Running On Docker

Stop the rabbitmq-server if running

build the docker using "sudo docker-compose build"

run the docker using "sudo docker-compose up"

get the container id of the docker container "data_sync" using "sudo docker container ls"

log in to the docker container using "sudo docker exec -it <container_id> bash"

start the application using "python main.py"
