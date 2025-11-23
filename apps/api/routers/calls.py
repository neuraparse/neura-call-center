"""Call management endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.middleware.auth import require_api_key
from apps.core.database import get_db
from apps.core.logging import get_logger
from apps.models.api_key import APIKey
from apps.models.call import Call, CallStatus

logger = get_logger(__name__)
router = APIRouter()


class CreateCallRequest(BaseModel):
    """Request to create a new call."""

    phone_number: str = Field(..., description="Phone number to call")
    language: str = Field(default="en-US", description="Language code")
    agent_phone_number: str | None = Field(None, description="Agent phone number")
    task: str | None = Field(None, description="Call objective/task")
    claim_schema: list[dict] | None = Field(None, description="Custom claim schema")


class CallResponse(BaseModel):
    """Call response."""

    id: UUID
    phone_number: str
    status: CallStatus
    direction: str
    language: str
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None

    class Config:
        from_attributes = True


@router.post("/", response_model=CallResponse)
async def create_call(
    request: CreateCallRequest,
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(require_api_key),
):
    """
    Create a new outbound call.

    This endpoint initiates a new call to the specified phone number.
    """
    try:
        # Create call record
        call = Call(
            phone_number=request.phone_number,
            agent_phone_number=request.agent_phone_number or "+1234567890",  # TODO: Get from settings
            status=CallStatus.INITIATED,
            direction="outbound",
            language=request.language,
            provider="twilio",  # TODO: Get from settings
        )

        db.add(call)
        await db.commit()
        await db.refresh(call)

        logger.info(
            "Call created",
            call_id=str(call.id),
            phone_number=request.phone_number,
        )

        # TODO: Actually initiate the call via telephony provider
        # telephony = get_telephony_provider()
        # await telephony.make_call(...)

        return call

    except Exception as e:
        logger.error("Failed to create call", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(require_api_key),
):
    """Get call details by ID."""
    try:
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(status_code=404, detail="Call not found")

        return call

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get call", call_id=str(call_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[CallResponse])
async def list_calls(
    skip: int = 0,
    limit: int = 100,
    status: CallStatus | None = None,
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(require_api_key),
):
    """List calls with optional filtering."""
    try:
        query = select(Call)

        if status:
            query = query.where(Call.status == status)

        query = query.offset(skip).limit(limit).order_by(Call.created_at.desc())

        result = await db.execute(query)
        calls = result.scalars().all()

        return calls

    except Exception as e:
        logger.error("Failed to list calls", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{call_id}/hangup")
async def hangup_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(require_api_key),
):
    """Hang up an active call."""
    try:
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(status_code=404, detail="Call not found")

        # TODO: Actually hang up via telephony provider
        # telephony = get_telephony_provider()
        # await telephony.hangup_call(call.external_id)

        call.status = CallStatus.COMPLETED
        call.ended_at = datetime.utcnow()

        await db.commit()

        logger.info("Call hung up", call_id=str(call_id))

        return {"status": "success", "message": "Call hung up"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to hang up call", call_id=str(call_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

