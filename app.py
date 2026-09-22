import gradio as gr
from query_engine import load_data
from validator import build_valid_values
from agent import ask

df = load_data()
valid_values = build_valid_values(df)

last_spec_state = {"spec": None}


def respond(message, history):
    answer, spec = ask(message, df, valid_values, previous_spec=last_spec_state["spec"])
    last_spec_state["spec"] = spec
    return answer


demo = gr.ChatInterface(
    fn=respond,
    title="WHO Hemoglobin Data Agent",
    description="Ask questions about hemoglobin levels across age groups, regions, and years (WHO GHO data, 2000-2019).",
    examples=[
        "What is the average Hb level by age group?",
        "Which region has the lowest average Hb?",
        "What percentage of children have Hb below 110?",
        "Compare Hb levels between pregnant and nonpregnant women",
        "Who is having low Hb levels?",
    ],
)

if __name__ == "__main__":
    demo.launch()