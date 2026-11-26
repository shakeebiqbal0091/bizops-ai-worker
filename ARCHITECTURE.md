# Architecture — BizOps AI Worker

## 1. Architecture Overview

BizOps AI Worker will use a modular, multi-agent architecture designed to support autonomous business operations.

The system will combine:

- A central Director Agent.
- Specialized AI Workers.
- Persistent memory.
- Scheduled and event-driven execution.
- External tools and API integrations.
- Human approval and permission controls.
- Execution monitoring and audit history.

The architecture will separate business logic, AI orchestration, data storage, external integrations, and user interfaces.

This separation will make the system easier to test, maintain, extend, and integrate with other business applications.

**Architecture Status:** Proposed architecture for initial development.

## 2. Architectural Principles

The system will follow these principles:

1. **Modularity:** Each component should have a clearly defined responsibility.
2. **Separation of Concerns:** AI reasoning, business logic, data access, and external integrations should remain separate.
3. **Controlled Autonomy:** Workers can only execute actions permitted by application-level authorization.
4. **Persistent Memory:** Important business context must survive application restarts and separate executions.
5. **Reliability:** Workflows must support validation, error handling, retries, and execution tracking.
6. **Traceability:** Important decisions and actions must be recorded.
7. **Incremental Development:** Components will be implemented and tested independently.

## 3. High-Level System Architecture

The planned system will contain the following layers.

### 3.1 User Interface Layer

Provides the interface through which business owners interact with BizOps AI Worker.

Responsibilities:

- Display business operations.
- Show worker activities.
- Display operational reports.
- Present approval requests.
- Allow users to provide instructions.
- Show execution history.

**Technology:** Next.js (planned for a later development stage).

### 3.2 API Layer

Provides communication between the user interface, AI orchestration system, and other application components.

Responsibilities:

- Receive user requests.
- Validate incoming data.
- Handle authentication and authorization.
- Expose business operation endpoints.
- Return execution results.
- Manage approval requests.

**Technology:** FastAPI and Pydantic.

### 3.3 AI Orchestration Layer

Coordinates the Director Agent and specialized AI Workers.

Responsibilities:

- Understand operational requests.
- Determine which worker should handle a task.
- Delegate tasks.
- Coordinate multi-step workflows.
- Maintain workflow state.
- Handle failures and escalation.
- Return structured results.

**Technology:** LangGraph.

### 3.4 Memory Layer

Provides persistent storage and retrieval of business context.

Responsibilities:

- Store business information.
- Retrieve relevant memories.
- Maintain operational history.
- Store previous decisions and outcomes.
- Support semantic retrieval.
- Preserve important context across executions.

**Technology:** PostgreSQL and pgvector.

### 3.5 Scheduling Layer

Activates recurring business workflows without requiring daily user instructions.

Responsibilities:

- Schedule recurring tasks.
- Trigger monitoring workflows.
- Start daily and weekly reports.
- Track scheduled execution.
- Handle execution failures.

**Technology:** APScheduler for the initial version.

### 3.6 Tool and Integration Layer

Connects AI Workers to external business applications.

Responsibilities:

- Retrieve order information.
- Retrieve inventory information.
- Access approved business operations.
- Prepare customer notifications.
- Validate tool inputs.
- Enforce permissions before executing actions.

**Technologies:** Python API clients and MCP integrations.

### 3.7 Approval and Security Layer

Controls what the AI Worker is allowed to do.

Responsibilities:

- Check permissions.
- Identify actions requiring approval.
- Create approval requests.
- Validate approval decisions.
- Prevent unauthorized actions.
- Record important security events.

Permission enforcement must happen in application code, not only through AI prompts.

## 4. Multi-Agent Architecture

BizOps AI Worker will use a central Director Agent to coordinate specialized workers.

### 4.1 Director Agent

The Director Agent is responsible for overall workflow coordination.

Responsibilities:

- Receive tasks and operational events.
- Understand business context.
- Retrieve relevant memory.
- Determine the appropriate worker.
- Delegate responsibilities.
- Coordinate worker results.
- Handle exceptions.
- Request human approval when required.
- Produce a final operational result.

The Director Agent should coordinate work rather than independently perform every specialized responsibility.

### 4.2 Order Worker

Responsible for order operations.

Responsibilities:

- Retrieve order information.
- Identify pending orders.
- Detect delayed or problematic orders.
- Analyze order status.
- Prepare order-related reports.
- Identify situations requiring human attention.

### 4.3 Inventory Worker

Responsible for inventory operations.

Responsibilities:

- Retrieve product stock information.
- Monitor stock levels.
- Identify low-stock products.
- Analyze historical stock movement.
- Recommend restocking.
- Prepare inventory alerts.

### 4.4 Customer Worker

Responsible for customer communication workflows.

Responsibilities:

- Identify customers requiring follow-up.
- Prepare customer notifications.
- Draft order-related messages.
- Retrieve relevant customer interaction context.
- Request approval before sending messages when required.

### 4.5 Analytics Worker

Responsible for business performance analysis.

Responsibilities:

- Retrieve sales information.
- Analyze business performance.
- Identify sales trends.
- Generate operational summaries.
- Prepare daily and weekly reports.

### 4.6 Worker Design Rules

Each worker should have:

- A clearly defined responsibility.
- A documented input and output schema.
- Access only to the tools it needs.
- Explicit permission boundaries.
- Defined error-handling behavior.
- Appropriate tests.

Workers should return structured results rather than relying only on unstructured text.

## 5. Workflow Execution

The system will support two primary execution methods.

### 5.1 User-Initiated Execution

A business owner submits a request through the API or dashboard.

Example:

1. The user requests an inventory review.
2. The API validates the request.
3. The Director Agent receives the task.
4. Relevant business memory is retrieved.
5. The Director delegates to the Inventory Worker.
6. The worker retrieves inventory information.
7. The worker analyzes stock levels.
8. The result is returned to the Director.
9. The Director records the result and responds to the user.

### 5.2 Scheduled Execution

The scheduler starts recurring workflows automatically.

Example: Daily inventory monitoring.

1. APScheduler triggers the inventory monitoring workflow.
2. The workflow creates an execution record.
3. The Director Agent receives the scheduled task.
4. Relevant business context is retrieved.
5. The Inventory Worker checks product stock.
6. Low-stock products are identified.
7. Recommendations are generated.
8. Approval is requested if an action requires authorization.
9. The outcome is recorded.

### 5.3 Event-Driven Execution

External systems may generate events that require attention.

Examples:

- A new order is received.
- An order status changes.
- A product's stock level changes.

Events should be validated before they trigger workflows. The system should also protect against duplicate event processing.

## 6. Persistent Memory Architecture

PostgreSQL will be the primary persistent data store.

pgvector will support semantic retrieval of relevant business information.

Memory will be separated into logical categories.

### 6.1 Structured Business Memory

Stores information that should be retrieved using precise queries.

Examples:

- Business profiles.
- Business policies.
- Product information.
- Operational preferences.
- Pending tasks.
- Approval records.

### 6.2 Episodic Memory

Stores important events and experiences.

Examples:

- Previous inventory alerts.
- Completed operational tasks.
- Important order events.
- Previous approval decisions.
- Outcomes of business workflows.

### 6.3 Semantic Memory

Stores information that benefits from meaning-based retrieval.

Examples:

- Business procedures.
- Operational guidelines.
- Relevant historical notes.
- Business-specific knowledge.

Embeddings will be stored and searched using pgvector.

### 6.4 Memory Retrieval Process

1. A worker receives a task.
2. The system identifies the relevant business context.
3. Structured records are retrieved where necessary.
4. Semantic search retrieves relevant stored knowledge.
5. Retrieved information is provided to the worker.
6. The worker completes its task.
7. Important verified outcomes are stored for future use.

### 6.5 Memory Rules

- Do not treat every AI-generated response as a verified fact.
- Preserve the source of important business information.
- Avoid storing unnecessary sensitive information.
- Support updating and correcting business memories.
- Separate information belonging to different businesses.
- Retrieve only information relevant to the current task.

External order and inventory systems remain the source of truth for their respective records. BizOps AI Worker should not silently replace their authoritative data with AI-generated memories.

## 7. Database Architecture

PostgreSQL will store operational data and persistent memory.

The initial logical data model is expected to include:

| Entity | Purpose |
|---|---|
| Businesses | Business profiles and configuration |
| Users | User accounts and access |
| Business Policies | Business rules and operating preferences |
| Tasks | Operational tasks and their status |
| Worker Executions | Worker execution records |
| Workflow Runs | Workflow state and execution history |
| Memories | Persistent business memories |
| Memory Embeddings | Semantic memory vectors |
| Approval Requests | Actions waiting for authorization |
| Audit Logs | Important decisions and system actions |
| Scheduled Jobs | Recurring workflow configuration |

Records should be associated with the appropriate business so that information cannot accidentally cross business boundaries.

The final database schema will be defined during the database implementation stage.

## 8. Tool and MCP Architecture

AI Workers will use controlled tools to interact with external applications.

The tool layer will provide a consistent interface between workers and business systems.

### 8.1 Internal Tools

Examples:

- Get order details.
- List pending orders.
- Get product inventory.
- Identify low-stock products.
- Create an internal task.
- Generate a business report.

### 8.2 External Integrations

Examples:

- E-commerce order systems.
- Inventory management systems.
- WhatsApp messaging services.
- Supplier systems.
- Other business APIs.

### 8.3 MCP Integration

MCP may be used to expose external tools through standardized interfaces.

The system should not depend on MCP for every internal operation. Direct Python services and API clients can handle internal application logic where they are simpler and more appropriate.

### 8.4 Tool Execution Rules

- Validate every tool input.
- Authenticate external requests.
- Enforce permissions before execution.
- Apply timeouts and controlled retries.
- Record important tool executions.
- Handle external API failures safely.
- Treat external content as untrusted data.

## 9. Human Approval Architecture

Actions will be evaluated before execution.

The application will determine whether an action is permitted independently, requires approval, or is restricted.

### Approval Workflow

1. A worker proposes an action.
2. The application checks the action's permission level.
3. If approval is required, an approval request is created.
4. The business owner reviews the request.
5. The owner approves or rejects it.
6. The application validates the decision and executes the authorized action if approved.
7. The result is recorded in the audit history.

Approval should be linked to the exact proposed action and its parameters. Changing the action after approval must require a new authorization.

The application must not allow an AI Worker to bypass the approval process by directly calling an external tool.

## 10. Security and Reliability

Security and reliability must be built into the architecture from the beginning.

### 10.1 Authentication and Authorization

- Protect API endpoints.
- Validate user access to business resources.
- Apply business-level data isolation.
- Enforce tool permissions in application code.
- Store secrets in environment variables or an appropriate secret manager.

### 10.2 Untrusted Content

External messages, customer input, product descriptions, documents, and API responses must be treated as untrusted data.

They must never be allowed to override system instructions, permissions, or application security rules.

### 10.3 Reliability

- Validate inputs and outputs.
- Handle failures at component boundaries.
- Use bounded retries.
- Avoid duplicate execution of consequential operations.
- Record workflow states.
- Support recovery from interrupted workflows.
- Use idempotency controls where appropriate.

### 10.4 Auditability

Important system events should be recorded, including:

- Worker task creation.
- Workflow execution.
- Tool usage.
- Approval requests.
- Approval decisions.
- Completed actions.
- Failed operations.

## 11. Monitoring and Observability

The system should provide visibility into its own operations.

It should track:

- Worker execution status.
- Workflow duration.
- Tool execution results.
- Failed operations.
- Pending approvals.
- Scheduled job status.
- Important system errors.

Logs and execution records should make it possible to understand what happened, when it happened, and why an action was taken.

## 12. Proposed Project Structure

The project will evolve incrementally. The following is the proposed target structure, not a requirement to create every file immediately.

```text
bizops-ai-worker/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── permissions.py
│   │
│   ├── agents/
│   │   ├── director.py
│   │   ├── state.py
│   │   └── workers/
│   │       ├── order_worker.py
│   │       ├── inventory_worker.py
│   │       ├── customer_worker.py
│   │       └── analytics_worker.py
│   │
│   ├── memory/
│   │   ├── service.py
│   │   ├── retrieval.py
│   │   └── storage.py
│   │
│   ├── workflows/
│   │   ├── order_workflow.py
│   │   └── inventory_workflow.py
│   │
│   ├── scheduler/
│   │   └── jobs.py
│   │
│   ├── tools/
│   │   ├── orders.py
│   │   ├── inventory.py
│   │   └── notifications.py
│   │
│   ├── integrations/
│   │   ├── inventory_client.py
│   │   └── whatsapp_client.py
│   │
│   ├── approvals/
│   │   └── service.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   │
│   └── schemas/
│       ├── task.py
│       ├── worker.py
│       └── approval.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── workflows/
│
├── docs/
│
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
├── README.md
├── PRODUCT_VISION.md
└── ARCHITECTURE.md
```

## 13. Development Strategy

Implementation will follow incremental development stages.

### Stage 1 — Project Foundation

- Initialize the Python application.
- Configure FastAPI.
- Configure environment settings.
- Establish the initial project structure.
- Add basic testing infrastructure.

### Stage 2 — Database Foundation

- Configure PostgreSQL.
- Define initial database models.
- Add database migrations.
- Establish business-level data isolation.

### Stage 3 — Persistent Memory

- Implement structured memory storage.
- Implement memory retrieval.
- Integrate pgvector.
- Test memory persistence across application restarts.

### Stage 4 — AI Worker Foundation

- Define worker input and output schemas.
- Implement LangGraph state.
- Create the Director Agent.
- Implement the first specialized worker.
- Test task delegation.

### Stage 5 — Business Tools

- Implement order and inventory integrations.
- Define tool permissions.
- Validate tool execution.
- Test external API failures.

### Stage 6 — Approval and Security

- Implement permission checks.
- Create approval workflows.
- Add audit records.
- Test unauthorized action prevention.

### Stage 7 — Autonomous Scheduling

- Configure APScheduler.
- Implement recurring workflows.
- Track execution status.
- Test recovery and duplicate prevention.

### Stage 8 — Monitoring and Dashboard

- Add execution monitoring.
- Implement business operation endpoints.
- Develop the Next.js dashboard.
- Display worker activity and approvals.

### Stage 9 — Integration and Deployment

- Connect the complete system.
- Run integration tests.
- Review security and reliability.
- Prepare deployment configuration.

Each stage must be tested and verified before moving to the next major stage.

## 14. Architecture Decision Summary

| Decision | Selected Approach | Reason |
|---|---|---|
| Language | Python | Main AI and backend ecosystem |
| Backend | FastAPI | Structured API development |
| Validation | Pydantic | Reliable data validation |
| Orchestration | LangGraph | Stateful workflow coordination |
| Database | PostgreSQL | Persistent relational storage |
| Semantic Memory | pgvector | Meaning-based retrieval |
| Scheduling | APScheduler | Initial recurring execution |
| Tool Integration | Python APIs and MCP | Controlled external integrations |
| Frontend | Next.js | Future management dashboard |

Technology versions and compatibility will be verified during implementation, especially against the project's Python 3.10 requirement.

## 15. Final Architecture Direction

BizOps AI Worker will be built as a modular, stateful, and permission-controlled autonomous operations system.

The Director Agent will coordinate specialized workers, the memory layer will provide continuity, the scheduler will activate recurring workflows, and the tool layer will connect the system to external business applications.

The architecture prioritizes reliability, security, traceability, and incremental development.

The initial implementation will focus on establishing a reliable backend and memory foundation before expanding into multi-agent operations and advanced autonomy.