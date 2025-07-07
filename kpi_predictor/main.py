import pandas as pd
from pymongo import MongoClient
import json
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

def read_config(path):
    with open(path, 'r') as f:
        return json.load(f)

config = read_config('kpi_predictor/config.json')

def connect_mongo_collection(collection_name):
    client = MongoClient(config["mongo_db"]["uri"])
    db = client[config["mongo_db"]["db"]]
    return db[collection_name]

# Initialize main DataFrame
dfs = pd.DataFrame()

# Loop through all collections and variables
for j in range(len(config["mongo_collection_features"])):
    aux = config["mongo_collection_features"][j]
    if len(aux)==3:
        collection, variable, elem = aux
    else:
        collection, variable = aux
        elem = 0
    data = connect_mongo_collection(collection).find()
    records = []

    for document in data:
        year = int(document["calculation_date"][:4])
        kpis=list(document["kpis"].items())
        if "kpis_predicted" in document.keys():
            kpis_predicted = [h[1] for h in list(document["kpis_predicted"].items())]
        else:
            kpis_predicted = [False] * len(kpis)
        for i in range(len(kpis)):
            building_reference, value = kpis[i]
            try:
                if isinstance(value, list):
                    value = float(value[elem])
                else:
                    value = float(value)
            except (ValueError, TypeError):
                value = None
            if kpis_predicted[i] == False:
                records.append({
                    "building_reference": building_reference,
                    "year": year,
                    variable: value
                })
    if len(records)>0:
        df = pd.DataFrame(records)
        df = df[df.year >= config["min_year"]]
        if variable in list(config["predictors_to_run"].keys()):
            df = df[
                df[config["predictors_to_run"][variable][4][0]].isin(
                    config["predictors_to_run"][variable][4][1])
            ]
        if dfs.empty:
            dfs = df
        else:
            if variable in dfs.columns:
                dfs = pd.concat([dfs, df], axis=0)
            else:
                dfs = pd.merge(dfs, df, on=["building_reference", "year"], how="outer")

# Create index and sort
dfs = dfs.set_index(["building_reference","year"])
dfs = dfs.sort_index(level=['building_reference', 'year'])

# Fill missing values forward and backward within each building group
fill_cols = dfs.columns.difference(list(config["predictors_to_run"].keys()))

# Apply ffill + bfill to selected columns grouped by building_reference
dfs[fill_cols] = dfs[fill_cols].groupby(level='building_reference').transform(lambda group: group.ffill().bfill())

# Filter dfs
dfs = dfs.groupby(dfs.index).filter(lambda x: not x["residents"].isna().any())
dfs.reset_index(inplace=True)

# Helper to run training and prediction
def run_predictor(df, target_col, input_cols, mongo_collection_name, min_val, max_val, n_splits=5, random_state=42):
    df_model = df.copy()

    # Filter training data
    known_mask = df_model[target_col].notna()
    in_range_mask = (df_model[target_col] >= min_val) & (df_model[target_col] <= max_val)
    train_mask = known_mask & in_range_mask

    X = df_model.loc[train_mask, input_cols].reset_index(drop=True)
    y = df_model.loc[train_mask, target_col].reset_index(drop=True)

    # Minimal hyperparameter grid
    param_grid = {
        'depth': [6, 8, 10],
        'learning_rate': [0.03, 0.1],
        'l2_leaf_reg': [6, 8, 10]
    }

    base_model = CatBoostRegressor(verbose=0, random_seed=random_state)
    grid = GridSearchCV(base_model, param_grid, cv=n_splits, scoring='neg_mean_squared_error', n_jobs=-1)
    grid.fit(X, y)

    best_model = grid.best_estimator_

    # Cross-validated predictions on training set
    oof_preds = np.zeros(len(y))
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train = y.iloc[train_idx]

        m = CatBoostRegressor(verbose=0, random_seed=random_state, **grid.best_params_)
        m.fit(X_train, y_train)
        oof_preds[val_idx] = m.predict(X_val)

    oof_preds_clamped = np.clip(oof_preds, min_val, max_val)
    rmse = np.sqrt(mean_squared_error(y, oof_preds_clamped))
    cvrmse = rmse / y.mean()
    r2 = r2_score(y, oof_preds_clamped)

    print(f"\n📊 Cross-validated results for '{target_col}':")
    print(f"   Best params: {grid.best_params_}")
    print(f"   CVRMSE:      {cvrmse*100:.2f}%")
    print(f"   R²:          {r2:.3f}")

    # Final model training on full filtered training data
    final_model = CatBoostRegressor(verbose=0, random_seed=random_state, **grid.best_params_)
    final_model.fit(X, y)

    # Predict all
    X_all = df_model[input_cols]
    all_preds = final_model.predict(X_all)
    all_preds_clamped = np.clip(all_preds, min_val, max_val)

    df_model["predicted_" + target_col] = all_preds_clamped
    df_model["used_prediction_" + target_col] = df_model[target_col].isna()
    df_model[target_col + "_filled"] = df_model[target_col].combine_first(
        pd.Series(all_preds_clamped, index=df_model.index)
    )

    # Upload filtered predictions and values to MongoDB
    for year in df_model["year"].unique():
        df_year = df_model[df_model["year"] == year]

        kpis = {
            row["building_reference"]: round(float(row[target_col + "_filled"]))
            for _, row in df_year.iterrows()
            if pd.notna(row[target_col + "_filled"])
            and min_val <= row[target_col + "_filled"] <= max_val
        }

        kpis_predicted = {
            row["building_reference"]: bool(row["used_prediction_" + target_col])
            for _, row in df_year.iterrows()
            if pd.notna(row[target_col + "_filled"])
            and min_val <= row[target_col + "_filled"] <= max_val
        }

        connect_mongo_collection(mongo_collection_name).update_one(
            {"calculation_date": f"{year}-01-01"},
            {"$set": {
                "calculation_date": f"{year}-01-01",
                "kpis": kpis,
                "kpis_predicted": kpis_predicted
            }},
            upsert=True
        )

    return df_model

for (target_col, (input_cols, mongo_collection, min_val, max_val, filters)) in config["predictors_to_run"].items():
    dfs = run_predictor(
        df=dfs,
        target_col=target_col,
        input_cols=input_cols,
        mongo_collection_name=mongo_collection,
        min_val=min_val,
        max_val=max_val
    )
    dfs[target_col] = dfs[f"{target_col}_filled"]