from pprint import pprint

from dotenv import load_dotenv

load_dotenv()


# from graph.chains.generation import generation_chain
# from graph.chains.hallucination_grader import (GradeHallucinations,
#                                                hallucination_grader)
# from graph.chains.retrieval_grader import GradeDocuments, retrieval_grader
from graph.chains.router import RouteQuery, question_router
# from ingestion import retriever




def test_router_to_chat_agent() -> None:
    question = "what is etf"

    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "chat_agent"


def test_router_to_portfolio_agent() -> None:
    question = "I have VTI and BND in my portfolio, should I rebalance?"

    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "portfolio_agent"