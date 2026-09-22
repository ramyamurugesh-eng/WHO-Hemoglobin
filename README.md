# WHO Hemoglobin Data Query Agent

A natural-language query agent for WHO Global Health Observatory hemoglobin (Hb) data. Ask questions in plain English — an LLM interprets the intent, and Pandas performs the actual computation, keeping numeric answers accurate rather than hallucinated.

## What it does

Ask things like:
- "What is the average Hb level by age group?"
- "Which region has the lowest average Hb?"
- "Who is having low Hb levels?"
- "Compare Hb levels between pregnant and nonpregnant women"
- "What percentage of children have Hb below 110?"

The agent supports genuinely open-ended questions, not just a fixed set of templates.

## Architecture

1. **Data pipeline** (`data_fetch.py`) — pulls hemoglobin indicator data directly from the WHO GHO API (children, pregnant, nonpregnant, and reproductive-age mean Hb levels), joins country names, and produces a clean long-format dataset.
2. **LLM intent parser** (`llm_parser.py`) — a Hugging Face-hosted LLM converts a natural-language question into a structured JSON query spec (metric, group-by columns, filters, sort, threshold). It also merges short follow-up questions with the previous query's context.
3. **Validator** (`validator.py`) — checks the LLM's output against the real dataset's columns and values before anything runs, catching hallucinated filters or invalid columns, with fuzzy "did you mean" suggestions for typos.
4. **Query engine** (`query_engine.py`) — a single generic Pandas function executes any valid spec: grouping, filtering, aggregating, sorting, thresholding, or computing a distribution. The LLM never touches the data directly — it only decides *what* to compute.
5. **Response formatter** (`response_formatter.py`) — turns the computed result back into a readable sentence or list.
6. **Interface** (`app.py`) — a Gradio chat interface tying it all together.

## Why this design

Keeping the LLM out of the arithmetic (it only fills a schema, never computes a number) avoids a common failure mode in LLM-powered data tools: confidently wrong numbers. Every number shown to the user comes from Pandas running against real WHO data.

## Data source

World Health Organization, Global Health Observatory (GHO) API — mean hemoglobin levels by country, 2000–2019, across four population groups: children, pregnant women, nonpregnant women, and women of reproductive age.

## Running locally

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

Create a `.env` file with a Hugging Face access token:
```
HF_TOKEN=your_token_here
```

Fetch the data:
```bash
python data_fetch.py
```

Run the app:
```bash
python app.py
```

## Known limitations

- This indicator family (WHO GHO hemoglobin data) has no sex-based breakdown — all four categories are female life-stage groups, so "compare male vs female" isn't answerable with this dataset.
- Single-word follow-up questions (e.g. just "children") are sometimes parsed inconsistently by the LLM compared to fuller follow-up phrasing.
- Data covers 2000–2019 only, as published by WHO GHO.

## Author

Ramya Murugesh