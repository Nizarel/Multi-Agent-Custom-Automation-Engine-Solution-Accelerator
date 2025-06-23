# Multi-Agent Controller System

## Overview

This document describes the Multi-Agent Custom Automation Engine's controller system, implemented in `app_kernel.py`. The controller serves as the central orchestration point for an AI-powered multi-agent system that processes user tasks through collaborative AI agents.

## Architecture Overview

The controller is built using FastAPI and integrates with Azure services for monitoring and AI capabilities. It implements a sophisticated multi-agent orchestration platform where different AI agents collaborate to complete tasks based on user input.

### Key Components

1. **FastAPI Application**: Core web service framework
2. **Semantic Kernel**: Framework for building AI applications
3. **Agent Factory**: Creates and manages different types of AI agents
4. **Memory Store**: Persists plans, steps, and agent communications
5. **Azure Integration**: Application Insights for monitoring and AI Project Client for AI services

## Core Endpoints

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

## Security Features

### Authentication
- All endpoints require user authentication via request headers
- User principal ID extracted and validated before operations
- Session-based isolation ensures data privacy

### Input Validation
- Responsible AI (RAI) checks on all input tasks
- Prevents processing of inappropriate or harmful requests
- Comprehensive error handling and logging

## Agent Orchestration

### Agent Types
The system supports multiple agent types coordinated by a Group Chat Manager:
- **Planner Agent**: Creates execution plans from user tasks
- **Execution Agents**: Specialized agents for different task types
- **Human Agent**: Handles human feedback and clarifications
- **Group Chat Manager**: Coordinates all agents and maintains workflow

### Memory Management
- Persistent storage of plans, steps, and communications
- Session-based context maintenance
- Efficient retrieval of historical data

## Monitoring and Observability

### Application Insights Integration
- Automatic configuration when connection string is provided
- Custom event tracking for important operations
- Error tracking and performance monitoring

### Logging
- Comprehensive logging at INFO level
- Suppressed verbose logs from Azure SDK components
- Custom event tracking for business-critical operations

## Error Handling

The controller implements robust error handling:
- HTTP exceptions with appropriate status codes
- Detailed error messages for debugging
- Event tracking for error analysis
- Graceful degradation when optional services unavailable

## Design Principles

1. **Separation of Concerns**: Clear boundaries between orchestration, execution, and persistence
2. **Human Oversight**: Multiple touchpoints for human intervention and control
3. **Scalability**: Microservices-inspired architecture for handling complex workflows
4. **Maintainability**: Modular design with specialized agents for specific tasks
5. **Security First**: Authentication and authorization at every endpoint

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

## Future Enhancements

- Real-time WebSocket support for live agent updates
- Enhanced agent capabilities and specializations
- Advanced plan optimization algorithms
- Distributed execution across multiple nodes
- Enhanced security with role-based access