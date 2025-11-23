"""CRM and knowledge base tools for LangGraph agents.

These tools allow agents to search knowledge bases and retrieve
product information.

Uses LangChain 2025 latest tool decorator.
"""

from typing import Annotated

from langchain_core.tools import tool

from apps.core.logging import get_logger

logger = get_logger(__name__)


# Mock knowledge base - in production, this would query a vector database
KNOWLEDGE_BASE = {
    "refund_policy": {
        "title": "Refund Policy",
        "content": "Customers can request a refund within 30 days of purchase. "
                  "Refunds are processed within 5-7 business days. "
                  "Items must be in original condition.",
        "category": "policy",
    },
    "shipping_info": {
        "title": "Shipping Information",
        "content": "Standard shipping takes 3-5 business days. "
                  "Express shipping takes 1-2 business days. "
                  "Free shipping on orders over $50.",
        "category": "shipping",
    },
    "technical_support": {
        "title": "Technical Support",
        "content": "For technical issues, try restarting the device first. "
                  "Check for software updates. "
                  "Contact support if the issue persists.",
        "category": "support",
    },
    "warranty_info": {
        "title": "Warranty Information",
        "content": "All products come with a 1-year manufacturer warranty. "
                  "Extended warranty available for purchase. "
                  "Warranty covers manufacturing defects only.",
        "category": "warranty",
    },
}

# Mock product catalog
PRODUCT_CATALOG = {
    "PROD-001": {
        "id": "PROD-001",
        "name": "Premium Headphones",
        "price": 199.99,
        "category": "Electronics",
        "in_stock": True,
        "description": "High-quality wireless headphones with noise cancellation",
    },
    "PROD-002": {
        "id": "PROD-002",
        "name": "Smart Watch",
        "price": 299.99,
        "category": "Electronics",
        "in_stock": True,
        "description": "Fitness tracking smartwatch with heart rate monitor",
    },
    "PROD-003": {
        "id": "PROD-003",
        "name": "Laptop Stand",
        "price": 49.99,
        "category": "Accessories",
        "in_stock": False,
        "description": "Ergonomic aluminum laptop stand",
    },
}


@tool
async def search_knowledge_base(
    query: Annotated[str, "The search query to find relevant information"],
    category: Annotated[str | None, "Optional category filter (policy, shipping, support, warranty)"] = None,
) -> dict:
    """Search the knowledge base for relevant information.
    
    Args:
        query: The search query
        category: Optional category filter
        
    Returns:
        Dictionary containing:
        - results: List of matching knowledge base articles
        - count: Number of results found
    """
    try:
        query_lower = query.lower()
        results = []
        
        for key, article in KNOWLEDGE_BASE.items():
            # Filter by category if specified
            if category and article["category"] != category:
                continue
            
            # Simple keyword matching (in production, use vector similarity)
            if (query_lower in article["title"].lower() or 
                query_lower in article["content"].lower()):
                results.append({
                    "id": key,
                    "title": article["title"],
                    "content": article["content"],
                    "category": article["category"],
                })
        
        return {
            "results": results,
            "count": len(results),
            "query": query,
        }
    except Exception as e:
        logger.error("Error searching knowledge base", error=str(e), query=query)
        return {"error": f"Failed to search knowledge base: {str(e)}"}


@tool
async def get_product_info(
    product_id: Annotated[str, "The product ID to retrieve information for"],
) -> dict:
    """Get detailed product information.
    
    Args:
        product_id: The product ID
        
    Returns:
        Dictionary containing product details:
        - id: Product ID
        - name: Product name
        - price: Product price
        - category: Product category
        - in_stock: Stock availability
        - description: Product description
    """
    try:
        product = PRODUCT_CATALOG.get(product_id)
        
        if not product:
            return {
                "error": f"Product {product_id} not found",
                "available_products": list(PRODUCT_CATALOG.keys()),
            }
        
        return product
    except Exception as e:
        logger.error("Error getting product info", error=str(e), product_id=product_id)
        return {"error": f"Failed to get product info: {str(e)}"}

