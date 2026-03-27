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
            news, historical price trends, and conceptual explanations.

portfolio_agent: handles analysis of the user's specific portfolio, allocation review,
                 rebalancing suggestions, AND explicit requests for investment
                 recommendations or advice.

Route to portfolio_agent when:
- The user mentions assets they personally hold
- The user asks for a specific recommendation ("should I buy", "what should I invest in",
  "which ETF do you recommend for me", "help me pick")

Route to chat_agent for everything else.

Examples:
Q: "What is an ETF?" -> chat_agent
Q: "What's VTI's current price?" -> chat_agent
Q: "How has BND performed this year?" -> chat_agent
Q: "Should I buy VTI or QQQ?" -> portfolio_agent
Q: "What should I invest in given my risk level?" -> portfolio_agent
Q: "I have VTI and BND, should I rebalance?" -> portfolio_agent
Q: "Recommend an ETF for a medium risk investor" -> portfolio_agent
Q: "What are the risks of investing in bonds?" -> chat_agent"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router