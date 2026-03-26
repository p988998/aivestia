import operator
from typing import Annotated, TypedDict


class GraphState(TypedDict):
    question:   str
    datasource: str
    answer:     str
    context:    list
    news_urls:  list
    history:    Annotated[list, operator.add]
