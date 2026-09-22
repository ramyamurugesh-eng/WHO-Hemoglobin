import pandas as pd

def load_data(path="hb_data_clean.csv"):
    return pd.read_csv(path)

def run_query(df, spec):
    """
    spec keys:
      target_col: always "Value" for this dataset
      metric: mean, median, std, min, max, count
      group_by: list of columns, e.g. ["AgeGroup"], ["Region"], ["Country"]
      filters: dict, e.g. {"Region": "Africa", "AgeGroup": "pregnant"}
      threshold: number (optional)
      threshold_op: "<", ">", "<=", ">=" (optional)
      sort: "asc" or "desc" (optional)
      top_n: int (optional)
      distribution: bool (optional)
    """
    d = _apply_filters(df, spec.get("filters"))
    target_col = spec.get("target_col", "Value")

    if not len(d):
        return {"type": "error", "value": "No data matches these filters."}

    if spec.get("threshold") is not None:
        op = spec.get("threshold_op", "<")
        ops = {
            "<": d[target_col].lt, ">": d[target_col].gt,
            "<=": d[target_col].le, ">=": d[target_col].ge,
        }
        pct = float(ops[op](spec["threshold"]).mean() * 100)
        return {"type": "percentage", "value": round(pct, 2)}

    if spec.get("distribution"):
        bins = spec.get("bins", 10)
        hist = pd.cut(d[target_col], bins=bins)
        counts = hist.value_counts().sort_index()
        return {"type": "distribution",
                "value": {str(k): int(v) for k, v in counts.items()}}

    group_by = spec.get("group_by") or []
    if group_by:
        agg = d.groupby(group_by)[target_col].agg(spec.get("metric", "mean")).round(2)
        if spec.get("sort"):
            agg = agg.sort_values(ascending=(spec["sort"] == "asc"))
        if spec.get("top_n"):
            agg = agg.head(spec["top_n"])
        return {"type": "grouped", "value": agg.to_dict()}

    val = d[target_col].agg(spec.get("metric", "mean"))
    return {"type": "scalar", "value": round(float(val), 2)}


def _apply_filters(df, filters):
    if not filters:
        return df
    d = df
    for col, val in filters.items():
        if val is None:
            continue
        if isinstance(val, list):
            d = d[d[col].isin(val)]
        else:
            d = d[d[col] == val]
    return d


# quick manual test
if __name__ == "__main__":
    df = load_data()

    # "average Hb by age group"
    print(run_query(df, {"group_by": ["AgeGroup"], "metric": "mean"}))

    # "which region has the lowest average Hb"
    print(run_query(df, {"group_by": ["Region"], "metric": "mean", "sort": "asc", "top_n": 1}))

    # "% of records below 110 in Africa"
    print(run_query(df, {"filters": {"Region": "Africa"}, "threshold": 110, "threshold_op": "<"}))

    # "compare pregnant vs nonpregnant"
    print(run_query(df, {
        "group_by": ["AgeGroup"],
        "metric": "mean",
        "filters": {"AgeGroup": ["pregnant", "nonpregnant"]}
    }))