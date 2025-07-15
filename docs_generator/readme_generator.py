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
readme_lines = ["# Climate Ready Barcelona: Indicators calculation\n",
    "Welcome to the **Climate Ready Barcelona: Indicators calculation** repository.\n",
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
readme_lines.append("## Climate Vulnerability Index (CVI) construction\n")
readme_lines.append(
    "The **Climate Vulnerability Index (CVI)** is a composite indicator used to assess climate-related vulnerability across buildings in Barcelona. "
    "To assign a vulnerability value to each building for a given indicator, an **Empirical Cumulative Distribution Function (ECDF)** is used. "
    "The ECDF transforms raw indicator values into a continuous score between 0 and 1, representing the building’s relative position within the city-wide distribution. "
    "This allows for a finer-grained assessment than discrete quantile bins."
)
readme_lines.append(
    "Indicators are grouped into thematic categories, and each category contributes equally to the initial index — which is the default version shown on the Climate Ready BCN map. "
    "However, users can adjust the weights of these categories to reflect specific local priorities or sensitivities.\n"
)
readme_lines.append("### CVI categories and included KPIs:")
readme_lines.append("- **Demographic Indicators**: Number of child residents, number of elderly residents, number of female residents.")
readme_lines.append("- **Building Characteristics Indicators**: Total built area, year of construction.")
readme_lines.append("- **Climate Variability and Extreme Events Indicators**: Torrid nights, heat index.")
readme_lines.append("- **Energy Indicators**: Annual electricity consumption, annual gas consumption, cooling thermal demand (EPC), heating thermal demand (EPC), and final energy consumption (EPC).")
readme_lines.append("- **Socio-Economic Indicators**: Annual net household income, income Gini index.")
readme_lines.append("")
readme_lines.append(
    "**Note:** Some indicators are considered *inverse*, meaning that higher values contribute to *lower* vulnerability. "
    "These include: total built area, year of construction, and annual net household income."
)

readme_lines.append("### Mathematical formulation:")
readme_lines.append("Mathematically, for an indicator *I*, the ECDF is defined as:")
readme_lines.append("![ECDF formula](docs_generator/Fig/ECDF_formula.png)")
readme_lines.append("")
readme_lines.append("Where:")
readme_lines.append("- **N** is the total number of buildings")
readme_lines.append("- **Xᵦ** is the indicator value for building *b*")
readme_lines.append("- **1(Xᵦ ≤ x)** is an indicator function returning 1 if the condition is true, 0 otherwise")
readme_lines.append("")
readme_lines.append("For an indicator *Iⱼ* of a building *b*, the normalized value becomes:")
readme_lines.append("")
readme_lines.append("![normalised indicator](docs_generator/Fig/normalised_indicator_score.png)")
readme_lines.append("")
readme_lines.append("Some indicators *reduce* vulnerability (e.g., high income, newer buildings). These are treated as inverse indicators, and their scores are flipped:")
readme_lines.append("![Inverse Indicator Transformation](docs_generator/Fig/Inverse_Indicator_Transformation.png)")
readme_lines.append("")
readme_lines.append("Where *Iⱼ* is the value between 0 and 1 of indicator *j*.")
readme_lines.append("Each indicator belongs to a broader typology (category), and the **typology score** is computed as the average of its indicators:")
readme_lines.append("![Typology Aggregated Score](docs_generator/Fig/Typology_Aggregated_Score.png)")
readme_lines.append("")
readme_lines.append("Where |T| is the number of indicators in typology T.")
readme_lines.append("")
readme_lines.append("Finally, the **Climate Vulnerability Index (CVI)** is calculated as a weighted sum of all typologies:")
readme_lines.append("![CVI](docs_generator/Fig/CVI.png)")
readme_lines.append("")
readme_lines.append("Where **Wₜ** is the weight assigned to typology T.")
readme_lines.append("")
readme_lines.append("By default, all typologies are equally weighted (Wₜ = 1/7). However, the user interface allows for customization of these weights, enabling users to prioritize indicators based on their specific needs — such as focusing more on climatic factors or socioeconomic vulnerability.")
readme_lines.append("")
readme_lines.append("The figure below shows a spatial representation of the CVI across Barcelona:")
readme_lines.append("![CVI map](docs_generator/Fig/CVI_map.png)")
readme_lines.append("The figure above illustrates the vulnerability levels of buildings throughout the city, with areas of higher vulnerability marked. On the left-hand side of the map, the different indicator typologies are displayed, and users can adjust the weights of these categories.")
readme_lines.append("This customisation feature allows users to modify the influence of each typology (such as demographic, building characteristics, or energy-related indicators) based on their specific needs or priorities. By adjusting these weights, users can tailor the analysis to focus more on certain factors — for instance, prioritising climate-related variables or socioeconomic factors — depending on the context or objectives of their study.")



# Add licence
readme_lines.append("\n---\n")
readme_lines.append("## License\n")
readme_lines.append("This project is licensed under the **European Union Public License (EUPL), Version 1.2.**\n")
readme_lines.append("You may obtain a copy of the license at:\n")
readme_lines.append("https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12\n")
readme_lines.append("Unless required by applicable law or agreed to in writing, software distributed under this license is distributed **on an \"AS IS\" basis**, without warranties or conditions of any kind.\n")
readme_lines.append("© 2025 Jose Manuel Broto, Gerard Mor\n")
readme_lines.append("\nThank you for using Climate Ready Barcelona: Indicators calculation!\n")
readme_lines.append("For any questions or suggestions, feel free to reach gmor@cimne.upc.edu\n")


# Write the content to README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(readme_lines))

print("README.md generated successfully.")