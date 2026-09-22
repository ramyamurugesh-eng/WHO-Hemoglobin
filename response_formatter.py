def format_result(spec, result):
    """Turn a run_query() result into a readable sentence/list."""
    rtype = result["type"]
    value = result["value"]

    if rtype == "error":
        return value

    if rtype == "scalar":
        metric = spec.get("metric", "mean")
        return f"The {metric} Hb level is {value} g/L."

    if rtype == "percentage":
        op = spec.get("threshold_op", "<")
        threshold = spec.get("threshold")
        op_words = {"<": "below", ">": "above", "<=": "at or below", ">=": "at or above"}

        filters = spec.get("filters") or {}
        if filters:
            filter_desc = []
            for col, val in filters.items():
                val_str = " or ".join(val) if isinstance(val, list) else str(val)
                filter_desc.append(f"{col.lower()} = {val_str}")
            context = " for " + ", ".join(filter_desc)
        else:
            context = ""

        return f"{value}% of records{context} are {op_words.get(op, op)} {threshold} g/L."

    if rtype == "grouped":
        group_by = spec.get("group_by", [])
        metric = spec.get("metric", "mean")
        label = " and ".join(group_by) if group_by else "group"

        lines = [f"Here are the {metric} Hb levels by {label}:"]
        for key, val in value.items():
            if isinstance(key, tuple):
                key_str = " / ".join(str(k) for k in key)
            else:
                key_str = str(key)
            key_str = key_str.replace("_", " ").title()
            lines.append(f"- {key_str}: {val} g/L")
        return "\n".join(lines)

    if rtype == "distribution":
        lines = ["Here's the distribution of Hb levels:"]
        for bucket, count in value.items():
            lines.append(f"- {bucket}: {count} records")
        return "\n".join(lines)

    return str(value)


if __name__ == "__main__":
    from query_engine import load_data, run_query

    df = load_data()

    spec1 = {"group_by": ["AgeGroup"], "metric": "mean"}
    result1 = run_query(df, spec1)
    print(format_result(spec1, result1))

    print()

    spec2 = {"filters": {"Region": "Africa"}, "threshold": 110, "threshold_op": "<"}
    result2 = run_query(df, spec2)
    print(format_result(spec2, result2))

    print()

    spec3 = {"group_by": ["Region"], "metric": "mean", "sort": "asc"}
    result3 = run_query(df, spec3)
    print(format_result(spec3, result3))