# AgentMesh

**The Infrastructure Platform for AI Agents**

Stop rebuilding the same infrastructure. AgentMesh provides cross-session memory, intelligent context management, and visual workflow orchestration for AI agents.

## The Problem

Building production AI agents means solving the same problems over and over:
- Agents forget everything between sessions
- Context windows overflow and crash
- Multi-agent coordination is a nightmare
- No standard infrastructure exists

## The Solution

```python
from agentmesh import Agent

# One line to add persistent memory and context management
agent = Agent(
    name="my-assistant",
    api_key="your-key",
    memory=True,  # ✅ Remembers across sessions
    context_limit=8000  # ✅ Never overflows
)

# Store memories
agent.remember("User prefers dark mode", tags=["preference"])

# Recall relevant context
memories = agent.recall("what are the user's preferences?")
```

## Quick Start

```bash
pip install agentmesh
```

```python
import agentmesh

# Initialize
client = agentmesh.init(api_key="your-api-key")

# Store a memory
memory = client.remember(
    agent_id="support-bot",
    content="Customer is on the Enterprise plan",
    tags=["billing", "plan"]
)

# Recall semantically
results = client.recall(
    agent_id="support-bot",
    query="what plan is the customer on?",
    limit=3
)
```

## Features

### Persistent Memory
- Cross-session memory for agents
- Semantic search with embeddings
- Tag-based organization
- Metadata support

### Context Management
- Automatic token counting
- Intelligent truncation
- Preserves recent context
- Never exceeds limits

### Python SDK
- Simple, familiar API
- Zero-config setup
- Async support
- Type hints

## Pricing

| Plan | Price | Operations | Agents |
|------|-------|------------|--------|
| **Starter** | Free | 1,000/mo | 1 |
| **Pro** | $99/mo | 100,000/mo | 10 |
| **Business** | $299/mo | 1,000,000/mo | Unlimited |
| **Enterprise** | $999/mo | Unlimited | Unlimited |

## Documentation

Full documentation at [docs.agentmesh.io](https://docs.agentmesh.io)

## License

MIT License - see LICENSE file
