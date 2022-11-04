from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, MetaData
from db_conf import db, metadata


class DBUtils:
    """database utilities to select/update/insert/delete"""
    def __init__(self):
        self.db = db
        Session = sessionmaker(bind=self.db)
        self.session = Session()
        self.table = None
        self.metadata = MetaData(db)
        self.metadata.reflect()
    
    def insert_in_table(self, table, data):
        self.select_table(table)
        row = self.table.insert().values(**data)
        res = self.session.execute(row)
        self.session.commit()
        return res.inserted_primary_key[0]

    def query_by_column(self, table, filters, all=True, limit=None):
        self.select_table(table)
        if all:
            result = self.session.query(self.table).filter_by(**filters)
            if limit:
                result = result.limit(limit)
            return [res._asdict() for res in result.all()]

        result = self.session.query(self.table).filter_by(**filters).first()
        if result:
            return result._asdict()
    
    def update_by_column(self, table, filters, data):
        self.select_table(table)
        query = self.session.query(self.table).filter_by(**filters)
        query.update(data)
        self.session.commit()
    
    def delete_by_column(self, table, filters):
        self.select_table(table)
        query = self.session.query(self.table).filter_by(**filters)
        query.delete()
        self.session.commit()
    
    def select_table(self, table):
        self.table = self.metadata.tables[table]


