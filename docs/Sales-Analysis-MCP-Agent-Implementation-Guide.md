# Sales Analysis MCP Agent Implementation Guide

## Overview

This guide provides step-by-step instructions to implement new sales analysis agents based on Model Context Protocol (MCP) server while deactivating current specialized agents, maintaining the Group Chat Manager and Planner functionality with human-in-the-loop capabilities.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create MCP Sales Analysis Tools](#step-1-create-mcp-sales-analysis-tools)
4. [Step 2: Implement Sales Analysis Agent](#step-2-implement-sales-analysis-agent)
5. [Step 3: Update Agent Factory](#step-3-update-agent-factory)
6. [Step 4: Deactivate Specialized Agents](#step-4-deactivate-specialized-agents)
7. [Step 5: Update Models and Enums](#step-5-update-models-and-enums)
8. [Step 6: Update Configuration](#step-6-update-configuration)
9. [Step 7: Testing](#step-7-testing)
10. [Step 8: Deployment](#step-8-deployment)

## Architecture Overview

### Current Architecture
- Multiple specialized agents (HR, Marketing, Product, etc.)
- Group Chat Manager for orchestration
- Planner Agent for task breakdown
- Human Agent for feedback loop

### New Architecture
- **Sales Analysis Agents** (MCP-based) for data analysis
- **Group Chat Manager** (maintained) for orchestration
- **Planner Agent** (maintained) for task breakdown
- **Human Agent** (maintained) for feedback loop
- Deactivated specialized agents (HR, Marketing, Product, etc.)

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent System                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Group Chat      │  │ Planner Agent   │  │ Human Agent  │ │
│  │ Manager         │  │                 │  │              │ │
│  │ (Maintained)    │  │ (Maintained)    │  │ (Maintained) │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Sales Analysis Agents (NEW)                  │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │ │
│  │  │ Revenue     │ │ Customer    │ │ Market Trends   │   │ │
│  │  │ Analysis    │ │ Analytics   │ │ Analysis        │   │ │
│  │  │ Agent       │ │ Agent       │ │ Agent           │   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 MCP Server                              │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │ │
│  │  │ Sales Data  │ │ Customer    │ │ Analytics       │   │ │
│  │  │ Connector   │ │ Database    │ │ Engine          │   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Azure Container Apps environment setup
- Access to sales data sources (Cosmos DB, SQL Database, etc.)
- MCP server framework knowledge

## Step 1: Create MCP Sales Analysis Tools

### 1.1 Create Sales Tools Directory Structure

```bash
mkdir -p src/backend/kernel_tools/sales_tools
mkdir -p src/backend/mcp_servers/sales_analysis
```

### 1.2 Create Sales Analysis MCP Tools

Create `src/backend/kernel_tools/sales_tools/sales_analysis_tools.py`:

```python
"""Sales Analysis Tools using MCP Server integration."""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from semantic_kernel.functions import kernel_function
from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

class SalesAnalysisTools:
    """Sales Analysis tools for MCP-based agents."""

    def __init__(self, mcp_client=None):
        """Initialize with MCP client connection."""
        self.mcp_client = mcp_client

    @kernel_function(
        description="Analyze revenue trends over a specified time period",
        name="analyze_revenue_trends"
    )
    async def analyze_revenue_trends(
        self,
        time_period: str = "last_30_days",
        region: str = "all",
        product_category: str = "all"
    ) -> str:
        """
        Analyze revenue trends for specified parameters.
        
        Args:
            time_period: Time period for analysis (last_30_days, last_quarter, last_year)
            region: Geographic region filter (all, north_america, europe, asia)
            product_category: Product category filter (all, beverages, snacks, etc.)
            
        Returns:
            JSON string with revenue analysis results
        """
        try:
            # Use MCP server to query sales data
            query_params = {
                "action": "analyze_revenue_trends",
                "time_period": time_period,
                "region": region,
                "product_category": product_category
            }
            
            # Mock MCP server call - replace with actual MCP implementation
            result = await self._call_mcp_server("sales_analysis", query_params)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @kernel_function(
        description="Analyze customer behavior and segmentation",
        name="analyze_customer_behavior"
    )
    async def analyze_customer_behavior(
        self,
        customer_segment: str = "all",
        metric_type: str = "purchase_frequency"
    ) -> str:
        """
        Analyze customer behavior patterns.
        
        Args:
            customer_segment: Customer segment to analyze (all, premium, regular, new)
            metric_type: Type of metric (purchase_frequency, average_order_value, retention_rate)
            
        Returns:
            JSON string with customer behavior analysis
        """
        try:
            query_params = {
                "action": "analyze_customer_behavior",
                "customer_segment": customer_segment,
                "metric_type": metric_type
            }
            
            result = await self._call_mcp_server("customer_analytics", query_params)
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error analyzing customer behavior: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @kernel_function(
        description="Generate market trends and competitive analysis",
        name="analyze_market_trends"
    )
    async def analyze_market_trends(
        self,
        market_segment: str = "beverages",
        analysis_type: str = "trend_analysis"
    ) -> str:
        """
        Analyze market trends and competitive positioning.
        
        Args:
            market_segment: Market segment to analyze
            analysis_type: Type of analysis (trend_analysis, competitive_analysis, forecast)
            
        Returns:
            JSON string with market analysis results
        """
        try:
            query_params = {
                "action": "analyze_market_trends",
                "market_segment": market_segment,
                "analysis_type": analysis_type
            }
            
            result = await self._call_mcp_server("market_analysis", query_params)
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    async def _call_mcp_server(self, server_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server with specified parameters."""
        # This is a placeholder for actual MCP server integration
        # Replace with actual MCP client calls
        
        if server_name == "sales_analysis":
            return {
                "revenue_trend": "increasing",
                "growth_rate": "15.2%",
                "total_revenue": "$2,450,000",
                "period": params.get("time_period", "unknown"),
                "region": params.get("region", "all"),
                "insights": [
                    "Revenue growth accelerated in the last quarter",
                    "Strong performance in premium product categories",
                    "Emerging markets showing significant potential"
                ]
            }
        elif server_name == "customer_analytics":
            return {
                "customer_segment": params.get("customer_segment", "all"),
                "metric_type": params.get("metric_type", "unknown"),
                "average_purchase_frequency": "2.3 times per month",
                "customer_retention_rate": "78%",
                "insights": [
                    "Premium customers show higher loyalty",
                    "New customer acquisition rate improved by 12%",
                    "Mobile app usage correlates with higher purchase frequency"
                ]
            }
        elif server_name == "market_analysis":
            return {
                "market_segment": params.get("market_segment", "unknown"),
                "market_size": "$15.2B",
                "growth_forecast": "8.5% CAGR",
                "competitive_position": "Market leader with 23% share",
                "insights": [
                    "Health-conscious trends driving premium segment growth",
                    "Sustainability concerns affecting brand preference",
                    "Digital marketing channels showing higher ROI"
                ]
            }
        
        return {"error": "Unknown server", "status": "failed"}

    @staticmethod
    def get_default_system_message() -> str:
        """Get the default system message for sales analysis agents."""
        return """You are a Sales Analysis Agent specialized in analyzing sales data, customer behavior, and market trends. 
        
        Your capabilities include:
        - Revenue trend analysis across different time periods and regions
        - Customer behavior analysis and segmentation
        - Market trend analysis and competitive positioning
        - Data-driven insights and recommendations
        
        When performing analysis:
        1. Always validate input parameters
        2. Provide clear, actionable insights
        3. Include relevant metrics and KPIs
        4. Suggest follow-up actions when appropriate
        5. If you need additional information, ask specific questions
        
        You work collaboratively with other agents through the Group Chat Manager and respond to human feedback appropriately."""
```

### 1.3 Create MCP Server Integration

Create `src/backend/mcp_servers/sales_analysis/mcp_server.py`:

```python
"""MCP Server for Sales Analysis."""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SalesAnalysisMCPServer:
    """MCP Server for sales analysis operations."""
    
    def __init__(self, cosmos_client=None, sql_client=None):
        """Initialize MCP server with database clients."""
        self.cosmos_client = cosmos_client
        self.sql_client = sql_client
        
    async def handle_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            if action == "analyze_revenue_trends":
                return await self._analyze_revenue_trends(params)
            elif action == "analyze_customer_behavior":
                return await self._analyze_customer_behavior(params)
            elif action == "analyze_market_trends":
                return await self._analyze_market_trends(params)
            else:
                return {"error": f"Unknown action: {action}", "status": "failed"}
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _analyze_revenue_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue trends using actual data sources."""
        # Implementation would query actual databases
        # This is a placeholder for demonstration
        
        time_period = params.get("time_period", "last_30_days")
        region = params.get("region", "all")
        product_category = params.get("product_category", "all")
        
        # Mock data - replace with actual database queries
        return {
            "revenue_trend": "increasing",
            "growth_rate": "15.2%",
            "total_revenue": "$2,450,000",
            "period": time_period,
            "region": region,
            "product_category": product_category,
            "insights": [
                f"Revenue growth for {region} region in {time_period}",
                f"Product category {product_category} showing strong performance",
                "Recommended to increase inventory for high-performing products"
            ],
            "data_points": [
                {"date": "2025-06-01", "revenue": 80000},
                {"date": "2025-06-15", "revenue": 85000},
                {"date": "2025-06-23", "revenue": 90000}
            ]
        }
    
    async def _analyze_customer_behavior(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer behavior patterns."""
        customer_segment = params.get("customer_segment", "all")
        metric_type = params.get("metric_type", "purchase_frequency")
        
        return {
            "customer_segment": customer_segment,
            "metric_type": metric_type,
            "key_metrics": {
                "total_customers": 12500,
                "active_customers": 8750,
                "average_order_value": "$45.30",
                "purchase_frequency": "2.3 times per month",
                "customer_lifetime_value": "$890"
            },
            "insights": [
                f"Customer segment {customer_segment} analysis completed",
                "Higher engagement through mobile app",
                "Loyalty program showing positive impact on retention"
            ]
        }
    
    async def _analyze_market_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends and competitive positioning."""
        market_segment = params.get("market_segment", "beverages")
        analysis_type = params.get("analysis_type", "trend_analysis")
        
        return {
            "market_segment": market_segment,
            "analysis_type": analysis_type,
            "market_data": {
                "market_size": "$15.2B",
                "growth_rate": "8.5% CAGR",
                "competitive_position": "Market leader with 23% share",
                "market_share_trend": "stable"
            },
            "trends": [
                "Health-conscious consumer preferences increasing",
                "Sustainability becoming key differentiator",
                "Premium segment outperforming mass market"
            ],
            "recommendations": [
                "Invest in sustainable packaging",
                "Expand premium product line",
                "Enhance digital marketing presence"
            ]
        }
```

## Step 2: Implement Sales Analysis Agent

### 2.1 Create Sales Analysis Agent

Create `src/backend/kernel_agents/sales_analysis_agent.py`:

```python
"""Sales Analysis Agent implementation using MCP server integration."""
from typing import Dict, List, Optional
import logging

from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import BaseAgent
from kernel_tools.sales_tools.sales_analysis_tools import SalesAnalysisTools
from models.messages_kernel import AgentType
from semantic_kernel.functions import KernelFunction

logger = logging.getLogger(__name__)

class SalesAnalysisAgent(BaseAgent):
    """Sales Analysis agent implementation using MCP server integration.

    This agent specializes in sales data analysis, customer behavior analysis,
    and market trend analysis using Model Context Protocol (MCP) servers.
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        tools: Optional[List[KernelFunction]] = None,
        system_message: Optional[str] = None,
        agent_name: str = AgentType.SALES_ANALYSIS.value,
        mcp_client=None,
        client=None,
        definition=None,
    ) -> None:
        """Initialize the Sales Analysis Agent.

        Args:
            session_id: The current session identifier
            user_id: The user identifier
            memory_store: The Cosmos memory context
            tools: List of tools available to this agent (optional)
            system_message: Optional system message for the agent
            agent_name: Optional name for the agent
            mcp_client: MCP client for server communication
            client: Optional client instance
            definition: Optional definition instance
        """
        # Load configuration if tools not provided
        if not tools:
            sales_tools = SalesAnalysisTools(mcp_client=mcp_client)
            tools = [
                sales_tools.analyze_revenue_trends,
                sales_tools.analyze_customer_behavior,
                sales_tools.analyze_market_trends,
            ]

        # Use system message from config if not explicitly provided
        if not system_message:
            system_message = SalesAnalysisTools.get_default_system_message()

        super().__init__(
            agent_name=agent_name,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            tools=tools,
            system_message=system_message,
            client=client,
            definition=definition,
        )

    @classmethod
    async def create(
        cls,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        mcp_client=None,
        client=None,
        **kwargs: Dict[str, str],
    ) -> "SalesAnalysisAgent":
        """Create a new Sales Analysis Agent instance."""
        return cls(
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            mcp_client=mcp_client,
            client=client,
            **kwargs
        )

    @staticmethod
    def default_system_message(agent_name=None) -> str:
        """Get the default system message for the sales analysis agent."""
        return SalesAnalysisTools.get_default_system_message()

    @property
    def agent_type(self) -> AgentType:
        """Return the agent type."""
        return AgentType.SALES_ANALYSIS
```

## Step 3: Update Agent Factory

### 3.1 Modify Agent Factory

Update `src/backend/kernel_agents/agent_factory.py`:

```python
"""Factory for creating agents in the Multi-Agent Custom Automation Engine."""
from typing import Any, Dict, Optional, Type
import logging

# Import the new AppConfig instance
from app_config import config
from azure.ai.agents.models import (ResponseFormatJsonSchema,
                                    ResponseFormatJsonSchemaType)
from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import BaseAgent
from kernel_agents.generic_agent import GenericAgent
from kernel_agents.group_chat_manager import GroupChatManager
# Import new sales analysis agent
from kernel_agents.sales_analysis_agent import SalesAnalysisAgent
# Keep core agents
from kernel_agents.human_agent import HumanAgent
from kernel_agents.planner_agent import PlannerAgent

# Comment out specialized agents
# from kernel_agents.hr_agent import HrAgent
# from kernel_agents.marketing_agent import MarketingAgent
# from kernel_agents.procurement_agent import ProcurementAgent
# from kernel_agents.product_agent import ProductAgent
# from kernel_agents.tech_support_agent import TechSupportAgent

from models.messages_kernel import AgentType, PlannerResponsePlan
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating agents in the Multi-Agent Custom Automation Engine."""

    # Updated mapping - removed specialized agents, added sales analysis
    _agent_classes: Dict[AgentType, Type[BaseAgent]] = {
        # Core agents (maintained)
        AgentType.GENERIC: GenericAgent,
        AgentType.HUMAN: HumanAgent,
        AgentType.PLANNER: PlannerAgent,
        AgentType.GROUP_CHAT_MANAGER: GroupChatManager,
        
        # New sales analysis agent
        AgentType.SALES_ANALYSIS: SalesAnalysisAgent,
        
        # Deactivated specialized agents
        # AgentType.HR: HrAgent,
        # AgentType.MARKETING: MarketingAgent,
        # AgentType.PRODUCT: ProductAgent,
        # AgentType.PROCUREMENT: ProcurementAgent,
        # AgentType.TECH_SUPPORT: TechSupportAgent,
    }

    # Updated agent tools mapping
    _agent_tools_mapping: Dict[AgentType, str] = {
        AgentType.GENERIC: "generic",
        AgentType.SALES_ANALYSIS: "sales_analysis",
        # Removed mappings for deactivated agents
    }

    # Cache for created agents
    _agent_cache: Dict[str, BaseAgent] = {}

    @classmethod
    async def create_agent(
        cls,
        agent_type: AgentType,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        client=None,
        mcp_client=None,
        **kwargs
    ) -> BaseAgent:
        """Create a single agent of the specified type."""
        
        cache_key = f"{agent_type.value}_{session_id}_{user_id}"
        
        # Return cached agent if available
        if cache_key in cls._agent_cache:
            return cls._agent_cache[cache_key]

        agent_class = cls._agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")

        try:
            # Special handling for sales analysis agent with MCP client
            if agent_type == AgentType.SALES_ANALYSIS:
                agent = await agent_class.create(
                    session_id=session_id,
                    user_id=user_id,
                    memory_store=memory_store,
                    client=client,
                    mcp_client=mcp_client,
                    **kwargs
                )
            else:
                agent = await agent_class.create(
                    session_id=session_id,
                    user_id=user_id,
                    memory_store=memory_store,
                    client=client,
                    **kwargs
                )
            
            # Cache the agent
            cls._agent_cache[cache_key] = agent
            return agent

        except Exception as e:
            logger.error(f"Error creating agent of type {agent_type}: {e}")
            raise

    @classmethod
    async def create_all_agents(
        cls,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        client=None,
        mcp_client=None
    ) -> Dict[str, BaseAgent]:
        """Create all available agents."""
        agents = {}
        
        for agent_type in cls._agent_classes.keys():
            try:
                agent = await cls.create_agent(
                    agent_type=agent_type,
                    session_id=session_id,
                    user_id=user_id,
                    memory_store=memory_store,
                    client=client,
                    mcp_client=mcp_client
                )
                agents[agent_type.value] = agent
            except Exception as e:
                logger.error(f"Failed to create agent {agent_type}: {e}")
                continue
        
        return agents

    @classmethod
    def get_available_agent_types(cls) -> List[AgentType]:
        """Get list of available agent types."""
        return list(cls._agent_classes.keys())

    @classmethod
    def clear_cache(cls):
        """Clear the agent cache."""
        cls._agent_cache.clear()
```

## Step 4: Deactivate Specialized Agents

### 4.1 Move Specialized Agents to Archive

```bash
# Create archive directory
mkdir -p src/backend/kernel_agents/archived

# Move specialized agents to archive
mv src/backend/kernel_agents/hr_agent.py src/backend/kernel_agents/archived/
mv src/backend/kernel_agents/marketing_agent.py src/backend/kernel_agents/archived/
mv src/backend/kernel_agents/product_agent.py src/backend/kernel_agents/archived/
mv src/backend/kernel_agents/procurement_agent.py src/backend/kernel_agents/archived/
mv src/backend/kernel_agents/tech_support_agent.py src/backend/kernel_agents/archived/

# Move corresponding tools to archive
mkdir -p src/backend/kernel_tools/archived
mv src/backend/kernel_tools/hr_tools src/backend/kernel_tools/archived/
mv src/backend/kernel_tools/marketing_tools src/backend/kernel_tools/archived/
mv src/backend/kernel_tools/product_tools src/backend/kernel_tools/archived/
mv src/backend/kernel_tools/procurement_tools src/backend/kernel_tools/archived/
mv src/backend/kernel_tools/tech_support_tools src/backend/kernel_tools/archived/
```

### 4.2 Create Archive Documentation

Create `src/backend/kernel_agents/archived/README.md`:

```markdown
# Archived Agents

This directory contains the previously active specialized agents that have been deactivated in favor of the new MCP-based sales analysis agents.

## Archived Agents:
- `hr_agent.py` - Human Resources agent
- `marketing_agent.py` - Marketing agent  
- `product_agent.py` - Product management agent
- `procurement_agent.py` - Procurement agent
- `tech_support_agent.py` - Technical support agent

## Archived Tools:
- `hr_tools/` - HR-related tools and functions
- `marketing_tools/` - Marketing-related tools and functions
- `product_tools/` - Product management tools and functions
- `procurement_tools/` - Procurement tools and functions
- `tech_support_tools/` - Technical support tools and functions

## Reactivation Process:
To reactivate any of these agents:
1. Move the agent file back to `src/backend/kernel_agents/`
2. Move the corresponding tools back to `src/backend/kernel_tools/`
3. Update the `AgentFactory` to include the agent type
4. Update the `AgentType` enum in models
5. Test the integration

## Date Archived: 2025-06-23
## Reason: Transition to MCP-based sales analysis agents
```

## Step 5: Update Models and Enums

### 5.1 Update AgentType Enum

Update `src/backend/models/messages_kernel.py`:

```python
# Find the AgentType enum and update it
class AgentType(str, Enum):
    """Enumeration of available agent types."""
    
    # Core agents (maintained)
    GENERIC = "Generic_Agent"
    HUMAN = "Human_Agent"
    PLANNER = "Planner_Agent"
    GROUP_CHAT_MANAGER = "Group_Chat_Manager"
    
    # New sales analysis agent
    SALES_ANALYSIS = "Sales_Analysis_Agent"
    
    # Deactivated agents (commented out)
    # HR = "Hr_Agent"
    # MARKETING = "Marketing_Agent"
    # PRODUCT = "Product_Agent"
    # PROCUREMENT = "Procurement_Agent"
    # TECH_SUPPORT = "Tech_Support_Agent"
```

### 5.2 Update Planner Agent Configuration

Update `src/backend/kernel_agents/planner_agent.py` to work with the new agent structure:

```python
# In the PlannerAgent class, update the available agents list
class PlannerAgent(BaseAgent):
    # ... existing code ...
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        tools: Optional[List[KernelFunction]] = None,
        system_message: Optional[str] = None,
        agent_name: str = AgentType.PLANNER.value,
        available_agents: List[str] = None,
        agent_instances: Optional[Dict[str, BaseAgent]] = None,
        client=None,
        definition=None,
    ) -> None:
        
        # Update available agents list to include only active agents
        if available_agents is None:
            available_agents = [
                AgentType.GENERIC.value,
                AgentType.SALES_ANALYSIS.value,
                AgentType.HUMAN.value,
            ]
        
        # ... rest of existing code ...
```

## Step 6: Update Configuration

### 6.1 Update Environment Variables

Add MCP server configuration to your environment variables:

```bash
# Add to your .env file or container app environment variables
MCP_SERVER_ENDPOINT=https://your-mcp-server-endpoint.com
MCP_SERVER_API_KEY=your-mcp-api-key
SALES_DATA_SOURCE=cosmos_db  # or sql_database
ENABLE_SALES_ANALYSIS=true
```

### 6.2 Update AppConfig

Update `src/backend/app_config.py`:

```python
class AppConfig:
    """Application configuration class that loads settings from environment variables."""

    def __init__(self):
        """Initialize the application configuration with environment variables."""
        # ... existing configuration ...
        
        # MCP Server settings
        self.MCP_SERVER_ENDPOINT = self._get_optional("MCP_SERVER_ENDPOINT")
        self.MCP_SERVER_API_KEY = self._get_optional("MCP_SERVER_API_KEY")
        self.SALES_DATA_SOURCE = self._get_optional("SALES_DATA_SOURCE", "cosmos_db")
        self.ENABLE_SALES_ANALYSIS = self._get_bool("ENABLE_SALES_ANALYSIS")
        
    def get_mcp_client(self):
        """Get MCP client for sales analysis."""
        # Implementation for MCP client creation
        # This would depend on your specific MCP server setup
        return None  # Placeholder
```

## Step 7: Testing

### 7.1 Create Test Script

Create `src/backend/tests/test_sales_analysis_agent.py`:

```python
"""Test script for Sales Analysis Agent."""
import asyncio
import pytest
from unittest.mock import Mock, patch

from kernel_agents.sales_analysis_agent import SalesAnalysisAgent
from context.cosmos_memory_kernel import CosmosMemoryContext
from models.messages_kernel import AgentType

class TestSalesAnalysisAgent:
    """Test cases for Sales Analysis Agent."""
    
    @pytest.fixture
    async def mock_memory_store(self):
        """Create mock memory store."""
        memory_store = Mock(spec=CosmosMemoryContext)
        return memory_store
    
    @pytest.fixture
    async def sales_agent(self, mock_memory_store):
        """Create sales analysis agent for testing."""
        return await SalesAnalysisAgent.create(
            session_id="test_session",
            user_id="test_user",
            memory_store=mock_memory_store
        )
    
    async def test_agent_creation(self, sales_agent):
        """Test that sales analysis agent is created correctly."""
        assert sales_agent.agent_type == AgentType.SALES_ANALYSIS
        assert sales_agent.agent_name == AgentType.SALES_ANALYSIS.value
        assert len(sales_agent.tools) > 0
    
    async def test_revenue_analysis(self, sales_agent):
        """Test revenue analysis functionality."""
        # Mock the tool call
        with patch.object(sales_agent, 'analyze_revenue_trends') as mock_analyze:
            mock_analyze.return_value = '{"revenue_trend": "increasing", "growth_rate": "15.2%"}'
            
            result = await sales_agent.analyze_revenue_trends(
                time_period="last_30_days",
                region="north_america"
            )
            
            assert "revenue_trend" in result
            mock_analyze.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
```

### 7.2 Update Test Endpoints Script

Update your existing `test_endpoints.py`:

```python
# Add test for sales analysis agent
def test_sales_analysis_task():
    """Test sales analysis task creation."""
    test_endpoint(
        "Create Sales Analysis Task",
        "POST",
        "/api/input_task",
        data={
            "session_id": "sales_test_session",
            "description": "Analyze revenue trends for the last quarter and provide insights on customer behavior"
        }
    )
```

### 7.3 Manual Testing Steps

1. **Test Agent Creation**:
   ```bash
   # Run the test script
   python src/backend/tests/test_sales_analysis_agent.py
   ```

2. **Test API Endpoints**:
   ```bash
   # Test the updated endpoints
   python test_endpoints.py
   ```

3. **Test Sales Analysis Task**:
   ```bash
   curl -X POST "https://cpo-acrasalesanalytics.jollyfield-479bc951.eastus2.azurecontainerapps.io/api/input_task" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "sales_analysis_test",
       "description": "Analyze our Q2 revenue performance and identify top-performing customer segments"
     }'
   ```

## Step 8: Deployment

### 8.1 Update Dockerfile

Ensure your `src/backend/Dockerfile` includes the new dependencies:

```dockerfile
# ... existing Dockerfile content ...

# Copy new sales analysis tools
COPY kernel_tools/sales_tools/ /app/kernel_tools/sales_tools/
COPY mcp_servers/ /app/mcp_servers/

# ... rest of Dockerfile ...
```

### 8.2 Build and Deploy

```bash
# Build the new image
az acr build --registry acracrasalesanalytics2 --image arcagent-be:v2.0 --file src/backend/Dockerfile src/backend/

# Update container app with new image
az containerapp update \
  --name cpo-acrasalesanalytics \
  --resource-group rg-AcraSalesAnalytics2 \
  --image acracrasalesanalytics2.azurecr.io/arcagent-be:v2.0

# Add new environment variables
az containerapp update --name cpo-acrasalesanalytics --resource-group rg-AcraSalesAnalytics2 \
  --set-env-vars \
    MCP_SERVER_ENDPOINT="https://your-mcp-server.com" \
    ENABLE_SALES_ANALYSIS="true" \
    SALES_DATA_SOURCE="cosmos_db"
```

### 8.3 Verification

1. **Check Container App Status**:
   ```bash
   az containerapp show --name cpo-acrasalesanalytics --resource-group rg-AcraSalesAnalytics2 \
     --query 'properties.runningStatus'
   ```

2. **Test New Functionality**:
   ```bash
   # Test with sales analysis task
   curl -X POST "https://cpo-acrasalesanalytics.jollyfield-479bc951.eastus2.azurecontainerapps.io/api/input_task" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "production_test",
       "description": "Provide a comprehensive sales analysis including revenue trends, customer segmentation, and market positioning for our beverage products"
     }'
   ```

3. **Monitor Logs**:
   ```bash
   az containerapp logs show --name cpo-acrasalesanalytics --resource-group rg-AcraSalesAnalytics2 --follow
   ```

## Migration Checklist

- [ ] Create MCP sales analysis tools
- [ ] Implement Sales Analysis Agent
- [ ] Update Agent Factory
- [ ] Archive specialized agents
- [ ] Update AgentType enum
- [ ] Update Planner Agent configuration  
- [ ] Add MCP configuration
- [ ] Create tests
- [ ] Build and deploy new image
- [ ] Update environment variables
- [ ] Verify functionality
- [ ] Monitor production logs

## Rollback Plan

If issues arise, you can quickly rollback:

1. **Restore Previous Image**:
   ```bash
   az containerapp update \
     --name cpo-acrasalesanalytics \
     --resource-group rg-AcraSalesAnalytics2 \
     --image acracrasalesanalytics2.azurecr.io/arcagent-be:latest
   ```

2. **Reactivate Specialized Agents**:
   ```bash
   # Move agents back from archive
   mv src/backend/kernel_agents/archived/*.py src/backend/kernel_agents/
   mv src/backend/kernel_tools/archived/* src/backend/kernel_tools/
   ```

3. **Update Agent Factory** to include the original agents

## Expected Results

After implementation, you should see:

1. **Simplified Agent Architecture**: Only core agents (Group Chat Manager, Planner, Human) plus new Sales Analysis Agent
2. **Enhanced Sales Capabilities**: Comprehensive sales analysis through MCP server integration
3. **Maintained Human-in-the-Loop**: All approval and feedback mechanisms preserved
4. **Better Performance**: Focused agent set with specialized sales analysis capabilities
5. **Extensible Framework**: Easy to add more MCP-based agents in the future

## Support and Troubleshooting

### Common Issues:

1. **MCP Server Connection Issues**: Check endpoint and API key configuration
2. **Agent Creation Failures**: Verify all dependencies are installed
3. **Tool Loading Errors**: Ensure sales tools are properly imported
4. **Performance Issues**: Monitor container app resources and scale if needed

### Debug Commands:

```bash
# Check container app logs
az containerapp logs show --name cpo-acrasalesanalytics --resource-group rg-AcraSalesAnalytics2

# Verify environment variables
az containerapp show --name cpo-acrasalesanalytics --resource-group rg-AcraSalesAnalytics2 \
  --query 'properties.template.containers[0].env'

# Test individual endpoints
curl -X GET "https://cpo-acrasalesanalytics.jollyfield-479bc951.eastus2.azurecontainerapps.io/api/plans"
```

This guide provides a comprehensive approach to transitioning from specialized agents to MCP-based sales analysis agents while maintaining the core functionality of your multi-agent system.
