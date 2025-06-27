from pymongo import MongoClient
import pymongo
from collections import defaultdict
from config.config_loader import config
from tqdm import tqdm
import pandas as pd


def transformar_datos(client, db, indicators, coleccion_destino, batch_size =1000):

    resultados = defaultdict(lambda: {"calculation_date": None, "indicators": {}})

    for coleccion in indicators:
        collection = db[coleccion]
        indicador_nombre = coleccion

        for doc in collection.find({}, {"calculation_date": 1, "kpis": 1}):
            fecha = doc["calculation_date"]
            kpis = doc["kpis"]

            for ref_catastral, valor in kpis.items():
                if resultados[ref_catastral]["calculation_date"] is None:
                    resultados[ref_catastral]["calculation_date"] = fecha

                resultados[ref_catastral]["indicators"][indicador_nombre] = valor

    # Preparar documentos para bulk write
    bulk_ops = []
    collection_dest = db[coleccion_destino]
    for i, (ref_catastral, data) in tqdm(enumerate(resultados.items(), start=1)):
        bulk_ops.append(
            pymongo.UpdateOne(
                {"reference": ref_catastral},
                {"$set": data},
                upsert=True
            )
        )

        if i % batch_size == 0:
            collection_dest.bulk_write(bulk_ops)
            bulk_ops = []

    if bulk_ops:
        collection_dest.bulk_write(bulk_ops)

    print("Transformación completada y datos almacenados en la colección destino.")
    client.close()


    file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/08900.pkl"
    df = pd.read_pickle(file_path, compression="gzip")
    result = {}

    for idx, row in df.iterrows():
        address_dict = row["br__building_spaces_postal_address"]

        result[row["building_reference"]] = {}
        if isinstance(address_dict, dict) and "Residential" in address_dict:
            result[row["building_reference"]]["address"] = list(set(row["br__building_spaces_postal_address"]["Residential"]))
        result[row["building_reference"]]["district"] = row['district_name']
        result[row["building_reference"]]["neighborhood"] = row['neighborhood_name']
    # for ref, location_data in tqdm(result.items()):
    #     db["indicators_by_reference"].update_one(
    #         {"reference": ref},
    #         {"$set": {"location": location_data}}
    #     )
    batch_size = 1000
    operations = []

    client = MongoClient(config["mongo_db"]["uri"])
    db = client[config["mongo_db"]["db"]]

    for i, (ref, location_data) in tqdm(enumerate(result.items(), 1)):
        operations.append(
            pymongo.UpdateOne({"reference": ref}, {"$set": {"location": location_data}})
        )
        if i % batch_size == 0:
            db["indicators_by_reference"].bulk_write(operations, ordered=False)
            operations = []

    # Final batch
    if operations:
        db["indicators_by_reference"].bulk_write(operations, ordered=False)
def create_indicator_by_reference_metadata(client, db, indicators, collection):
    collection_db = db[collection]
    # collection_db.delete_many({})

    campos_deseados = ["description", "unit", "name", "labels_type", "frequency"]

    indicators_all = []

    for nombre_col in indicators:
        coleccion_origen = db[f"{nombre_col}_data"]
        documentos = coleccion_origen.find({}, {campo: 1 for campo in campos_deseados})

        for doc in documentos:
            doc.pop("_id", None)
            doc["kpi"] = nombre_col
            indicators_all.append(doc)

    document = {
        "indicators": indicators_all
    }
    collection_db.insert_one(document)

indicators = config["indicators_by_reference"]
coleccion_destino = "indicators_by_reference"
client = MongoClient(config["mongo_db"]["uri"])
db = client[config["mongo_db"]["db"]]

# Ejecutar la transformación
transformar_datos(client, db, indicators, coleccion_destino)
create_indicator_by_reference_metadata(client, db, indicators, "indicators_by_reference_data")