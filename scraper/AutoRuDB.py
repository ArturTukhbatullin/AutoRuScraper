import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase, Mapped,mapped_column
from loguru import logger
from .models.autoru_table import Base, autoru_table
from .schemas.autoru_item import autoru_item

logger.add("logs/log.log", rotation="500 MB",compression='zip')


class AutoRuDB:

    def __init__(self, db_name, **conn_params):

        username = conn_params['username']
        password = conn_params['password']
        host = conn_params['host']
        port = conn_params['port']
        connection_string = fr"postgresql+psycopg2://{username}:{password}"f"@{host}:{port}/{db_name}"
        
        self.db_name = db_name        
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)

    def get_init_params(self):

        query = """
        select * from autoru_init_params
        where active_flg = True
        """
        
        engine = create_engine(self.connection_string, echo=False)
            
        with engine.connect() as connection:
            data_db = pd.read_sql(query,connection)
            connection.close()

        return data_db


    def create_table(self):
       
        Base.metadata.create_all(self.engine)
        self.autoru_table = autoru_table

    def load_data_to_db(self, data):

        with self.engine.connect() as connection:
            self.connection = connection

        data['parse_date'] = pd.to_datetime(data['parse_date']).dt.date
        new_data = []
        for row in data.to_dict(orient = 'records'):
            new_data.append(autoru_item.from_row(row))
        new_data = [autoru_table.from_pydantic(item) for item in new_data]
    
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add_all(new_data)
        session.commit()
        logger.info('Данные загружены в БД')
        self.connection.close()

    def read_db(self, table_name):
    
        query = fr'select * from {table_name}'
        engine = create_engine(self.connection_string, echo=False)
    
        with engine.connect() as connection:
                data_db = pd.read_sql(query,connection)
                connection.close()
        return data_db
