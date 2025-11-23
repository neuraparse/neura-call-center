"""Example usage of CallCenterAgent with LangGraph v1.0.

This example demonstrates:
1. Basic agent invocation
2. Streaming responses
3. Token-by-token streaming
4. Tool calling
5. Multi-turn conversations

Run with:
    python examples/agent_example.py
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.agents.call_agent import CallCenterAgent
from apps.core.logging import get_logger

logger = get_logger(__name__)


async def example_basic_invocation():
    """Example 1: Basic agent invocation."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Agent Invocation")
    print("="*80 + "\n")
    
    agent = CallCenterAgent(streaming=False)
    
    result = await agent.invoke(
        message="Hello, I need help with my recent order",
        customer_id="CUST-12345",
        call_id="CALL-001",
    )
    
    # Get last AI message
    last_message = result["messages"][-1]
    print(f"Agent: {last_message.content}\n")


async def example_streaming():
    """Example 2: Streaming responses."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Streaming Responses")
    print("="*80 + "\n")
    
    agent = CallCenterAgent(streaming=True)
    
    print("User: What is your refund policy?\n")
    print("Agent: ", end="", flush=True)
    
    async for chunk in agent.stream(
        message="What is your refund policy?",
        customer_id="CUST-12345",
    ):
        # Print node updates
        for node_name, node_data in chunk.items():
            if "messages" in node_data:
                last_msg = node_data["messages"][-1]
                if hasattr(last_msg, "content") and last_msg.content:
                    print(last_msg.content, end="", flush=True)
    
    print("\n")


async def example_token_streaming():
    """Example 3: Token-by-token streaming."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Token-by-Token Streaming")
    print("="*80 + "\n")
    
    agent = CallCenterAgent(streaming=True)
    
    print("User: Tell me about product PROD-001\n")
    print("Agent: ", end="", flush=True)
    
    async for event in agent.stream_events(
        message="Tell me about product PROD-001",
        customer_id="CUST-12345",
    ):
        # Stream LLM tokens
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)
    
    print("\n")


async def example_tool_calling():
    """Example 4: Tool calling."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Tool Calling")
    print("="*80 + "\n")
    
    agent = CallCenterAgent(streaming=False)
    
    print("User: I want to create a claim for a defective product\n")
    
    result = await agent.invoke(
        message="I want to create a claim for a defective product. "
                "My customer ID is CUST-12345 and the product is broken.",
        customer_id="CUST-12345",
        call_id="CALL-002",
    )
    
    # Print all messages
    for msg in result["messages"]:
        if hasattr(msg, "content") and msg.content:
            role = msg.__class__.__name__.replace("Message", "")
            print(f"{role}: {msg.content}\n")


async def example_multi_turn():
    """Example 5: Multi-turn conversation."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Multi-Turn Conversation")
    print("="*80 + "\n")
    
    agent = CallCenterAgent(streaming=False)
    
    # Conversation history
    messages = []
    
    # Turn 1
    print("User: Hi, I need help\n")
    result = await agent.invoke(
        message="Hi, I need help",
        customer_id="CUST-12345",
    )
    messages = result["messages"]
    print(f"Agent: {messages[-1].content}\n")
    
    # Turn 2 - Continue conversation
    print("User: What products do you have?\n")
    # In a real scenario, you'd maintain state across turns
    result = await agent.invoke(
        message="What products do you have?",
        customer_id="CUST-12345",
    )
    print(f"Agent: {result['messages'][-1].content}\n")


async def main():
    """Run all examples."""
    print("\n🤖 CallCenterAgent Examples - LangGraph v1.0 (2025)")
    print("="*80)
    
    try:
        # Run examples
        await example_basic_invocation()
        await example_streaming()
        await example_token_streaming()
        await example_tool_calling()
        await example_multi_turn()
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error("Error running examples", error=str(e))
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())

