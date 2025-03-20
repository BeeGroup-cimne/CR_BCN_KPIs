from datetime import datetime

from pymongo import MongoClient
from config.config_loader import config


def store_data_in_mongodb(collection_name, data):
    # store kpi
    client = MongoClient(config["mongo_db"]["uri"])
    db = client[config["mongo_db"]["db"]]
    collection = db[collection_name]
    collection.insert_one(data)
    # update calculation date
    if f"""{collection_name}_data""" not in db.list_collection_names():
        db[f"""{collection_name}_data"""].update_one({},
                                                     {"$push": {"calculation_dates": data["calculation_date"],
                                                                "description": "",
                                                                "unit": "",
                                                                "labels_names": "",
                                                                "labels_title": "",
                                                                "labels_type": "",
                                                                "legend": "",
                                                                "name": ""}},
                                                     upsert=True)
    else:
        db[f"""{collection_name}_data"""].update_one({},
                                                     {"$set": {"calculation_dates": data["calculation_date"]}},
                                                     upsert=True)
    client.close()

def store_many_data_in_mongodb(collection_name, data):

    client = MongoClient(config["mongo_db"]["uri"])
    db = client[config["mongo_db"]["db"]]
    collection = db[collection_name]
    collection.insert_many(data)

    if f"""{collection_name}_data""" not in db.list_collection_names():
        db[f"""{collection_name}_data"""].update_one({},
                                                     {"$push": {"calculation_dates": [item["calculation_date"] for item in data],
                                                                "description": "",
                                                                "unit": "",
                                                                "labels_names": "",
                                                                "labels_title": "",
                                                                "labels_type": "",
                                                                "legend": "",
                                                                "name": ""}},
                                                     upsert=True)
    else:
        db[f"""{collection_name}_data"""].update_one({},
                                                     {"$set": {"calculation_dates": [item["calculation_date"] for item in data]}},
                                                     upsert=True)
    client.close()

def get_mongo_data(collection_name):
    client = MongoClient(config["mongo_db"]["uri"])
    db = client[config["mongo_db"]["db"]]

    collection = db[collection_name]
    return collection.find()

