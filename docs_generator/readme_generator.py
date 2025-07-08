from pymongo import MongoClient
import re
from collections import defaultdict
from pymongo.errors import ConnectionFailure, OperationFailure
import config

mongo_uri = (
    f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}/"
    f"?authSource={config.auth_db}&directConnection=true"
)

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  # 5 second timeout
    # Try to list databases to test connection & authentication
    db_names = client.list_database_names()
    print("Databases on server:", db_names)

except ConnectionFailure as e:
    print(f"Connection failed: {e}")
except OperationFailure as e:
    print(f"Authentication failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")


db = client["cr_bcn_kpis"]

# Read all group documents from the collection
group_collection = db["buildings_indicators_by_group"]
group_documents = list(group_collection.find())

# Map: group_name -> list of KPI keys
group_to_kpi_keys = defaultdict(list)
for doc in group_documents:
    group_name = doc.get("key", "Unknown Group")
    kpi_list = doc.get("kpis", [])
    for kpi in kpi_list:
        kpi_key = kpi.get("key")
        if kpi_key:
            group_to_kpi_keys[group_name].append(kpi_key)

# Get available "_data" collections
all_data_collections = [name for name in db.list_collection_names() if name.endswith("_data")]
existing_data_collections = set(all_data_collections)

# Initialise README content
readme_lines = ["# CR_BCN_KPIs\n",
    "Welcome to the **CR_BCN_KPIs** repository.\n",
    "This repository contains a collection of Key Performance Indicators (KPIs) calculated for each building in the city of Barcelona.\n",
    "These indicators are used to support data-driven decision-making and are displayed in the **Climate Ready BCN map**, a platform designed to visualize and explore urban performance metrics.\n",
    "\n---\n",
    "## Authors\n",
    "- Jose Manuel Broto - jmbroto@cimne.upc.edu\n",
    "- Gerard Mor - gmor@cimne.upc.edu\n",
    "\n---\n",

    "## Filling Missing KPI Values – KPI Predictor\n",
    "\n",
    "To complement the static KPI dataset provided in this repository, we offer an additional tool: the [**KPI Predictor**](https://github.com/BeeGroup-cimne/CR_BCN_KPIs/tree/main/kpi_predictor), a Python-based utility that fills in missing KPI values over time using supervised learning techniques.\n",
    "\n",
    "This tool is specifically designed to work with time series of KPIs stored in MongoDB and uses CatBoost, a gradient boosting model optimized for tabular data.\n",
    "\n---\n"
    

    "## KPI Documentation\n",
    "\n",
    "This section provides a detailed list of Key Performance Indicators (KPIs) used to assess buildings and their surrounding environment in Barcelona. Each KPI includes its name, description, unit of measurement, and data source.\n",
    "\n",
    "To improve clarity and usability, KPIs are grouped into the following typologies:\n",
    "\n",
    "- **Building Characteristics**: Physical and structural features of buildings, such as floor area, construction year, number of dwellings, or wall orientation.\n",
    "- **Climate Variability and Extreme Events**: Indicators that describe local climate behavior and exposure to extreme weather, including heatwaves, cooling degree days, and tropical nights.\n",
    "- **Demographic Indicators**: Population characteristics such as age, gender, household size, and place of birth, allocated to each building.\n",
    "- **Energy Indicators**: Information on energy consumption and efficiency, including electricity and gas use, thermal demand, and EPC performance.\n",
    "- **Infrastructure Indicators**: Measures of access to climate shelters, vegetation coverage, and proximity to key infrastructure.\n",
    "- **Socio-Economic Indicators**: Metrics describing income levels, economic inequality, and household income distribution.\n"
]

# Loop through groups and their indicators
for group_name in sorted(group_to_kpi_keys.keys()):
    readme_lines.append(f"### {group_name}\n")
    for kpi_key in sorted(group_to_kpi_keys[group_name]):
        collection_name = f"{kpi_key}_data"
        if collection_name not in existing_data_collections:
            continue  # Skip if the data collection doesn't exist

        collection = db[collection_name]
        metadata = collection.find_one()
        if not metadata:
            continue  # Skip if no metadata found

        name_list = metadata.get("name", [])
        description_list = metadata.get("description", [])
        unit_list = metadata.get("unit", [])

        name = name_list[0] if isinstance(name_list, list) and name_list else "N/A"
        description = description_list[0] if isinstance(description_list, list) and description_list else "N/A"
        unit = unit_list[0] if isinstance(unit_list, list) and unit_list else "N/A"
        if isinstance(unit, str):
            unit = unit.replace("m^2", "m²")

        # Remove HTML tags from description
        if isinstance(description, str):
            description_clean = re.sub(r'<[^>]+>', '', description)
        else:
            description_clean = "N/A"

        # Extract Data Source if present at the end
        data_source = "N/A"
        match = re.search(r"(?i)\bdata sources?\s*:\s*(.+)$", description_clean)
        if match:
            description_clean = description_clean[:match.start()].strip()
            data_source = match.group(1).strip()


        # Append KPI info
        readme_lines.append(f"#### {name}\n")
        readme_lines.append(f"- **Description:** {description_clean}")
        readme_lines.append(f"- **Unit:** {unit}")
        if data_source != "N/A":
            readme_lines.append(f"- **Data Source:** {data_source}")
        readme_lines.append("")  # Empty line for spacing


# Add CVI section
readme_lines.append("\n---\n")
readme_lines.append("## Climate Vulnerability Index (CVI)\n")
readme_lines.append(
    "The **Climate Vulnerability Index (CVI)** is a composite indicator used to assess climate-related vulnerability across buildings in Barcelona. "
    "It is calculated using an Empirical Cumulative Distribution Function (ECDF) approach that ranks each individual indicator.\n"
)
readme_lines.append(
    "Indicators are grouped into thematic categories, and each category contributes equally to the initial index — which is the default version shown on the Climate Ready BCN map. "
    "However, users can adjust the weights of these categories to reflect specific local priorities or sensitivities.\n"
)
readme_lines.append("### CVI categories and included KPIs:")
readme_lines.append("- **Demographic Indicators**: Number of child residents, number of elderly residents, number of female residents.")
readme_lines.append("- **Building Characteristics Indicators**: Total built area, year of construction.")
readme_lines.append("- **Climate Variability and Extreme Events Indicators**: Torrid nights.")
readme_lines.append("- **Energy Indicators**: Annual electricity consumption, annual gas consumption, cooling thermal demand (EPC), heating thermal demand (EPC), and final energy consumption (EPC).")
readme_lines.append("- **Socio-Economic Indicators**: Annual net household income.")
readme_lines.append("")
readme_lines.append(
    "**Note:** Some indicators are considered *inverse*, meaning that higher values contribute to *lower* vulnerability. "
    "These include: total built area, year of construction, and annual net household income."
)


# Add licence
readme_lines.append("\n---\n")
readme_lines.append("## License\n")
readme_lines.append("This project is licensed under the **European Union Public License (EUPL), Version 1.2.**\n")
readme_lines.append("You may obtain a copy of the license at:\n")
readme_lines.append("https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12\n")
readme_lines.append("Unless required by applicable law or agreed to in writing, software distributed under this license is distributed **on an \"AS IS\" basis**, without warranties or conditions of any kind.\n")
readme_lines.append("© 2025 Jose Manuel Broto, Gerard Mor\n")
readme_lines.append("\nThank you for using CR_BCN_KPIs!\n")
readme_lines.append("For any questions or suggestions, feel free to reach gmor@cimne.upc.edu\n")


# Write the content to README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(readme_lines))

print("README.md generated successfully.")