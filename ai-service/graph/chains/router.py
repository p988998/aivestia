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

system = """You are an expert router that assigns a user query to the correct agent.

## Agents
chat_agent:
- General investing questions
- ETF knowledge and concepts
- Market prices, news, historical trends
- Educational explanations

portfolio_agent:
- Portfolio analysis and allocation review
- Rebalancing suggestions
- Investment recommendations or advice
- Any question involving personal holdings

## Routing Rules

Route to portfolio_agent if:
- The user asks for investment advice or recommendations
- The user asks "should I buy", "what should I invest in", "recommend"
- The user mentions their own holdings
- The user asks about allocation, rebalancing, or portfolio construction

Route to chat_agent if:
- The question is informational or educational
- The question asks about prices, news, or market data
- The question asks about general investing concepts

## Ambiguity Handling
If the query is ambiguous:
- If it implies a decision → portfolio_agent
- Otherwise → chat_agent

## Examples
Q: What is an ETF? → chat_agent
Q: What's VTI's current price? → chat_agent
Q: How has BND performed this year? → chat_agent
Q: Should I buy VTI or QQQ? → portfolio_agent
Q: What should I invest in given my risk level? → portfolio_agent
Q: I have VTI and BND, should I rebalance? → portfolio_agent
Q: Recommend an ETF for a medium risk investor → portfolio_agent
Q: What are the risks of investing in bonds? → chat_agent"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router