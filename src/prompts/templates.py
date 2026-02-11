from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
        "You must return ONLY a valid JSON object.\n"
        "Do NOT include explanations, markdown, examples, or extra text.\n\n"
        "{format_instructions}"
    ),
    input_variables=["topic", "difficulty"],
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
        "You must return ONLY a valid JSON object.\n"
        "Do NOT include explanations, markdown, examples, or extra text.\n\n"
        "{format_instructions}"
    ),
    input_variables=["topic", "difficulty"],
)
