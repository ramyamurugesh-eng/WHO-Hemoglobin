from query_engine import load_data, run_query
from validator import build_valid_values
from llm_parser import parse_and_validate
from response_formatter import format_result


def ask(question, df, valid_values, previous_spec=None):
    spec, errors = parse_and_validate(question, valid_values, previous_spec=previous_spec)
    if errors:
        return f"Sorry, I couldn't understand that question clearly: {'; '.join(errors)}", None

    result = run_query(df, spec)
    answer = format_result(spec, result)
    return answer, spec  # return spec too, so caller can track it


if __name__ == "__main__":
    df = load_data()
    valid_values = build_valid_values(df)

    # simulate a follow-up conversation
    last_spec = None

    q1 = "Who is having low Hb levels?"
    print(f"\nQ: {q1}")
    answer, last_spec = ask(q1, df, valid_values, previous_spec=last_spec)
    print(answer)

    q2 = "what about just pregnant women?"
    print(f"\nQ: {q2}")
    answer, last_spec = ask(q2, df, valid_values, previous_spec=last_spec)
    print(answer)

    q3 = "children"
    print(f"\nQ: {q3}")
    answer, last_spec = ask(q3, df, valid_values, previous_spec=last_spec)
    print(answer)