# Backend Architecture Overview

## Introduction

The Multi-Agent Custom Automation Engine backend is a sophisticated AI-powered orchestration system built with FastAPI and Azure services. This document provides a comprehensive overview of the backend architecture, its components, and how they work together to process user tasks through collaborative AI agents.

## Architecture Overview

This is an AI-powered orchestration system that uses multiple specialized agents to handle complex tasks. The system follows a microservices-inspired pattern with:

1. **FastAPI Backend** ([`src/backend/app_kernel.py`](../../src/backend/app_kernel.py)) - Main API server with endpoints for task management
2. **Agent System** - Multiple specialized agents (HR, Product, Marketing, Tech Support, etc.)
3. **Memory Store** - Cosmos DB for persistent storage
4. **Azure AI Integration** - Using Azure OpenAI and AI Project services

## Key Components

### 1. Agent Types

The system includes several specialized agents:

- **PlannerAgent** - Creates execution plans from user tasks
- **GroupChatManager** - Orchestrates communication between agents
- **HrAgent** - Handles HR tasks (onboarding, benefits, etc.)
- **ProductAgent** - Manages product-related operations
- **MarketingAgent** - Handles marketing campaigns and analysis
- **TechSupportAgent** - IT support and technical operations
- **ProcurementAgent** - Purchasing and vendor management
- **HumanAgent** - Interfaces with human users for feedback

### 2. Core Workflow

```
User Input → RAI Check → Plan Creation → Step Execution → Human Feedback → Completion
```

### 3. Data Models

- **InputTask** - User's initial request
- **Plan** - High-level execution plan
- **Step** - Individual actions within a plan
- **AgentMessage** - Communication between agents

## Key Features

### Human-in-the-Loop

The system includes several endpoints for human interaction:
- `/api/human_feedback` - Approve/reject steps
- `/api/human_clarification_on_plan` - Modify plans
- `/api/approve_step_or_steps` - Bulk approvals

### Security

- Azure AD authentication via EasyAuth headers
- User isolation (data filtered by user_id)
- Responsible AI (RAI) checks on input

### Monitoring

- Azure Application Insights integration
- Custom event tracking throughout the workflow
- Comprehensive logging with filtered Azure SDK logs

## API Endpoints

### Task Processing

#### `POST /api/input_task`
Receives initial task descriptions from users and initiates the multi-agent workflow:
- Validates requests against Responsible AI (RAI) guidelines
- Creates or uses existing sessions
- Initializes all required agents through the AgentFactory
- Generates execution plans with detailed steps
- Returns plan ID and session information

### Human-in-the-Loop Interactions

#### `POST /api/human_feedback`
Enables users to provide feedback on specific execution steps:
- Accepts approval/rejection of steps
- Allows modification of planned actions
- Updates the execution plan based on feedback

#### `POST /api/human_clarification_on_plan`
Allows users to clarify or modify entire plans:
- Accepts clarification text from users
- Updates plan understanding and execution strategy
- Ensures AI agents align with user intentions

#### `POST /api/approve_step_or_steps`
Manages approval workflow for individual steps or entire plans:
- Supports single step or bulk approval
- Integrates with the group chat manager for coordination
- Ensures human oversight before critical actions

### Data Retrieval

#### `GET /api/plans`
Retrieves plans for the authenticated user:
- Optional filtering by session ID
- Returns complete plan details with step counts
- Includes overall status and progress information

#### `GET /api/steps/{plan_id}`
Fetches detailed steps for a specific plan:
- Returns all steps associated with the plan
- Includes step status, agent assignments, and feedback
- Shows execution results and any modifications

#### `GET /api/agent_messages/{session_id}`
Returns communication history between agents:
- Shows inter-agent coordination messages
- Includes timestamps and message sources
- Useful for debugging and understanding agent decisions

### System Management

#### `DELETE /api/messages`
Clears all stored data:
- Removes plans, sessions, steps, and messages
- Clears agent factory cache
- Useful for testing and reset scenarios

#### `GET /api/messages`
Retrieves all messages across sessions:
- Provides comprehensive view of system activity
- Includes all data types (plans, steps, messages)
- Useful for system-wide analysis

## Technical Stack

### Dependencies

- **FastAPI** - Web framework
- **Semantic Kernel** - AI orchestration framework
- **Azure Services**:
  - Cosmos DB - Data persistence
  - Azure OpenAI - LLM capabilities
  - Azure AI Projects - Agent management
  - Application Insights - Monitoring

### Design Patterns

1. **Factory Pattern** - [`AgentFactory`](../../src/backend/kernel_agents/agent_factory.py) for creating agents
2. **Memory Context Pattern** - [`CosmosMemoryContext`](../../src/backend/context/cosmos_memory_kernel.py) for session management
3. **Tool Registration** - Each agent has specialized tools/functions
4. **Async/Await** - Fully asynchronous architecture

## Agent Orchestration

### Agent Coordination

The system uses a memory store to persist plans, steps, and agent communications across sessions. Each user task gets translated into a plan with multiple steps, where each step can be assigned to different specialized agents. The group chat manager orchestrates these agents, ensuring they work together effectively to accomplish the user's goal.

### Memory Management

- Persistent storage of plans, steps, and communications
- Session-based context maintenance
- Efficient retrieval of historical data

## Error Handling and Monitoring

The controller implements robust error handling:
- HTTP exceptions with appropriate status codes
- Detailed error messages for debugging
- Event tracking for error analysis
- Graceful degradation when optional services unavailable

## Design Philosophy

The overall design follows a microservices-inspired pattern where each agent has specific responsibilities, and the system maintains a clear separation between the orchestration layer (group chat manager), the execution layer (individual agents), and the persistence layer (memory store). This architecture allows for scalable, maintainable AI applications where complex tasks can be broken down and handled by specialized agents while maintaining human oversight and control.

## Usage Example

```python
# 1. Submit a task
POST /api/input_task
{
    "description": "Create a marketing campaign for our new product",
    "session_id": "optional-session-id"
}

# 2. Review the generated plan
GET /api/plans?session_id=<session_id>

# 3. Provide feedback on specific steps
POST /api/human_feedback
{
    "step_id": "step-123",
    "plan_id": "plan-456",
    "session_id": "session-789",
    "approved": true,
    "human_feedback": "Looks good, but increase budget to $5000"
}

# 4. Approve the entire plan
POST /api/approve_step_or_steps
{
    "plan_id": "plan-456",
    "session_id": "session-789",
    "approved": true
}
```

## Improvement Opportunities

1. **Error Handling**: Could benefit from more granular exception types and retry logic
2. **Caching**: Agent instances are cached but could extend to plan/step caching
3. **Testing**: No test files visible in the provided code
4. **API Documentation**: While docstrings exist, OpenAPI/Swagger docs could be enhanced
5. **Rate Limiting**: No visible rate limiting for API endpoints
6. **Health Checks**: Basic middleware exists but could add more comprehensive checks

## Future Enhancements

- Real-time WebSocket support for live agent updates
- Enhanced agent capabilities and specializations
- Advanced plan optimization algorithms
- Distributed execution across multiple nodes
- Enhanced security with role-based access control

## Conclusion

This is a well-structured enterprise-grade solution that effectively implements a multi-agent AI system with proper separation of concerns and Azure integration. The architecture supports complex task processing while maintaining human oversight and control, making it suitable for production environments where reliability and transparency are crucial.