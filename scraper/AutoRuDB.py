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
             
        # for i in range(len(data)):
        #     try:
        #             temp = self.autoru_table(name = data.loc[i,'name'],
        #                 url = data.loc[i,'url'],
        #                 cost = float(data.loc[i,'cost']),
        #                 millege = data.loc[i,'millege'],
        #                 engine_volume = data.loc[i,'engine_volume'],
        #                 motor_power = data.loc[i,'motor_power'],
        #                 fuel_type = data.loc[i,'fuel_type'],
        #                 body_type = data.loc[i,'body_type'],
        #                 drive_type = data.loc[i,'drive_type'],
        #                 gearbox_type = data.loc[i,'gearbox_type'],
        #                 owners_num = data.loc[i,'owners_num'],
        #                 configuration = data.loc[i,'configuration'],
        #                 steering_wheel_type = data.loc[i,'steering_wheel_type'],
        #                 color = data.loc[i,'color'],
        #                 saler_comment = data.loc[i, 'saler_comment'],
        #                 parse_city = data.loc[i,'parse_city'],
        #                 parse_mark = data.loc[i,'parse_mark'],
        #                 parse_model = data.loc[i,'parse_model'],
        #                 parse_date = data.loc[i,'parse_date']
        #                 )
        #     except:
        #             temp = self.autoru_table(name = data.loc[i,'name'],
        #                 url = data.loc[i,'url'],
        #                 cost = float(data.loc[i,'cost']),
        #                 millege = data.loc[i,'millege'],
        #                 engine_volume = data.loc[i,'engine_volume'],
        #                 motor_power = data.loc[i,'motor_power'],
        #                 fuel_type = data.loc[i,'fuel_type'],
        #                 body_type = data.loc[i,'body_type'],
        #                 drive_type = data.loc[i,'drive_type'],
        #                 gearbox_type = data.loc[i,'gearbox_type'],
        #                 parse_city = data.loc[i,'parse_city'],
        #                 parse_mark = data.loc[i,'parse_mark'],
        #                 parse_model = data.loc[i,'parse_model'],
        #                 parse_date = data.loc[i,'parse_date']
        #                 )
        #     new_data.append(temp)
    
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
    
        return data_db
