# Cosmos DB Container Schema for CosmosMemoryContext

## Container Overview

The CosmosMemoryContext uses a **single container** approach with a **multi-document type schema**. All different data types (ChatMessage, Plan, PlanStep, MemoryRecord) are stored in the same container, differentiated by a `type` field.

### Container Configuration

```json
{
  "container_name": "memory_store",
  "partition_key": "/session_id",
  "indexing_policy": {
    "automatic": true,
    "indexing_mode": "consistent"
  }
}
```

---

## Document Schema Structure

### Base Document Schema

Every document in the container follows this base structure:

```json
{
  "id": "unique-document-identifier",
  "session_id": "session-partition-key", 
  "type": "document-type-identifier",
  "_ts": 1718798400,
  "_etag": "\"0000d986-0000-0700-0000-667890a00000\"",
  "_rid": "VhYwAOKs6gw=",
  "_self": "dbs/VhYwAA==/colls/VhYwAOKs6gw=/docs/VhYwAOKs6gw=/",
  "ts": "2025-06-19T10:30:00.000Z"
}
```

**Base Field Descriptions:**
- `id` - Unique identifier (UUID4 format)
- `session_id` - Partition key for data isolation and performance
- `type` - Document type discriminator ("chatmessage", "plan", "planstep", "memoryrecord")
- `_ts` - Cosmos DB internal timestamp (Unix epoch)
- `_etag` - Entity tag for optimistic concurrency control
- `_rid` - Resource identifier (Cosmos DB internal)
- `_self` - Resource self-link (Cosmos DB internal)
- `ts` - Application-level timestamp (ISO 8601 format)

---

## Document Type Schemas

### 1. ChatMessage Documents

**Type Identifier**: `"chatmessage"`

```json
{
  "id": "msg_550e8400-e29b-41d4-a716-446655440000",
  "session_id": "session_user123_20250619_001",
  "type": "chatmessage",
  "role": "user|assistant|system",
  "content": "The actual message content text",
  "timestamp": "2025-06-19T10:30:00.000Z",
  "metadata": {
    "user_id": "user123",
    "source": "web_chat",
    "language": "en"
  },
  "_ts": 1718798400,
  "_etag": "\"0000d986-0000-0700-0000-667890a00000\"",
  "ts": "2025-06-19T10:30:00.000Z"
}
```

**ChatMessage-Specific Fields:**
- `role` - Message sender role (user/assistant/system)
- `content` - The actual message text
- `timestamp` - When the message was created
- `metadata` - Optional additional information about the message

### 2. Plan Documents

**Type Identifier**: `"plan"`

```json
{
  "id": "plan_660e8400-e29b-41d4-a716-446655440001",
  "session_id": "session_user123_20250619_001",
  "type": "plan",
  "goal": "Complete user's task request",
  "description": "Detailed plan description",
  "status": "active|completed|failed|cancelled",
  "created_at": "2025-06-19T10:30:00.000Z",
  "updated_at": "2025-06-19T10:35:00.000Z",
  "parameters": {
    "max_steps": 10,
    "timeout_minutes": 30,
    "priority": "high"
  },
  "steps": [
    "step_id_1",
    "step_id_2",
    "step_id_3"
  ],
  "_ts": 1718798400,
  "_etag": "\"0000d986-0000-0700-0000-667890a00001\"",
  "ts": "2025-06-19T10:30:00.000Z"
}
```

**Plan-Specific Fields:**
- `goal` - High-level objective of the plan
- `description` - Detailed plan description
- `status` - Current execution status
- `created_at` - Plan creation timestamp
- `updated_at` - Last modification timestamp
- `parameters` - Configuration parameters for plan execution
- `steps` - Array of step IDs associated with this plan

### 3. PlanStep Documents

**Type Identifier**: `"planstep"`

```json
{
  "id": "step_770e8400-e29b-41d4-a716-446655440002",
  "session_id": "session_user123_20250619_001",
  "type": "planstep",
  "plan_id": "plan_660e8400-e29b-41d4-a716-446655440001",
  "step_number": 1,
  "description": "Execute the first step of the plan",
  "status": "pending|running|completed|failed|skipped",
  "skill_name": "data_processor",
  "function_name": "process_data",
  "parameters": {
    "input_file": "data.csv",
    "output_format": "json",
    "validation_rules": ["not_null", "unique_id"]
  },
  "result": {
    "success": true,
    "output": "Processed 1000 records successfully",
    "execution_time_ms": 2500
  },
  "created_at": "2025-06-19T10:30:00.000Z",
  "started_at": "2025-06-19T10:30:05.000Z",
  "completed_at": "2025-06-19T10:30:08.000Z",
  "_ts": 1718798400,
  "_etag": "\"0000d986-0000-0700-0000-667890a00002\"",
  "ts": "2025-06-19T10:30:00.000Z"
}
```

**PlanStep-Specific Fields:**
- `plan_id` - Reference to parent plan
- `step_number` - Execution order within the plan
- `description` - What this step accomplishes
- `status` - Current execution state
- `skill_name` - Semantic Kernel skill to execute
- `function_name` - Specific function within the skill
- `parameters` - Input parameters for step execution
- `result` - Execution results and output data
- `created_at` - Step creation timestamp
- `started_at` - Execution start time
- `completed_at` - Execution completion time

### 4. MemoryRecord Documents

**Type Identifier**: `"memoryrecord"`

```json
{
  "id": "mem_880e8400-e29b-41d4-a716-446655440003",
  "session_id": "session_user123_20250619_001",
  "type": "memoryrecord",
  "key": "conversation_context_001",
  "text": "User asked about weather forecast for next week",
  "description": "Weather inquiry context for semantic search",
  "external_source_name": "weather_service",
  "is_reference": false,
  "additional_metadata": "location=Seattle,timeframe=7days",
  "embedding": [
    0.1234, -0.5678, 0.9012, -0.3456, 0.7890,
    -0.2345, 0.6789, -0.1234, 0.4567, -0.8901
  ],
  "collection": "conversation_memories",
  "timestamp": "2025-06-19T10:30:00.000Z",
  "_ts": 1718798400,
  "_etag": "\"0000d986-0000-0700-0000-667890a00003\"",
  "ts": "2025-06-19T10:30:00.000Z"
}
```

**MemoryRecord-Specific Fields:**
- `key` - Unique identifier within the collection
- `text` - The actual text content for semantic search
- `description` - Human-readable description of the memory
- `external_source_name` - Source system or service name
- `is_reference` - Boolean indicating if this is a reference or primary content
- `additional_metadata` - Free-form metadata string
- `embedding` - Vector embedding array (typically 1536 dimensions for OpenAI)
- `collection` - Logical grouping for memory records
- `timestamp` - When the memory was created

---

## Partitioning Strategy

### Partition Key: `/session_id`

**Partition Key Format Examples:**
```
session_user123_20250619_001
session_agent456_20250619_002  
session_bot789_20250619_003
```

**Partition Distribution:**
```
Partition: session_user123_20250619_001
├── ChatMessage: 245 documents
├── Plan: 12 documents  
├── PlanStep: 89 documents
└── MemoryRecord: 156 documents

Partition: session_user456_20250619_002
├── ChatMessage: 89 documents
├── Plan: 3 documents
├── PlanStep: 18 documents
└── MemoryRecord: 45 documents
```

### Query Efficiency by Partition

| Query Pattern | Efficiency | Example |
|---------------|------------|---------|
| Single Session | ✅ Optimal | `WHERE session_id = 'session_123'` |
| Session + Type | ✅ Optimal | `WHERE session_id = 'session_123' AND type = 'chatmessage'` |
| Cross-Session Type | ⚠️ Cross-Partition | `WHERE type = 'plan'` |
| Content Search | ❌ Full Scan | `WHERE content CONTAINS 'weather'` |

---

## Indexing Strategy

### Default Indexing Policy

```json
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    {
      "path": "/*"
    }
  ],
  "excludedPaths": [
    {
      "path": "/embedding/*"
    },
    {
      "path": "/_etag/?"
    }
  ]
}
```

### Recommended Custom Indexes

```json
{
  "compositeIndexes": [
    [
      {"path": "/session_id", "order": "ascending"},
      {"path": "/type", "order": "ascending"},
      {"path": "/timestamp", "order": "descending"}
    ],
    [
      {"path": "/session_id", "order": "ascending"},
      {"path": "/plan_id", "order": "ascending"},
      {"path": "/step_number", "order": "ascending"}
    ]
  ],
  "spatialIndexes": [],
  "vectorIndexes": []
}
```

---

## Data Size Considerations

### Document Size Examples

| Document Type | Typical Size | Maximum Size | Notes |
|---------------|-------------|--------------|-------|
| ChatMessage | 1-5 KB | 50 KB | Depends on message length |
| Plan | 2-10 KB | 100 KB | Includes parameters and metadata |
| PlanStep | 1-8 KB | 80 KB | Includes execution results |
| MemoryRecord | 10-50 KB | 200 KB | Large due to embedding vectors |

### Partition Size Management

**Target Metrics:**
- **Logical Partition Size**: < 10 GB (Cosmos DB limit: 20 GB)
- **Documents per Partition**: 100K - 500K documents
- **Hot Partition Prevention**: Monitor RU consumption per partition
- **Session Rotation**: Encourage new sessions for long conversations

---

## Schema Evolution Strategy

### Version Management

```json
{
  "id": "doc_id",
  "session_id": "session_123",
  "type": "chatmessage",
  "schema_version": "1.0",
  "content": "message content",
  "timestamp": "2025-06-19T10:30:00.000Z"
}
```

### Backward Compatibility

- **Additive Changes**: New fields can be added without breaking existing code
- **Field Deprecation**: Old fields maintained during transition periods
- **Type Evolution**: Document types can evolve with proper version handling
- **Migration Strategy**: In-place document updates for schema changes

---

## Container Security and Access Patterns

### Access Control

```json
{
  "resource_tokens": {
    "read_permissions": ["session_user123_*"],
    "write_permissions": ["session_user123_*"],
    "admin_permissions": ["*"]
  }
}
```

### Query Patterns by Role

**User Queries (Session-Scoped):**
```sql
-- Get recent messages
SELECT * FROM c 
WHERE c.session_id = 'session_123' 
  AND c.type = 'chatmessage' 
ORDER BY c.timestamp DESC

-- Get active plans
SELECT * FROM c 
WHERE c.session_id = 'session_123' 
  AND c.type = 'plan' 
  AND c.status = 'active'
```

**Admin Queries (Cross-Session):**
```sql
-- Get all failed plans
SELECT * FROM c 
WHERE c.type = 'plan' 
  AND c.status = 'failed'

-- Memory usage statistics
SELECT c.type, COUNT(1) as count, AVG(LENGTH(ToString(c))) as avg_size
FROM c 
GROUP BY c.type
```

This schema design provides a flexible, scalable foundation for the multi-agent automation engine while maintaining optimal performance through proper partitioning and indexing strategies.
