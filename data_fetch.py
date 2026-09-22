import requests
import pandas as pd

indicators = {
    "HEMOGLOBINLEVEL_CHILDREN_MEAN": "children",
    "HEMOGLOBINLEVEL_NONPREGNANT_MEAN": "nonpregnant",
    "HEMOGLOBINLEVEL_PREGNANT_MEAN": "pregnant",
    "HEMOGLOBINLEVEL_REPRODUCTIVEAGE_MEAN": "reproductive_age",
}

frames = []
for code, label in indicators.items():
    url = f"https://ghoapi.azureedge.net/api/{code}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    d = pd.DataFrame(r.json()["value"])
    d["AgeGroup"] = label
    frames.append(d)

combined = pd.concat(frames, ignore_index=True)

# Keep only country-level rows (drop REGION/GLOBAL aggregates)
combined = combined[combined["SpatialDimType"] == "COUNTRY"].copy()

# Fetch country name lookup
url = "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues"
r = requests.get(url, timeout=30)
r.raise_for_status()
countries = pd.DataFrame(r.json()["value"])[["Code", "Title"]]
countries = countries.rename(columns={"Code": "SpatialDim", "Title": "Country"})

# Join country names
combined = combined.merge(countries, on="SpatialDim", how="left")

# Keep only the columns we actually need
final = combined[[
    "Country", "SpatialDim", "ParentLocation", "AgeGroup",
    "TimeDim", "NumericValue"
]].rename(columns={
    "SpatialDim": "CountryCode",
    "ParentLocation": "Region",
    "TimeDim": "Year",
    "NumericValue": "Value",
})

print(final.shape)
print(final.head(10))
print(final.isna().sum())

final.to_csv("hb_data_clean.csv", index=False)
print("\nSaved to hb_data_clean.csv")