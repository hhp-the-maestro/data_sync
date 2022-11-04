from sqlalchemy import (Table, Column, Integer, Numeric,
                        String, Boolean, ForeignKey, MetaData, create_engine, inspect, BigInteger)
from alembic.operations import Operations
from alembic.migration import MigrationContext
import json
from utils import print_out

db = create_engine("sqlite:///sqlite3")
metadata = MetaData(db)
metadata.reflect()

ctx = MigrationContext.configure(db.connect())
op = Operations(ctx)


class DbConf:
    # database configurations to create and drop tables
    type_mapper = {
        "str": String, 
        "int": Integer, 
        "bool": Boolean, 
        "foreign": ForeignKey, 
        "bigint": BigInteger
    }

    def __init__(self):
        self.table = None
        self.load_data()
        self.metadata = MetaData(db)
        self.metadata.reflect()

    def load_data(self):
        with open("db_config.json") as f:
            self.data = json.load(f)
        return self.data
    
    def build_db(self):
        for table in self.data["TABLES"]:
            self.table = table
            try:
                self.create_table()
                print_out("green", f"{table} Created")
            except:
                print_out("red", f"{table} Already Exist")
        self.metadata.create_all()

    def create_table(self, table=None, extend=False):
        if table:
            self.table = table
        if not inspect(db).has_table(self.table) or extend:
            columns = self.config_columns()
            Table(self.table, self.metadata, *columns)
        else:
            raise Exception("Table Already Exist")
    
    def drop_all_tables(self):
        for table in self.data["TABLES"]:
            try:
                self.drop_table(table)
            except:
                print_out("red", f"Table({table} does not exist")
    @staticmethod
    def drop_table(table):
        if inspect(db).has_table(table):
            op.drop_table(table)
        else:
            raise Exception("Table Does Not Exist")
        
    def add_column(self, table, conf=None):
        columns = inspect(db).get_columns(table)
        if not any(column["name"] == conf["name"] for column in columns):
            op.add_column(table, self.create_column(conf))
        else:
            raise Exception("Column Already Exist")

    @staticmethod
    def drop_column(self, table, column_name):
        columns = inspect(db).get_columns(table)
        if any(column["name"] == column_name for column in columns):
            op.drop_column(table, column_name)
        else:
            raise Exception("Column not found")

    def config_columns(self):

        columns = list()
        for col_info in self.data["TABLES"][self.table]:
            columns.append(self.create_column(col_info=col_info))
        return columns

    def create_column(self, col_info):
        if col_info.get("type") == "foreign":
            column = Column(col_info["name"], self.type_mapper[col_info["type"]](col_info["key"]))
        else:
            column = Column(col_info["name"])
            
            if col_info.get("size"):
                column.type = self.type_mapper[col_info["type"]](col_info["size"])
            else:
                column.type = self.type_mapper[col_info["type"]]()

            if col_info.get("primary_key"):
                column.primary_key = col_info["primary_key"]
            if col_info.get("nullable"):
                column.nullable = col_info["nullable"]
            if col_info.get("default"):
                column.nullable = col_info["default"]
            if col_info.get("unique"):
                column.unique = col_info["unique"]
        
        return column

