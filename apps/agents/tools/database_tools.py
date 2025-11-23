"""Database tools for LangGraph agents.

These tools allow agents to interact with the database to retrieve
customer information, call history, and create claims.

Uses LangChain 2025 latest tool decorator.
"""

from typing import Annotated

from langchain_core.tools import tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.database import get_db
from apps.core.logging import get_logger
from apps.models.call import Call
from apps.models.claim import Claim
from apps.models.conversation import Conversation

logger = get_logger(__name__)


@tool
async def get_customer_info(
    customer_id: Annotated[str, "The unique identifier for the customer"],
) -> dict:
    """Get customer information from the database.
    
    Args:
        customer_id: The unique identifier for the customer
        
    Returns:
        Dictionary containing customer information including:
        - customer_id: Customer ID
        - total_calls: Total number of calls
        - recent_calls: List of recent call IDs
        - active_claims: List of active claim IDs
    """
    try:
        async for db in get_db():
            # Get total calls
            result = await db.execute(
                select(Call).where(Call.customer_id == customer_id)
            )
            calls = result.scalars().all()
            
            # Get active claims
            result = await db.execute(
                select(Claim).where(
                    Claim.customer_id == customer_id,
                    Claim.status.in_(["open", "in_progress"])
                )
            )
            claims = result.scalars().all()
            
            return {
                "customer_id": customer_id,
                "total_calls": len(calls),
                "recent_calls": [str(call.id) for call in calls[:5]],
                "active_claims": [str(claim.id) for claim in claims],
            }
    except Exception as e:
        logger.error("Error getting customer info", error=str(e), customer_id=customer_id)
        return {
            "error": f"Failed to get customer info: {str(e)}",
            "customer_id": customer_id,
        }


@tool
async def get_call_history(
    call_id: Annotated[str, "The unique identifier for the call"],
) -> dict:
    """Get call history and conversation transcript.
    
    Args:
        call_id: The unique identifier for the call
        
    Returns:
        Dictionary containing:
        - call_id: Call ID
        - status: Call status
        - duration: Call duration in seconds
        - transcript: Full conversation transcript
        - messages: List of conversation messages
    """
    try:
        async for db in get_db():
            # Get call
            result = await db.execute(
                select(Call).where(Call.id == call_id)
            )
            call = result.scalar_one_or_none()
            
            if not call:
                return {"error": f"Call {call_id} not found"}
            
            # Get conversation
            result = await db.execute(
                select(Conversation).where(Conversation.call_id == call_id)
            )
            conversation = result.scalar_one_or_none()
            
            messages = []
            if conversation and conversation.messages:
                messages = conversation.messages
            
            return {
                "call_id": str(call.id),
                "status": call.status,
                "duration": call.duration_seconds or 0,
                "transcript": conversation.transcript if conversation else "",
                "messages": messages,
            }
    except Exception as e:
        logger.error("Error getting call history", error=str(e), call_id=call_id)
        return {"error": f"Failed to get call history: {str(e)}"}


@tool
async def create_claim(
    customer_id: Annotated[str, "The customer ID"],
    claim_type: Annotated[str, "Type of claim (e.g., 'refund', 'complaint', 'technical_issue')"],
    description: Annotated[str, "Detailed description of the claim"],
    priority: Annotated[str, "Priority level: 'low', 'medium', 'high', 'urgent'"] = "medium",
) -> dict:
    """Create a new claim for a customer.
    
    Args:
        customer_id: The customer ID
        claim_type: Type of claim
        description: Detailed description
        priority: Priority level (default: medium)
        
    Returns:
        Dictionary containing:
        - claim_id: Created claim ID
        - status: Claim status
        - message: Success message
    """
    try:
        async for db in get_db():
            claim = Claim(
                customer_id=customer_id,
                claim_type=claim_type,
                description=description,
                priority=priority,
                status="open",
            )
            db.add(claim)
            await db.commit()
            await db.refresh(claim)
            
            return {
                "claim_id": str(claim.id),
                "status": claim.status,
                "message": f"Claim created successfully with ID {claim.id}",
            }
    except Exception as e:
        logger.error("Error creating claim", error=str(e), customer_id=customer_id)
        return {"error": f"Failed to create claim: {str(e)}"}

