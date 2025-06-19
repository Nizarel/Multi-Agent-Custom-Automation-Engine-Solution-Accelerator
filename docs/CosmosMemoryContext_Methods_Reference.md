# CosmosMemoryContext Methods Reference

## Class: CosmosMemoryContext

### Initialization and Lifecycle Methods

**`__init__(self, config: CosmosMemoryConfig)`**
- Initializes the CosmosMemoryContext with configuration settings
- Sets up instance variables but doesn't establish database connection
- Configures session ID, buffer size, and connection parameters

**`__aenter__(self)`**
- Async context manager entry point
- Automatically initializes the Cosmos DB connection when entering context
- Loads recent messages for the current session into the buffer
- Returns self for use in async with statements

**`__aexit__(self, exc_type, exc_val, exc_tb)`**
- Async context manager exit point
- Performs cleanup operations when exiting the context
- Ensures proper resource disposal and connection cleanup

**`initialize(self)`**
- Establishes connection to Azure Cosmos DB
- Creates CosmosClient using DefaultAzureCredential for authentication
- Sets up database and container clients for subsequent operations
- Handles authentication and connection initialization

**`ensure_initialized(self)`**
- Safety check method to ensure the container is available before operations
- Attempts initialization if not already done
- Raises clear errors if initialization fails
- Prevents operations on uninitialized connections

---

### Message Management Methods

**`add_message(self, role: str, content: str, session_id: str = None)`**
- Adds a new chat message to both the in-memory buffer and persistent storage
- Creates a ChatMessage object with timestamp and session information
- Maintains buffer size limits by removing oldest messages when necessary
- Provides dual storage for fast access and durability

**`get_recent_messages(self, limit: int = None)`**
- Retrieves recent messages from the in-memory buffer
- Returns messages in chronological order (oldest to newest)
- Supports optional limit parameter to control number of messages returned
- Provides fast access to conversation history without database queries

**`_load_recent_messages(self)`**
- Private method to load recent messages from database into buffer during initialization
- Queries Cosmos DB for the most recent messages in the current session
- Populates the in-memory buffer with historical conversation data
- Ensures continuity when resuming conversations

---

### Generic Data Operations (CRUD)

**`add_item(self, item: BaseModel)`**
- Generic method to add any Pydantic model to Cosmos DB
- Handles automatic serialization of datetime fields
- Generates unique IDs and adds metadata (type, session_id)
- Returns the generated document ID

**`get_item(self, item_id: str, item_type: str)`**
- Retrieves a specific item by ID and type from Cosmos DB
- Performs type-safe deserialization back to Pydantic models
- Uses session-based partitioning for efficient queries
- Returns None if item not found

**`update_item(self, item: BaseModel)`**
- Updates an existing item in Cosmos DB
- Handles datetime serialization and metadata updates
- Uses upsert operation to create or update as needed
- Maintains data consistency and type safety

**`delete_item(self, item_id: str)`**
- Removes an item from Cosmos DB by ID
- Uses session-based partitioning for targeted deletion
- Handles cleanup of associated data and relationships
- Provides permanent removal of data

**`query_items(self, item_type: str, filters: Dict = None, limit: int = None, order_by: str = None)`**
- Flexible query method for retrieving multiple items of a specific type
- Supports dynamic filtering with dictionary-based conditions
- Allows ordering and limiting of results
- Returns list of properly typed Pydantic model instances

---

### Semantic Kernel Memory Store Interface

**`get_collections(self)`**
- Returns list of available memory collections in the store
- Implements Semantic Kernel MemoryStoreBase interface requirement
- Queries Cosmos DB for distinct collection names
- Supports memory organization and management

**`create_collection(self, collection_name: str)`**
- Creates a new memory collection in the store
- Implements Semantic Kernel interface for collection management
- Handles collection metadata and initialization
- Supports logical grouping of memory records

**`get_collection(self, collection_name: str)`**
- Retrieves information about a specific memory collection
- Returns collection metadata and statistics
- Supports collection discovery and management operations
- Implements standard Semantic Kernel interface

**`delete_collection(self, collection_name: str)`**
- Removes an entire memory collection and all its records
- Implements Semantic Kernel interface for collection cleanup
- Handles bulk deletion of related memory records
- Provides collection lifecycle management

**`does_collection_exist(self, collection_name: str)`**
- Checks if a specific memory collection exists in the store
- Returns boolean indicating collection presence
- Supports conditional logic and validation operations
- Implements Semantic Kernel interface requirement

---

### Vector Similarity and Memory Operations

**`upsert_memory_record(self, record: MemoryRecord)`**
- Stores or updates a memory record with vector embedding
- Handles conversion of numpy arrays to JSON-serializable lists
- Supports both creation and updating of memory records
- Maintains vector data for similarity search operations

**`get_memory_record(self, collection_name: str, key: str)`**
- Retrieves a specific memory record by collection and key
- Reconstructs numpy arrays from stored JSON data
- Returns properly formatted MemoryRecord objects
- Supports targeted memory retrieval operations

**`remove_memory_record(self, collection_name: str, key: str)`**
- Deletes a specific memory record from the store
- Uses collection and key for precise targeting
- Handles cleanup of vector data and metadata
- Supports memory management and cleanup operations

**`get_nearest_matches(self, collection_name: str, embedding: ndarray, limit: int, min_relevance_score: float)`**
- Performs semantic similarity search using vector embeddings
- Calculates cosine similarity between query embedding and stored vectors
- Returns ranked list of most similar memory records with scores
- Supports configurable result limits and relevance thresholds

**`get_nearest_match(self, collection_name: str, embedding: ndarray, min_relevance_score: float)`**
- Convenience method that returns only the single best match
- Wrapper around get_nearest_matches with limit of 1
- Simplifies common use case of finding best single match
- Returns single MemoryRecord or None if no matches meet threshold

---

### Utility and Helper Methods

**`_serialize_datetime_fields(self, data: dict)`**
- Private utility method for handling datetime serialization
- Converts datetime objects to ISO format strings for JSON storage
- Recursively processes nested dictionaries and lists
- Ensures compatibility with Cosmos DB document storage

**`_deserialize_datetime_fields(self, data: dict, model_class)`**
- Private utility method for reconstructing datetime objects from stored data
- Converts ISO format strings back to datetime objects during retrieval
- Uses model field annotations to identify datetime fields
- Maintains type safety during deserialization process

**`_cosine_similarity(self, vec1: ndarray, vec2: ndarray)`**
- Private method for calculating cosine similarity between two vectors
- Handles edge cases like zero vectors and normalization
- Returns similarity score between -1 and 1
- Core computation for semantic similarity search

**`_build_query_with_filters(self, base_query: str, filters: Dict)`**
- Private helper for constructing SQL queries with dynamic filters
- Safely handles parameter injection and query building
- Supports various filter types and conditions
- Prevents SQL injection while enabling flexible querying

---

### Session and Context Management

**`set_session_id(self, session_id: str)`**
- Changes the current session context for subsequent operations
- Clears the message buffer when switching sessions
- Updates partition key for all future database operations
- Enables dynamic session switching within same context instance

**`get_session_id(self)`**
- Returns the currently active session identifier
- Provides access to current session context
- Supports logging and debugging operations
- Simple getter for session state information

**`clear_session_data(self)`**
- Removes all data associated with the current session
- Clears both in-memory buffer and persistent storage
- Provides complete session reset functionality
- Supports privacy and data management requirements

**`get_session_statistics(self)`**
- Returns statistics about the current session's data
- Includes message count, data size, and activity metrics
- Supports monitoring and analytics requirements
- Provides insights into session usage patterns

---

## Summary

The CosmosMemoryContext class provides **29 public methods** and **4 private utility methods** organized into six main functional areas:

1. **Lifecycle Management** (5 methods) - Initialization, context management, safety checks
2. **Message Operations** (3 methods) - Chat message storage, retrieval, and buffer management  
3. **Generic CRUD** (5 methods) - Universal data operations for any Pydantic model type
4. **Semantic Kernel Interface** (5 methods) - Memory store compatibility and collection management
5. **Vector Operations** (5 methods) - Embedding storage, similarity search, and memory record management
6. **Utilities & Context** (6 methods) - Session management, statistics, and helper functions

This comprehensive API provides both high-level conversational memory management and low-level data operations, enabling flexible integration with various AI frameworks and application patterns.
