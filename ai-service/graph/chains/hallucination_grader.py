from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class GradeHallucinations(BaseModel):
    """Binary grounding score for a generated answer."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' = answer is grounded in the provided tool outputs. 'no' = answer contains information not supported by tool outputs."
    )


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

system = """You are grading whether an AI-generated answer is grounded in the provided tool outputs.
Tool outputs include retrieved documents, real-time market data, and news summaries.
If the key claims in the answer are supported by the tool outputs, grade 'yes'.
If the answer introduces facts or figures not present in the tool outputs, grade 'no'."""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Tool outputs:\n{tool_outputs}\n\nGenerated answer:\n{generation}"),
    ]
)

hallucination_grader = grade_prompt | structured_llm_grader
