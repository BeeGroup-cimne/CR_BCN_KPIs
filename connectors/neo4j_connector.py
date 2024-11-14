from neo4j import GraphDatabase
from config.config_loader import config


def fetch_data_from_neo4j(query):
    driver = GraphDatabase.driver(**config["neo4j"])

    with driver.session() as session:
        result = session.run(query).data()
    driver.close()
    return result
