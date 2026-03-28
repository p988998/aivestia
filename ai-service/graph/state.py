import operator
from typing import Annotated, Optional, TypedDict


class GraphState(TypedDict):
    question:     str
    datasource:   str
    answer:       str
    context:      list
    news_urls:    list
    history:      Annotated[list, operator.add]
    user_profile: dict
    tool_outputs: list
    grounded:     bool
    retry_count:  int
    simulations:  Optional[list]
