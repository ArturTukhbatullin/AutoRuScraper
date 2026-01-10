from scraper.AutoRuDB import AutoRuDB
import os
import pandas as pd


if __name__ == "__main__":

    db = AutoRuDB('autorudb')

    db.create_db()

    db.create_table()

    files = os.listdir('data/csv/')
    for file in files:
        data = pd.read_csv(fr'data/csv/{file}',sep = ';')
        db.load_data_to_db(data)



    # data_db = db.read_db('autoru')
    # print(data_db['name'].value_counts())
    # print()
    # print(data_db['url'].value_counts())