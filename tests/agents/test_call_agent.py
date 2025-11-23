"""Tests for CallCenterAgent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from apps.agents.call_agent import CallCenterAgent, CallCenterState


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = CallCenterAgent(
        model_name="gpt-4o-mini",
        temperature=0.7,
        streaming=True,
    )
    
    assert agent.model_name == "gpt-4o-mini"
    assert agent.temperature == 0.7
    assert agent.streaming is True
    assert len(agent.tools) == 5
    assert agent.graph is not None


@pytest.mark.asyncio
async def test_should_continue_with_tool_calls():
    """Test _should_continue with tool calls."""
    agent = CallCenterAgent()
    
    # Create mock message with tool calls
    mock_message = MagicMock()
    mock_message.tool_calls = [{"name": "get_customer_info", "args": {}}]
    
    state = {
        "messages": [mock_message],
        "customer_id": "CUST-123",
    }
    
    result = agent._should_continue(state)
    assert result == "continue"


@pytest.mark.asyncio
async def test_should_continue_without_tool_calls():
    """Test _should_continue without tool calls."""
    agent = CallCenterAgent()
    
    # Create mock message without tool calls
    mock_message = AIMessage(content="Hello, how can I help you?")
    
    state = {
        "messages": [mock_message],
        "customer_id": "CUST-123",
    }
    
    result = agent._should_continue(state)
    assert result == "end"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires OpenAI API key and makes real API calls")
async def test_agent_invoke():
    """Test agent invocation."""
    agent = CallCenterAgent(streaming=False)
    
    result = await agent.invoke(
        message="Hello, I need help",
        customer_id="CUST-123",
        call_id="CALL-001",
    )
    
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert result["customer_id"] == "CUST-123"
    assert result["call_id"] == "CALL-001"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires OpenAI API key and makes real API calls")
async def test_agent_streaming():
    """Test agent streaming."""
    agent = CallCenterAgent(streaming=True)
    
    chunks = []
    async for chunk in agent.stream(
        message="What is your refund policy?",
        customer_id="CUST-123",
    ):
        chunks.append(chunk)
    
    assert len(chunks) > 0


@pytest.mark.asyncio
@pytest.mark.skip(reason="Mock LLM test requires complex async setup")
async def test_agent_with_mock_llm():
    """Test agent with mocked LLM."""
    # This test is skipped because mocking async LangChain components
    # requires complex setup. Use integration tests with real API instead.
    pass


@pytest.mark.asyncio
async def test_call_center_state():
    """Test CallCenterState structure."""
    state = CallCenterState(
        messages=[HumanMessage(content="Hello")],
        customer_id="CUST-123",
        call_id="CALL-001",
        intent="greeting",
        sentiment="positive",
    )
    
    assert len(state["messages"]) == 1
    assert state["customer_id"] == "CUST-123"
    assert state["call_id"] == "CALL-001"
    assert state["intent"] == "greeting"
    assert state["sentiment"] == "positive"


def test_graph_visualization():
    """Test graph visualization."""
    agent = CallCenterAgent()
    
    # This should not raise an error
    viz = agent.get_graph_visualization()
    assert isinstance(viz, str)

