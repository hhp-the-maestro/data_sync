from db_utils import DBUtils
from utils import insertion_map, load_map, print_out
from pprint import pprint
from collation import Compare_Data
from config.celery import async_update_in_db, async_insert_in_table


def map_data_sources(kwargs1, kwargs2, identifier):
    """Fetches Data from source and destination and calls mapping to generate diff, 
        calls methods to Patches with the generated diff and Updates/Adds the missing data
    """

    no_updates = 1
    mapping = load_map()
    # fetching the source data
    source = fetch_data(**kwargs1)
    if not isinstance(source, list):
        source = [source]
    for src in source:
        # Creating filters and fetching the destination data

        print_out("purple", "Source:\n")
        pprint(src, indent=5, depth=3)

        kwargs2["filter"] = {mapping[identifier]: src[identifier]}
        dest = fetch_data(**kwargs2)

        print_out("purple", "Destination\n")
        pprint(dest, indent=5, depth=3)
        if dest:
            # if dest data found with filters generates diff
            cmp = Compare_Data()
            applied_mapping, to_update, to_create, to_delete = cmp.match_src_dest(src, dest)
            to_update_data = process_to_update(to_update) # preprocess the patch data

            print_out("cyan", "Applied Mapping: \n")
            pprint(applied_mapping, indent=4)
            print_out("yellow", "Patch to be Applied:")
            print_out("yellow", to_update_data)
            print_out("purple", "Insert/Update: Sub Columns")
            print_out("purple", to_create)

            if to_update_data:
                # creates patches for generated diff
                update_data(kwargs2["table1"], to_update_data)

                print_out("yellow", "Patch Applied Successfully")
                no_updates = 0
            if to_create:
                # inserts the missing data
                to_create_data(kwargs2["table1"], to_create)

                print_out("green", "Added/Updated Successfully")
                no_updates = 0
        else:
            # if dest data not found generate insertion map and insert in dest tables
            data = insertion_map(src)
            print(data)
            insert_data(kwargs2["table1"], data)
            no_updates = 0
            map_data_sources(kwargs1, kwargs2, identifier)
    if no_updates:
        print_out("green", "No Updates")
    return 


def process_to_update(data):
    # preprocess and returns the patch data

    i = 0
    to_update_data = {}
    for key in data:
        if isinstance(data[key], list):
            arr = []
            for dat in data[key]:
                dat.pop("id", None)
                if len(dat) > 1:
                    arr.append(dat)
            if len(arr):
                to_update_data[key] = arr
        else:
            if key != "identity" and key != "id":
                to_update_data[key] = data[key]
                i += 1
    if i > 0:
        to_update_data["identity"] = data["identity"]

    return to_update_data


def fetch_data(table1, sub_tables, filter, column_name, limit=None, all=False):
    # fetches data from the main table and the depending sub_tables

    arr_data = []
    utils = DBUtils()
    sub_utils = DBUtils()

    result = utils.query_by_column(table1, filter, all=all, limit=limit)
    if result:
        result = [result] if not isinstance(result, list) else result
    else:
        return result
    
    for res1 in result:
        data = {}
        identifier = res1.get("id")
        foreign_keys = [col.name for col in utils.table.columns if col.foreign_keys]
        data.update(res1)
        
        for key in foreign_keys:
            res = sub_utils.query_by_column(key[:-3], {"id": res1[key]})
            data[key[:-3]] = res

        for table in sub_tables:
            res = sub_utils.query_by_column(table, {column_name: identifier})
            data[table] = res

        arr_data.append(data)
    if all:
        return arr_data
    return arr_data[0]


def to_create_data(table=None, data=None):
    utils = DBUtils()
    sub_tables = [key for key in data if isinstance(data[key], list)]
    for sub_table in sub_tables:
        for row in data[sub_table]:
            res = utils.query_by_column(sub_table, {"id": row["id"]}, all=False)
            if res:
                # utils.update_by_column(sub_table, {"id": row["id"]}, row)
                async_update_in_db.apply_async((sub_table, {"id": row["id"]}, row))
            else:
                # utils.insert_in_table(sub_table, data=row)
                async_insert_in_table.apply_async((sub_table, row))


def update_data(table=None, data=None):
    # generates patches for the generated diff
    utils = DBUtils()
    sub_tables = [key for key in data if isinstance(data[key], list)]
    
    for sub_table in sub_tables:
        for row in data[sub_table]:
            
            id = row.pop("identity")
            row.pop("id", None)
            async_update_in_db.apply_async((sub_table, {"id": id}, row))
            # utils.update_by_column(sub_table, {"id": id}, row)
        data.pop(sub_table)
    if data:
        
        id = data.pop("identity")
        async_update_in_db.apply_async((table, {"id": id}, data))
        # utils.update_by_column(table, {"id": id}, data)
    

def delete_data(table=None, data=None):
    utils = DBUtils()
    sub_tables = [key for key in data if isinstance(data[key], list)]

    for sub_table in sub_tables:
        id = data[sub_table].get("identity")
        utils.delete_by_column(sub_table, {"id": id})
    
    if table:
        id = data.get("identity")
        utils.delete_by_column(table, {"id": id})

    
def insert_data(table=None, data=None):
    # inserting new data in dest from the mapping data of source data
    data = insertion_map(data)
    utils = DBUtils()
    for key in data:
        if isinstance(data[key], list):
            for dat in data[key]:
                res = utils.query_by_column(key, {"id": dat["id"]})
                if not res:
                    # utils.insert_in_table(key, dat)
                    async_insert_in_table.apply_async((key, dat))
            data.pop(key)
    if data:
        # utils.insert_in_table(table, data)
        async_insert_in_table.apply_async((table, data))

    