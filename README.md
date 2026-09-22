# WHO Hemoglobin Data Query Agent

Ask questions in plain English, get real answers from WHO health data — an LLM parses intent, Pandas does the math.

A natural-language query agent for WHO Global Health Observatory hemoglobin (Hb) data. The LLM never computes a number directly — it only interprets the question and converts it into a structured query, which a validation layer checks against the real dataset before Pandas executes it. This reduces the risk of fabricated numerical answers by keeping the actual computation deterministic.

## What It Does

Ask things like:
- "What is the average Hb level by age group?"
- "Which region has the lowest average Hb?"
- "Who is having low Hb levels?"
- "Compare Hb levels between pregnant and nonpregnant women"
- "What percentage of children have Hb below 110?"

The agent supports genuinely open-ended questions, not just a fixed set of templates — including short follow-ups that build on the previous question.

## Example Results

**Which country has the lowest hemoglobin value?**
Burkina Faso — 89.0 g/L

**In Burkina Faso, show the average Hb level for each age group.**
- Children: 91.85 g/L
- Pregnant: 105.90 g/L
- Nonpregnant: 117.35 g/L
- Reproductive age: 116.00 g/L

## Architecture

1. **Data pipeline** (`data_fetch.py`) — pulls hemoglobin indicator data directly from the WHO GHO API (children, pregnant, nonpregnant, and reproductive-age mean Hb levels), joins country names, and produces a clean long-format dataset.
2. **LLM intent parser** (`llm_parser.py`) — a Hugging Face-hosted LLM converts a natural-language question into a structured JSON query spec (metric, group-by columns, filters, sort, threshold), and merges short follow-up questions with the previous query's context.
3. **Validator** (`validator.py`) — checks the LLM's output against the real dataset's columns and values before anything runs, catching hallucinated filters or invalid columns, with fuzzy "did you mean" suggestions for typos.
4. **Query engine** (`query_engine.py`) — a single generic Pandas function executes any valid spec: grouping, filtering, aggregating, sorting, thresholding, or computing a distribution. The LLM never touches the data directly — it only decides *what* to compute.
5. **Response formatter** (`response_formatter.py`) — turns the computed result back into a readable sentence or list.
6. **Interface** (`app.py`) — a Gradio chat interface tying it all together.

## Data Source

World Health Organization — Global Health Observatory (GHO) API.
Mean hemoglobin levels by country, covering 2000–2019, across children, pregnant women, nonpregnant women, and women of reproductive age.

## Technology Stack

Python · Pandas · Hugging Face LLM · WHO GHO API · Gradio

## Running Locally

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

Create a `.env` file:
```
HF_TOKEN=your_token_here
```

Fetch the data:
```bash
python data_fetch.py
```

Run the application:
```bash
python app.py
```

## Known Limitations

- The dataset does not provide a male/female sex-based breakdown.
- Very short follow-up questions may occasionally be interpreted inconsistently by the LLM.
- The available data covers 2000–2019.
- Semantic ambiguity in natural-language questions can still affect interpretation.

## Author

Ramya Murugesh