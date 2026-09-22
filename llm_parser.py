from dotenv import load_dotenv
import os
import json
from huggingface_hub import InferenceClient
from validator import validate_spec, build_valid_values
from query_engine import load_data

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found. Check your .env file.")

client = InferenceClient(token=HF_TOKEN)

MODEL = "meta-llama/Llama-3.1-8B-Instruct"

SYSTEM_PROMPT = """You convert questions about hemoglobin (Hb) level data into a JSON query spec. Respond with ONLY valid JSON, no explanation, no markdown formatting.

The dataset has these columns:
- Country (e.g. "India", "Kenya")
- Region: one of "Africa", "Americas", "Europe", "Eastern Mediterranean", "South-East Asia", "Western Pacific"
- AgeGroup: one of "children", "pregnant", "nonpregnant", "reproductive_age"
- Year: 2000 to 2019
- Value: the Hb level (numeric)

Output this exact JSON shape:
{
  "metric": "mean" | "median" | "std" | "min" | "max" | "count" | "sum",
  "group_by": [list of column names, or empty list],
  "filters": {"ColumnName": "value", ...},
  "threshold": number or null,
  "threshold_op": "<" | ">" | "<=" | ">=" or null,
  "sort": "asc" | "desc" or null,
  "top_n": integer or null,
  "distribution": true or false
}

Examples:

Q: What is the average Hb level by age group?
A: {"metric": "mean", "group_by": ["AgeGroup"], "filters": {}, "threshold": null, "threshold_op": null, "sort": null, "top_n": null, "distribution": false}

Q: Which region has the lowest average Hb?
A: {"metric": "mean", "group_by": ["Region"], "filters": {}, "threshold": null, "threshold_op": null, "sort": "asc", "top_n": 1, "distribution": false}

Q: What percentage of pregnant women in Africa have Hb below 110?
A: {"metric": "mean", "group_by": [], "filters": {"AgeGroup": "pregnant", "Region": "Africa"}, "threshold": 110, "threshold_op": "<", "sort": null, "top_n": null, "distribution": false}

Q: Show the distribution of Hb levels
A: {"metric": "mean", "group_by": [], "filters": {}, "threshold": null, "threshold_op": null, "sort": null, "top_n": null, "distribution": true}

Q: Who is having low Hb levels?
A: {"metric": "mean", "group_by": ["Country"], "filters": {}, "threshold": null, "threshold_op": null, "sort": "asc", "top_n": 10, "distribution": false}

IMPORTANT: When a question asks "who" or uses vague language like "low Hb", "high Hb", "worst", "best" without naming specific columns to group by, default to group_by: ["Country"] (since "who" implies specific entities, not just categories), and set sort + a reasonable top_n (5-10) rather than returning every combination. Only group by AgeGroup or Region when those are explicitly the subject of the question (e.g. "which age group" or "which region").
"""

def parse_question(question, previous_spec=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if previous_spec:
        context_note = (
            f"The previous question's query spec was: {json.dumps(previous_spec)}. "
            f"If the new question is a short follow-up (a single word, a name, or a phrase like "
            f"'what about X' or 'just pregnant women'), treat it as adding or changing a FILTER only. "
            f"Keep group_by, sort, and top_n EXACTLY the same as the previous spec unless the new question "
            f"explicitly asks for a different grouping (e.g. 'by region instead', 'break it down by year'). "
            f"If the new question is a complete, self-contained question unrelated to the previous one, "
            f"ignore the previous spec entirely."
        )
        messages.append({"role": "system", "content": context_note})

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=300,
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw), raw


def parse_and_validate(question, valid_values, previous_spec=None):
    spec, raw = parse_question(question, previous_spec=previous_spec)
    errors = validate_spec(spec, valid_values)
    if errors:
        return None, errors
    return spec, None


if __name__ == "__main__":
    df = load_data()
    valid_values = build_valid_values(df)

    test_questions = [
        "What is the average Hb level by age group?",
        "Which country has the lowest Hb?",
        "Compare Hb levels between pregnant and nonpregnant women",
        "What percentage of children in Asia have Hb below 110?",
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        spec, errors = parse_and_validate(q, valid_values)
        if errors:
            print("VALIDATION FAILED:", errors)
        else:
            print("Valid spec:", spec)
