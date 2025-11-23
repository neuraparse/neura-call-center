"""Call Center Agent using LangGraph v1.0 (2025 latest).

This agent handles customer service calls with:
- Tool calling for database and CRM operations
- Streaming responses for real-time interaction
- State management for conversation context
- Memory for multi-turn conversations

References:
- LangGraph v1.0: https://docs.langchain.com/oss/python/langgraph/overview
- StateGraph: https://docs.langchain.com/oss/python/langgraph/workflows-agents
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from apps.agents.tools.crm_tools import get_product_info, search_knowledge_base
from apps.agents.tools.database_tools import create_claim, get_call_history, get_customer_info
from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)


# Define agent state using MessagesState pattern (LangGraph v1.0)
class CallCenterState(MessagesState):
    """State for call center agent.
    
    Extends MessagesState with additional fields for call center context.
    """
    customer_id: str | None = None
    call_id: str | None = None
    intent: str | None = None  # Detected customer intent
    sentiment: str | None = None  # Customer sentiment (positive, neutral, negative)


# System prompt for call center agent
CALL_CENTER_SYSTEM_PROMPT = """You are a helpful and empathetic call center AI assistant.

Your role is to:
1. Greet customers warmly and professionally
2. Listen carefully to understand their needs
3. Use available tools to help resolve their issues
4. Provide accurate information from the knowledge base
5. Create claims when necessary
6. Maintain a friendly and professional tone

Available tools:
- get_customer_info: Get customer details and history
- get_call_history: Retrieve past call transcripts
- create_claim: Create a new claim for the customer
- search_knowledge_base: Search for policy and product information
- get_product_info: Get detailed product information

Guidelines:
- Always be polite and empathetic
- Ask clarifying questions when needed
- Summarize actions taken at the end
- If you can't help, escalate to a human agent
- Keep responses concise but informative

Current customer ID: {customer_id}
Current call ID: {call_id}
"""


class CallCenterAgent:
    """Call Center Agent using LangGraph v1.0.
    
    This agent uses StateGraph to manage conversation flow and tool calling.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        streaming: bool = True,
    ):
        """Initialize the call center agent.
        
        Args:
            model_name: LLM model to use
            temperature: Temperature for response generation
            streaming: Enable streaming responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.streaming = streaming
        
        # Initialize LLM with tool binding
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            api_key=settings.openai_api_key or "sk-test-key",  # Use test key if not set
        )
        
        # Define tools
        self.tools = [
            get_customer_info,
            get_call_history,
            create_claim,
            search_knowledge_base,
            get_product_info,
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build graph
        self.graph = self._build_graph()
        
        logger.info(
            "CallCenterAgent initialized",
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            tools_count=len(self.tools),
        )
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph with CallCenterState
        graph = StateGraph(CallCenterState)
        
        # Add nodes
        graph.add_node("agent", self._call_model)
        graph.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        graph.add_edge(START, "agent")
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        graph.add_edge("tools", "agent")
        
        # Compile graph
        return graph.compile()
    
    async def _call_model(self, state: CallCenterState) -> dict:
        """Call the LLM with current state.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with AI response
        """
        # Prepare system message with context
        system_message = SystemMessage(
            content=CALL_CENTER_SYSTEM_PROMPT.format(
                customer_id=state.get("customer_id", "Unknown"),
                call_id=state.get("call_id", "Unknown"),
            )
        )
        
        # Prepare messages
        messages = [system_message] + state["messages"]
        
        # Call LLM
        response = await self.llm_with_tools.ainvoke(messages)

        return {"messages": [response]}

    def _should_continue(self, state: CallCenterState) -> str:
        """Determine if we should continue to tools or end.

        Args:
            state: Current conversation state

        Returns:
            "continue" if there are tool calls, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]

        # If there are tool calls, continue to tools node
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"

        # Otherwise, end
        return "end"

    async def invoke(
        self,
        message: str,
        customer_id: str | None = None,
        call_id: str | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Invoke the agent with a message.

        Args:
            message: User message
            customer_id: Optional customer ID
            call_id: Optional call ID
            config: Optional runnable config

        Returns:
            Final state with AI response
        """
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "customer_id": customer_id,
            "call_id": call_id,
        }

        # Invoke graph
        result = await self.graph.ainvoke(initial_state, config=config)

        return result

    async def stream(
        self,
        message: str,
        customer_id: str | None = None,
        call_id: str | None = None,
        config: RunnableConfig | None = None,
    ):
        """Stream agent responses in real-time.

        Args:
            message: User message
            customer_id: Optional customer ID
            call_id: Optional call ID
            config: Optional runnable config

        Yields:
            State updates as they occur
        """
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "customer_id": customer_id,
            "call_id": call_id,
        }

        # Stream graph execution
        async for chunk in self.graph.astream(initial_state, config=config):
            yield chunk

    async def stream_events(
        self,
        message: str,
        customer_id: str | None = None,
        call_id: str | None = None,
        config: RunnableConfig | None = None,
    ):
        """Stream detailed events including token-by-token streaming.

        Args:
            message: User message
            customer_id: Optional customer ID
            call_id: Optional call ID
            config: Optional runnable config

        Yields:
            Detailed events including LLM tokens
        """
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "customer_id": customer_id,
            "call_id": call_id,
        }

        # Stream events with version v2 for token streaming
        async for event in self.graph.astream_events(
            initial_state,
            config=config,
            version="v2",
        ):
            yield event

    def get_graph_visualization(self) -> str:
        """Get Mermaid diagram of the graph.

        Returns:
            Mermaid diagram string
        """
        try:
            from langgraph.graph import draw_mermaid
            return draw_mermaid(self.graph)
        except ImportError:
            return "Install langgraph[mermaid] to visualize the graph"

