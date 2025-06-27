import json

with open("/Users/jose/PycharmProjects/CR_BCN_KPIs/config.json", "r") as f:
    config = json.load(f)
    if 'neo4j' in config:
        config['neo4j']['auth'] = tuple(config['neo4j']['auth'])