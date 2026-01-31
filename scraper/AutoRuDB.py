import pandas as pd
import os


from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import Optional

from datetime import date
from sqlalchemy import Date

from loguru import logger

logger.add("logs/log.log", rotation="500 MB",compression='zip')


class AutoRuDB:


    def __init__(self, db_name):

        cols = ['name', 'url', 'cost', 'millege',  'engine_volume',
       'motor_power', 'fuel_type', 'body_type', 'drive_type', 'gearbox_type',
       'parse_date']
        
        self.cols = cols
        self.db_name = db_name


    def create_db(self):

        engine = create_engine(fr"sqlite:///data/{self.db_name}.db")
        self.engine = engine

        if os.path.exists(fr'data/{self.db_name}.db'):
            self.connection = engine.connect()
        else:
            try:
                with engine.connect() as connection:
                    self.connection = connection
                    logger.info('Создана новая БД')
            except Exception as ex:
                logger.warning(fr'{ex}')

    
    def create_table(self):

        class Base(DeclarativeBase):
            pass

        class autoru_table(Base):
            __tablename__ = "autoru"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(30))
            url: Mapped[str]
            cost: Mapped[float]
            millege: Mapped[str]
            engine_volume: Mapped[str]
            motor_power: Mapped[str]
            fuel_type: Mapped[str]
            body_type: Mapped[str]
            drive_type: Mapped[str]
            gearbox_type: Mapped[str]
            owners_num : Mapped[Optional[str]]
            configuration : Mapped[Optional[str]]
            steering_wheel_type : Mapped[Optional[str]]
            color : Mapped[Optional[str]]
            parse_date: Mapped[date] = mapped_column(Date())

        Base.metadata.create_all(self.engine)
        self.autoru_table = autoru_table

    def load_data_to_db(self, data):

        data['parse_date'] = pd.to_datetime(data['parse_date']).dt.date
        
        new_data = []
        for i in range(len(data)):
            try:
                temp = self.autoru_table(name = data.loc[i,'name'],
                    url = data.loc[i,'url'],
                    cost = data.loc[i,'cost'],
                    millege = data.loc[i,'millege'],
                    engine_volume = data.loc[i,'engine_volume'],
                    motor_power = data.loc[i,'motor_power'],
                    fuel_type = data.loc[i,'fuel_type'],
                    body_type = data.loc[i,'body_type'],
                    drive_type = data.loc[i,'drive_type'],
                    gearbox_type = data.loc[i,'gearbox_type'],
                    owners_num = data.loc[i,'owners_num'],
                    configuration = data.loc[i,'configuration'],
                    steering_wheel_type = data.loc[i,'steering_wheel_type'],
                    color = data.loc[i,'color'],
                    parse_date = data.loc[i,'parse_date']
                    )
            except:
                temp = self.autoru_table(name = data.loc[i,'name'],
                    url = data.loc[i,'url'],
                    cost = data.loc[i,'cost'],
                    millege = data.loc[i,'millege'],
                    engine_volume = data.loc[i,'engine_volume'],
                    motor_power = data.loc[i,'motor_power'],
                    fuel_type = data.loc[i,'fuel_type'],
                    body_type = data.loc[i,'body_type'],
                    drive_type = data.loc[i,'drive_type'],
                    gearbox_type = data.loc[i,'gearbox_type'],
                    parse_date = data.loc[i,'parse_date']
                    )
            new_data.append(temp)

        print(temp)

        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add_all(new_data)
        session.commit()
        logger.info('Данные загружены в БД')

        self.connection.close()
        
    def read_db(self, table_name):

        query = fr'select * from {table_name}'
        engine = create_engine(fr'sqlite:///data/{self.db_name}.db', echo=False)

        with engine.connect() as connection:
            data_db = pd.read_sql(query,connection)

        return data_db