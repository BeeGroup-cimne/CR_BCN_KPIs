# 🏠 KPI Predictor for Building-Level Time Series (MongoDB + CatBoost)

This repository contains a Python script for retrieving time series indicators (KPIs) from a MongoDB collection, training regression models using [CatBoost](https://catboost.ai/), and predicting missing KPI values for each building per year. It then uploads the completed values and prediction flags back to MongoDB.

---

## 🚀 Project Overview

This script is designed to:
- Connect to one or more MongoDB collections containing building-level KPIs
- Extract and preprocess data by merging multiple features
- Apply forward and backward filling of missing values
- Use cross-validated [CatBoostRegressor](https://catboost.ai/) models to predict missing values
- Log model performance (CVRMSE, R²)
- Upload the filled values and prediction flags (`kpis_predicted`) back to MongoDB

---

## ⚙️ Configuration (`config.json`)

The script uses a config file to control:
- MongoDB connection parameters
- List of collections and variables to extract
- Predictor targets, input variables, value ranges, and target output collection names

Example structure:

```json
{
  "mongo_db": {
    "uri": "mongodb://localhost:27017/",
    "db": "my_database"
  },
  "min_year": 2015,
  "mongo_collection_features": [
    ["collection_name", "feature_name"],  // collection where to gather feature, feature name in this script, element to gather if value is of type list
    ["another_collection", "feature_name", 1]
  ],
  "predictors_to_run": {
    "target_variable": [
      ["input1", "input2"],      // input features
      "output_collection",       // mongo collection where to write predictions
      0,                         // min allowed value
      10000,                     // max allowed value
      ["filter_col", [1, 2, 3]]  // optional filtering condition
    ]
  }
}
```

## 🧠 Modeling Approach

This project uses a **supervised learning approach** to predict missing KPI values across buildings and years. Each KPI is modeled independently using a [CatBoostRegressor](https://catboost.ai/), a gradient boosting algorithm optimized for tabular data.

### Why CatBoost?
- ✅ Handles missing values natively
- ✅ Prevents overfitting via ordered boosting
- ✅ Works efficiently with heterogeneous tabular datasets
- ✅ Easy integration with scikit-learn tools (e.g., GridSearchCV)

### Training & Prediction Pipeline

1. **Filter data**:
   - Removes rows where the target KPI is missing or falls outside an allowed range
   - Optional filter by categories (e.g., building type)

2. **Cross-Validation**:
   - K-Fold CV (default 5 splits) using grid search on:
     - `depth`: `[6, 8, 10]`
     - `learning_rate`: `[0.03, 0.1]`
     - `l2_leaf_reg`: `[6, 8, 10]`
   - Performance metrics:
     - **CVRMSE** (relative RMSE)
     - **R² Score**

3. **Final Training and Prediction**:
   - Trains the best model on all eligible samples
   - Predicts KPI values for all buildings and years
   - Clamps predictions to allowed value ranges
   - Stores both the filled value and a boolean flag indicating whether it was predicted

---

## 🗄️ MongoDB Output Format

For each `year`, the output collection contains a single document with:

```json
{
  "calculation_date": "YYYY-01-01",
  "kpis": {
    "building_reference_1": <value>,
    "building_reference_2": <value>
  },
  "kpis_predicted": {
    "building_reference_1": false,
    "building_reference_2": true
  }
}

```
- kpis: Contains all predicted or known KPI values per building
- kpis_predicted: Indicates whether each value was predicted (true) or original (false)

## 📚 Available KPI Collection Keys

Below is a structured list of all available KPI collection keys, organized by thematic categories, with English translations, descriptions, and units.

### 🌡️ Climate Variability and Extreme Events

| KPI Key                      | Name                             | Unit                  |
|------------------------------|----------------------------------|-----------------------|
| `heat_avg_temperature_kpis`  | Heat index (daily average)       | °C                    |
| `heat_max_temperature_kpis`  | Heat index (daily maximum)       | °C                    |
| `torrid_nights`              | Torrid nights (minimum >25°C)    | nights/year           |
| `tropical_nights`            | Tropical nights (minimum >20°C)  | nights/year           |
| `heat_waves`                 | Heat waves                       | events/year           |
| `heating_degree_days`        | Heating degree days              | degree-days/year      |
| `cooling_degree_days`        | Cooling degree days              | degree-days/year      |

### ⚡ Energy Indicators

| KPI Key                               | Name                                           | Unit            |
|---------------------------------------|------------------------------------------------|-----------------|
| `annual_electricity_consumption`      | Annual electricity consumption                 | kWh/year        |
| `annual_gas_consumption`              | Annual gas consumption                         | kWh/year        |
| `primary_energy_by_certificate`       | Estimated primary energy consumption           | kWh/year        |
| `cooling_thermal_demand_intensity`    | Cooling thermal demand (according to EPCs)     | kWh/m²·year     |
| `heating_thermal_demand_intensity`    | Heating thermal demand (according to EPCs)     | kWh/m²·year     |
| `total_energy_consumption_intensity`  | Final energy consumption (based on EPCs)       | kWh/m²·year     |
| `window_to_wall_ratio`                | Window to wall area ratio                      | %               |


### 🏢 Building Characteristics

| KPI Key                           | Name                                       | Unit        |
|-----------------------------------|--------------------------------------------|-------------|
| `gross_floor_area`                | Total built area                           | m²          |
| `walls_ratio_by_type`             | Building walls area by type                | %           |
| `walls_area_by_type`              | Building walls area                        | m²          |
| `main_usage`                      | Use type                             | m²    |
| `main_usage_percentage`   | Use type percentage           | %           |
| `elevation_above_sea_level`       | Elevation above sea level                  | m  |
| `effective_construction_year`     | Year of construction                       | year        |
| `building_code`                   | Building code at time of construction      | category    |
| `average_dwelling_area`           | Average dwelling area                      | m²          |
| `building_roof_area`              | Building roof area                         | m²          |
| `dwelings_number`                 | Number of dwellings                        | count       |
| `number_of_floors_below_ground`   | Floors below ground                        | count       |
| `number_of_floors_above_ground`   | Floors above ground                        | count       |

### 🏙️ Infrastructure Indicators

| KPI Key                                | Name                                      | Unit               |
|----------------------------------------|-------------------------------------------|--------------------|
| `vegetation_index`                     | Vegetation Index                          | category (%)         |
| `vegetation_index_avg`                 | Average Vegetation Index                  | ratio         |
| `min_time_to_closest_climate_shelter`  | Minimum time to nearest climate shelter   | minutes            |
| `num_climate_shelters`                 | Number of Climate Shelters within X mins  | count              |

### 🧬 Demographic Indicators

| KPI Key                                 | Name                                            | Unit           |
|-----------------------------------------|-------------------------------------------------|----------------|
| `percentage_single_person_households`   | Percentage of single-person households          | %              |
| `percentage_population_under_18`        | Percentage of population under 18 years old     | %              |
| `percentage_population_over_65`         | Percentage of population over 65 years old      | %              |
| `residents_per_building`                | Number of residents per building                | count          |
| `building_residents_birthplace`         | Residents' birthplace distribution              | category (%)   |
| `male_residents_per_building`           | Number of male residents per building           | count          |
| `female_residents_per_building`         | Number of female residents per building         | count          |
| `children_residents_per_building`       | Number of child residents per building          | count          |
| `ancients_residents_per_building`       | Number of elderly residents per building        | count          |

### 💰 Socio-Economic Indicators

| KPI Key                                     | Name                                     | Unit                 |
|---------------------------------------------|------------------------------------------|----------------------|
| `gini_index_incomes`                        | Income Gini Index                        | ratio     |
| `income_distribution_p80_p20`               | Income distribution ratio P80/P20        | ratio                |
| `annual_net_incomes_household_per_building` | Annual net household income per building | EUR/year             |

### 🏥 Health Indicators

_No KPIs are currently available in this category._


## 📄 License

This project is licensed under the **European Union Public Licence (EUPL) v1.2**.

