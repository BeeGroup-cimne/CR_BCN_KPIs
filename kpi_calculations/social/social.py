from datetime import datetime
from collections import defaultdict
import re

import numpy as np
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from config.config_loader import config


class social(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):

        vector_kpi_groups = {
            "electricity_consumption": [
                "so__electricity_consumption_p10",
                "so__electricity_consumption_p25",
                "so__electricity_consumption_p50",
                "so__electricity_consumption_p75",
                "so__electricity_consumption_p90"
            ],

            "housing_price_index": [
                "so__housing_price_index_new",
                "so__housing_price_index_second_hand",
                "so__housing_price_index_total"
            ],

            "education": [
                "so__pct_edu_lower_secondary",
                "so__pct_edu_primary_or_below",
                "so__pct_edu_tertiary",
                "so__pct_edu_upper_secondary"
            ],

            "income_source": [
                "so__pct_income_source_capital_investments_secondary",
                "so__pct_income_source_other_benefits",
                "so__pct_income_source_pension",
                "so__pct_income_source_salary",
                "so__pct_income_source_unemployment"
            ],

            "employment_status": [
                "so__pct_employed",
                "so__pct_other_inactive",
                "so__pct_pensioner",
                "so__pct_student",
                "so__pct_unemployed"
            ]
        }
        vector_kpis = {
            kpi
            for group in vector_kpi_groups.values()
            for kpi in group
        }

        social_df = pd.read_pickle("data/08900_complete_inference.pkl", compression="gzip")
        social_residential_df = social_df[social_df["building_use"] == "1_residential"]
        kpi_groups = defaultdict(list)

        for col in social_residential_df.columns:
            match = re.match(r"(.+)_(\d{4})$", col)

            if match:
                kpi = match.group(1)
                year = int(match.group(2))
                kpi_groups[kpi].append((year, col))

        for kpi, columns in kpi_groups.items():

            # estos se procesan después como vectores
            if kpi in vector_kpis:
                continue
            print(kpi)

            if kpi.startswith('so__'):

                self.data["result"] = {}
                for year, col in columns:
                    self.data["result"][year] = {
                        row["building_reference"]: round(float(row[col]), 2)
                        for _, row in social_residential_df.iterrows()
                        if pd.notna(row[col])
                    }

                self.data["result"] = [
                    {
                        "calculation_date": datetime(
                            year=int(year),
                            month=1,
                            day=1
                        ).date().isoformat(),
                        "kpis": values
                    }
                    for year, values in sorted(self.data["result"].items())
                ]

                store_many_data_in_mongodb(
                    kpi,
                    self.data["result"]
                )

        for group_name, group_kpis in vector_kpi_groups.items():
            vector_results = defaultdict(dict)

            for kpi in group_kpis:

                for year, col in kpi_groups[kpi]:

                    for _, row in social_residential_df.iterrows():

                        building = row["building_reference"]

                        if pd.notna(row[col]):

                            if building not in vector_results[year]:
                                vector_results[year][building] = {}

                            vector_results[year][building][kpi] = round(
                                float(row[col]),
                                2
                            )

            self.data["result"] = [
                {
                    "calculation_date": datetime(
                        year=int(year),
                        month=1,
                        day=1
                    ).date().isoformat(),

                    "kpis": {
                        building: [
                            values.get(kpi, None)
                            for kpi in group_kpis
                        ]
                        for building, values in buildings.items()
                    }
                }
                for year, buildings in sorted(vector_results.items())
            ]

            store_many_data_in_mongodb(
                group_name,
                self.data["result"]
            )

    def calculate(self):
        pass

    def store_result(self):
        pass
