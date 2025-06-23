# Adding and Removing Specialized Agents

## Overview

The Multi-Agent Custom Automation Engine is designed with extensibility in mind. Adding new specialized agents or removing existing ones is straightforward due to the system's well-architected design using factory patterns and consistent interfaces.

**Ease Rating: 8/10** - The architecture is designed for extensibility with minimal changes required to core orchestration logic.

## Adding a New Specialized Agent

Adding a new agent involves creating the agent's tools, implementing the agent class, and registering it with the factory. The orchestration logic remains unchanged.

### Step 1: Create the Agent Tools Class

Create a new file in the `/src/backend/kernel_tools/` directory. For example, to add a Finance Agent:

```python
# filepath: /src/backend/kernel_tools/finance_tools.py
from typing import Callable, get_type_hints
from semantic_kernel.functions import kernel_function
from models.messages_kernel import AgentType

class FinanceTools:
    agent_name = "FinanceAgent"
    
    @staticmethod
    @kernel_function(description="Process expense reimbursement for an employee")
    async def process_expense_reimbursement(employee_name: str, amount: float, description: str) -> str:
        return f"Processed expense reimbursement of ${amount} for {employee_name}: {description}"
    
    @staticmethod
    @kernel_function(description="Generate financial report for a department")
    async def generate_financial_report(department: str, period: str) -> str:
        return f"Generated financial report for {department} for period: {period}"
    
    @classmethod
    def get_all_kernel_functions(cls) -> dict[str, Callable]:
        # Implementation similar to other tool classes
        kernel_functions = {}
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, "__kernel_function__"):
                kernel_functions[name] = method
        return kernel_functions
    
    @classmethod
    def generate_tools_json_doc(cls) -> str:
        # Implementation similar to other tool classes
        # See generic_tools.py for full implementation
```

### Step 2: Create the Agent Class

Create a new file in the `/src/backend/kernel_agents/` directory:

```python
# filepath: /src/backend/kernel_agents/finance_agent.py
import logging
from typing import Dict, List, Optional

from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import BaseAgent
from kernel_tools.finance_tools import FinanceTools
from models.messages_kernel import AgentType
from semantic_kernel.functions import KernelFunction

class FinanceAgent(BaseAgent):
    """Finance agent implementation using Semantic Kernel."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        tools: Optional[List[KernelFunction]] = None,
        system_message: Optional[str] = None,
        agent_name: str = "FinanceAgent",
        client=None,
        definition=None,
    ) -> None:
        if not tools:
            tools_dict = FinanceTools.get_all_kernel_functions()
            tools = [KernelFunction.from_method(func) for func in tools_dict.values()]
        
        if not system_message:
            system_message = self.default_system_message(agent_name)
        
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
    
    @staticmethod
    def default_system_message(agent_name=None) -> str:
        return "You are a Finance agent. You handle financial operations, budgeting, expense management, and financial reporting."
```

### Step 3: Update the Agent Factory

Modify `src/backend/kernel_agents/agent_factory.py`:

```python
# Add import
from kernel_agents.finance_agent import FinanceAgent

class AgentFactory:
    # Update the _agent_classes mapping
    _agent_classes: Dict[AgentType, Type[BaseAgent]] = {
        AgentType.HR: HrAgent,
        AgentType.MARKETING: MarketingAgent,
        AgentType.PRODUCT: ProductAgent,
        AgentType.PROCUREMENT: ProcurementAgent,
        AgentType.TECH_SUPPORT: TechSupportAgent,
        AgentType.GENERIC: GenericAgent,
        AgentType.HUMAN: HumanAgent,
        AgentType.PLANNER: PlannerAgent,
        AgentType.GROUP_CHAT_MANAGER: GroupChatManager,
        # Add new agent (if using enum)
        # AgentType.FINANCE: FinanceAgent,
    }
    
    # If not using enum, you can use string mapping
    _agent_type_strings: Dict[str, str] = {
        # ... existing mappings ...
        "FinanceAgent": "FinanceAgent",
    }
    
    # Add system message
    _agent_system_messages: Dict[str, str] = {
        # ... existing messages ...
        "FinanceAgent": FinanceAgent.default_system_message(),
    }
```

### Step 4: Update the Planner Agent

Modify `src/backend/kernel_agents/planner_agent.py` to include the new agent:

```python
# In the __init__ method, update _available_agents:
self._available_agents = available_agents or [
    AgentType.HUMAN.value,
    AgentType.HR.value,
    AgentType.MARKETING.value,
    AgentType.PRODUCT.value,
    AgentType.PROCUREMENT.value,
    AgentType.TECH_SUPPORT.value,
    AgentType.GENERIC.value,
    "FinanceAgent",  # Add new agent
]

# Update _agent_tools_list:
self._agent_tools_list = {
    # ... existing tools ...
    "FinanceAgent": FinanceTools.generate_tools_json_doc(),
}
```

### Step 5: (Optional) Update AgentType Enum

If you prefer using enums over strings, update `src/backend/models/messages_kernel.py`:

```python
class AgentType(str, Enum):
    HR = "HrAgent"
    MARKETING = "MarketingAgent"
    PRODUCT = "ProductAgent"
    PROCUREMENT = "ProcurementAgent"
    TECH_SUPPORT = "TechSupportAgent"
    GENERIC = "GenericAgent"
    HUMAN = "HumanAgent"
    PLANNER = "PlannerAgent"
    GROUP_CHAT_MANAGER = "GroupChatManager"
    FINANCE = "FinanceAgent"  # Add new agent type
```

## Removing an Existing Agent

Removing an agent is even simpler. For example, to remove the ProcurementAgent:

### Step 1: Update Agent Factory

Remove references from `src/backend/kernel_agents/agent_factory.py`:

```python
class AgentFactory:
    _agent_classes: Dict[AgentType, Type[BaseAgent]] = {
        AgentType.HR: HrAgent,
        AgentType.MARKETING: MarketingAgent,
        AgentType.PRODUCT: ProductAgent,
        # AgentType.PROCUREMENT: ProcurementAgent,  # Remove this line
        AgentType.TECH_SUPPORT: TechSupportAgent,
        # ... rest of agents
    }
    
    # Remove from other mappings as well
    _agent_type_strings: Dict[str, str] = {
        # ... existing mappings ...
        # "ProcurementAgent": "ProcurementAgent",  # Remove this line
    }
    
    _agent_system_messages: Dict[str, str] = {
        # ... existing messages ...
        # "ProcurementAgent": ProcurementAgent.default_system_message(),  # Remove this line
    }
```

### Step 2: Update Planner Agent

Remove from available agents in `src/backend/kernel_agents/planner_agent.py`:

```python
self._available_agents = available_agents or [
    AgentType.HUMAN.value,
    AgentType.HR.value,
    AgentType.MARKETING.value,
    AgentType.PRODUCT.value,
    # AgentType.PROCUREMENT.value,  # Remove this line
    AgentType.TECH_SUPPORT.value,
    AgentType.GENERIC.value,
]

# Also remove from _agent_tools_list
self._agent_tools_list = {
    # ... existing tools ...
    # AgentType.PROCUREMENT.value: ProcurementTools.generate_tools_json_doc(),  # Remove
}
```

### Step 3: (Optional) Clean Up Files

- Delete `src/backend/kernel_agents/procurement_agent.py`
- Delete `src/backend/kernel_tools/procurement_tools.py`
- Remove import statements from agent_factory.py
- Remove from AgentType enum if using enums

## Why It's Easy

### 1. Factory Pattern
The `AgentFactory` centralizes agent creation, so you only need to update mappings in one place.

### 2. Consistent Interface
All agents inherit from `BaseAgent`, ensuring they implement the same methods:
- `handle_action_request()`
- `create()`
- `default_system_message()`

### 3. Tool Separation
Agent tools are separate from agent logic, making it easy to add/modify capabilities without touching the agent implementation.

### 4. Orchestration Independence
The `GroupChatManager` and orchestration logic don't need changes - they work with any agent that follows the interface.

### 5. Dynamic Discovery
The planner dynamically discovers available agents and their tools through the factory.

## Impact on Orchestration

The orchestration logic remains unchanged because:

- **Standardized Communication**: All agents communicate through standardized messages (`ActionRequest`, `ActionResponse`)
- **Abstract Interface**: The `GroupChatManager` uses agent instances through the base interface
- **Dynamic Planning**: The planner generates steps based on available agents at runtime
- **Consistent Execution**: All agents follow the same execution pattern through `handle_action_request`

## Best Practices

### When Adding Agents

1. **Follow Naming Conventions**: Use consistent naming (e.g., `FinanceAgent`, `FinanceTools`)
2. **Implement All Required Methods**: Ensure your agent implements all abstract methods from `BaseAgent`
3. **Document Tools Clearly**: Use descriptive `@kernel_function` decorations for tool discovery
4. **Test in Isolation**: Test your agent independently before integrating
5. **Update Documentation**: Document the agent's capabilities and use cases

### When Removing Agents

1. **Check Dependencies**: Ensure no other components directly depend on the agent
2. **Clean Imports**: Remove all import statements referencing the agent
3. **Test Thoroughly**: Verify the system works correctly after removal
4. **Update Documentation**: Remove references from user documentation

## Example: Complete Finance Agent Implementation

Here's a complete example of adding a Finance Agent:

### finance_tools.py
```python
import inspect
from typing import Callable, get_type_hints
from semantic_kernel.functions import kernel_function

class FinanceTools:
    agent_name = "FinanceAgent"
    
    @staticmethod
    @kernel_function(description="Calculate budget allocation for a project")
    async def calculate_budget_allocation(
        project_name: str,
        total_budget: float,
        categories: str
    ) -> str:
        """Calculate and allocate budget across different categories."""
        return f"Allocated budget for {project_name}: Total ${total_budget} across {categories}"
    
    @staticmethod
    @kernel_function(description="Generate expense report for an employee")
    async def generate_expense_report(
        employee_id: str,
        start_date: str,
        end_date: str
    ) -> str:
        """Generate detailed expense report for the specified period."""
        return f"Generated expense report for employee {employee_id} from {start_date} to {end_date}"
    
    @staticmethod
    @kernel_function(description="Process invoice payment")
    async def process_invoice_payment(
        invoice_id: str,
        amount: float,
        vendor_name: str
    ) -> str:
        """Process payment for a vendor invoice."""
        return f"Processed payment of ${amount} for invoice {invoice_id} to vendor {vendor_name}"
    
    @classmethod
    def get_all_kernel_functions(cls) -> dict[str, Callable]:
        """Get all kernel functions defined in this class."""
        kernel_functions = {}
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, "__kernel_function__"):
                kernel_functions[name] = method
        return kernel_functions
    
    @classmethod
    def generate_tools_json_doc(cls) -> str:
        """Generate JSON documentation for all tools."""
        tools_doc = []
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, "__kernel_function__"):
                func_info = method.__kernel_function__
                tools_doc.append({
                    "function": name,
                    "description": func_info.description,
                    "arguments": str(get_type_hints(method))
                })
        
        import json
        return json.dumps(tools_doc, indent=2)
```

This design makes the system highly extensible while maintaining stability in the core orchestration components. New agents can be added and existing ones removed without affecting the overall system architecture.
