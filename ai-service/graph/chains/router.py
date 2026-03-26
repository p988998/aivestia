from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class RouteQuery(BaseModel):
    """Route a user query to the most relevant agent."""

    datasource: Literal["chat_agent", "portfolio_agent"] = Field(
        ...,
        description="Given a user question choose to route it to the chat agent or the portfolio agent.",
    )


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are an expert at routing a user question to the right agent.

chat_agent: handles general investing questions, ETF knowledge, market prices, 
            news, and historical price trends.

portfolio_agent: handles analysis of the user's specific portfolio — 
                 allocation review, rebalancing suggestions, risk assessment 
                 based on the user's age and investment horizon.

Route to portfolio_agent only when the user is asking about their own portfolio
or mentions assets they personally hold. For everything else, route to chat_agent."""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router