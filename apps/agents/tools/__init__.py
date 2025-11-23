"""Tools for LangGraph agents."""

from apps.agents.tools.database_tools import (
    get_call_history,
    get_customer_info,
    create_claim,
)
from apps.agents.tools.crm_tools import (
    search_knowledge_base,
    get_product_info,
)

__all__ = [
    "get_call_history",
    "get_customer_info",
    "create_claim",
    "search_knowledge_base",
    "get_product_info",
]

