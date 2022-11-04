from db_conf import DbConf
from db_utils import DBUtils
from fns import map_data_sources
from config.celery import populate_db
from utils import print_out


def display_menu():
    print_out("purple", "Enter one of the below listed option:\n")
    print_out("purple", "1. Create the database tables from the db_config.json")
    print_out("purple", "2. Populate the database tables with db_data.json")
    print_out("purple", "3. Run/Generate Diff and update one record")
    print_out("purple", "4. Run/Generate Diff and update for specified number of rows (default 20)")
    print_out("purple", "5. Drop All Tables")
    print_out("purple", "6. Insert new record in src and map it with the dest")
    print_out("red", "exit to EXIT")


def main():
    db_conf = DbConf()

    while True:
        display_menu()

        kwargs1 = {"table1": "prospect", "sub_tables": ["phone_numbers", "email_address"], "filter":{}, "column_name": "prospect_id", "all": False}
        kwargs2 = {"table1": "contact", "sub_tables": ["phones", "emails"], "filter": {}, "column_name": "contact_id", "all": False}
        
        inp = input("Enter Your Choice: ")
        if inp == "exit":
            break
        
        if inp == '1':
            # create the database tables
            db_conf.build_db()

        if inp == '2':
            # Populate database with data in db_data.json
            task = populate_db.delay('db_data.json')
            print_out("yellow", "Data being populated in the background...")
        
        if inp == "3":
            # map a single data from 2 different sources , generate diff and update
            map_data_sources(kwargs1, kwargs2, identifier="id")
        
        if inp == "4":
            # map all data from the sources and generate diff and update
            '''As the data is inserted in async manner the src and dest data vary with diff ids, 
               So it would take multiple(2) mapping calls to make them identical 
            ''' 
            kwargs1["all"] = True
            kwargs1["limit"] = 20
            map_data_sources(kwargs1, kwargs2, identifier="id")
        
        if inp == "5":
            # Drop all tables
            DbConf().drop_all_tables()

            print_out("red", "All Tables are Dropeed.")

        if inp == "6":
            '''Add new column in src table and map it with the destination. 
                the destination don't have the record with that id, 
                therefore the data will be src data will be mapped and inserted in the dest tables
            '''

            data = {"display_name": "shawn", "prefix": "Mr", "location_id": 3, "company_detail_id": 2}
            
            id = DBUtils().insert_in_table("prospect", data)
            kwargs1["filter"] = {"id": id}
            map_data_sources(kwargs1, kwargs2, identifier="id")


if __name__ == "__main__":
    main()
