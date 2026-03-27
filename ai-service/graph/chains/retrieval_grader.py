from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    """Binary relevance score for a retrieved document."""

    binary_score: Literal["yes", "no"] = Field(
        description="Is the document relevant to the question? 'yes' or 'no'."
    )


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

system = """You are grading whether a retrieved document is relevant to a user's investment question.
If the document contains information related to the question (keywords, financial concepts, assets mentioned), grade it as 'yes'.
If it is off-topic or unrelated, grade it as 'no'.
Give a binary score 'yes' or 'no'."""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document:\n{document}\n\nUser question:\n{question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
