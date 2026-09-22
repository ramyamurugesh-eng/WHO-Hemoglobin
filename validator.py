import pandas as pd
from difflib import get_close_matches

VALID_METRICS = {"mean", "median", "std", "min", "max", "count", "sum"}
VALID_COLUMNS = {"Country", "CountryCode", "Region", "AgeGroup", "Year", "Value"}
VALID_THRESHOLD_OPS = {"<", ">", "<=", ">="}


def build_valid_values(df):
    return {
        "Region": set(df["Region"].unique()),
        "AgeGroup": set(df["AgeGroup"].unique()),
        "Country": set(df["Country"].unique()),
        "Year": set(df["Year"].unique()),
    }


def suggest_column(col, valid_columns):
    matches = get_close_matches(col, valid_columns, n=1, cutoff=0.5)
    return matches[0] if matches else None


def suggest_value(val, valid_set):
    close = [v for v in valid_set if str(val).lower() in str(v).lower()]
    if close:
        return close[0]
    matches = get_close_matches(str(val), [str(v) for v in valid_set], n=1, cutoff=0.5)
    return matches[0] if matches else None


def validate_spec(spec, valid_values):
    errors = []

    metric = spec.get("metric", "mean")
    if metric not in VALID_METRICS:
        hint_m = suggest_column(metric, VALID_METRICS)
        hint = f" Did you mean '{hint_m}'?" if hint_m else ""
        errors.append(f"Invalid metric '{metric}'.{hint}")

    for col in spec.get("group_by") or []:
        if col not in VALID_COLUMNS:
            hint_c = suggest_column(col, VALID_COLUMNS)
            hint = f" Did you mean '{hint_c}'?" if hint_c else ""
            errors.append(f"Invalid group_by column '{col}'.{hint}")

    filters = spec.get("filters") or {}
    for col, val in filters.items():
        if col not in VALID_COLUMNS:
            hint_c = suggest_column(col, VALID_COLUMNS)
            hint = f" Did you mean '{hint_c}'?" if hint_c else ""
            errors.append(f"Invalid filter column '{col}'.{hint}")
            continue
        if val is None:
            continue
        check_vals = val if isinstance(val, list) else [val]
        for v in check_vals:
            if col in valid_values and v not in valid_values[col]:
                hint_v = suggest_value(v, valid_values[col])
                hint = f" Did you mean '{hint_v}'?" if hint_v else ""
                errors.append(f"Invalid value '{v}' for filter '{col}'.{hint}")

    op = spec.get("threshold_op")
    if op is not None and op not in VALID_THRESHOLD_OPS:
        errors.append(f"Invalid threshold_op '{op}'. Must be one of {VALID_THRESHOLD_OPS}.")

    if spec.get("threshold") is not None and not isinstance(spec["threshold"], (int, float)):
        errors.append("threshold must be a number.")

    return errors


if __name__ == "__main__":
    from query_engine import load_data

    df = load_data()
    valid_values = build_valid_values(df)

    print("1. Valid spec (group_by + metric):")
    print(validate_spec({"group_by": ["Region"], "metric": "mean"}, valid_values))

    print("\n2. Valid spec with correct filter:")
    print(validate_spec({"filters": {"Region": "Africa"}, "metric": "median"}, valid_values))

    print("\n3. Bad group_by column (should suggest close match):")
    print(validate_spec({"group_by": ["Gender"], "metric": "mean"}, valid_values))

    print("\n4. Bad filter column, close to 'Region':")
    print(validate_spec({"filters": {"Regoin": "Africa"}}, valid_values))

    print("\n5. Bad filter value 'Asia' (should suggest 'South-East Asia'):")
    print(validate_spec({"filters": {"Region": "Asia"}}, valid_values))

    print("\n6. Bad filter value with typo, e.g. 'Afria' (should suggest 'Africa'):")
    print(validate_spec({"filters": {"Region": "Afria"}}, valid_values))

    print("\n7. Bad metric, close to 'mean':")
    print(validate_spec({"metric": "average"}, valid_values))

    print("\n8. Bad metric, no close match at all:")
    print(validate_spec({"metric": "xyzzy"}, valid_values))

    print("\n9. Bad AgeGroup filter value, e.g. 'pregnent' (typo):")
    print(validate_spec({"filters": {"AgeGroup": "pregnent"}}, valid_values))

    print("\n10. Multiple errors at once:")
    print(validate_spec({"group_by": ["Gender"], "metric": "average", "filters": {"Region": "Asia"}}, valid_values))