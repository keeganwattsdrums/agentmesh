# Hacker News "Show HN" Post

## Title
Show HN: AgentMesh – Persistent memory infrastructure for AI agents

## URL
https://keeganwattsdrums.github.io/agentmesh/

## Post Body

I've been building AI agents and kept running into the same problem: they forget everything when they restart.

Context windows are too small for real workflows. Vector databases are powerful but you still have to build the memory layer yourself. I wanted something that just worked.

So I built AgentMesh: persistent memory infrastructure for AI agents in one line of code.

**What it does:**
- Store agent context that survives restarts
- Semantic search through memory with natural language
- Automatic context window optimization
- Zero configuration, scales when you need it

**Tech stack:**
- Python (FastAPI backend)
- ChromaDB for vector storage
- Sentence-transformers for embeddings
- Async-first SDK

**Code example:**
```python
from agentmesh import Agent

agent = Agent(api_key="your_key")

# Store context
agent.remember("User prefers Python over JavaScript")

# Recall with semantic search
memories = agent.recall("what programming language?")
# Returns: ["User prefers Python over JavaScript"]
```

**GitHub:** https://github.com/keeganwattsdrums/agentmesh

**Live demo:** https://cuddly-bears-punch.loca.lt/docs

I'm offering free lifetime Pro access to the first 100 founding members (currently 99 spots left). If you're building AI agents and want to shape the roadmap, check it out.

Would love feedback from the HN community. What would you want from agent memory infrastructure?

🦞

---

## Response Templates

### If someone asks about competition vs Pinecone:
> Pinecone is a great vector DB but you still build the memory layer. AgentMesh is complete infrastructure with context optimization, semantic APIs, and agent-specific workflows.

### If someone asks about pricing:
> Starter: $19/month (1,000 agents), Pro: $99/month (10,000 agents). First 100 founding members get lifetime free Pro access.

### If someone asks about self-hosting:
> Core is open source (GitHub). You can self-host or use our managed cloud. Planning enterprise self-hosted option.

### If someone points out it's just a wrapper:
> Fair point. The value is in the agent-specific abstractions. We handle context window management, relevance scoring, and memory lifecycle so you don't have to.

### If someone is critical:
> Thanks for the feedback! What would make this more useful for your use case?

---

## Launch Strategy

**Best time to post:** Tuesday-Thursday, 8-10 AM PST

**Engagement rules:**
- Respond to every comment within 15 minutes
- Be genuinely helpful, not promotional
- Acknowledge valid criticism
- Don't argue with trolls

**Success metrics:**
- Target: Front page (100+ upvotes)
- Target: 50+ comments
- Target: 10+ founding member signups
- Target: 2,000+ website visits

---

## Follow-up Comment (after 2 hours)

Wow, thanks for all the feedback! A few common questions:

**Q: How is this different from just using ChromaDB directly?**
A: You're right that we use ChromaDB under the hood. The value is in the agent-specific abstractions — context window optimization, relevance scoring, memory lifecycle management. You *can* build this yourself, but our users prefer to focus on their agent logic.

**Q: What's the pricing?**
A: Starter: $19/month (1,000 agents), Pro: $99/month (10,000 agents). First 100 founding members get lifetime free Pro access.

**Q: Can I self-host?**
A: Yes! Core is open source. We're adding enterprise self-hosted option soon.

**Current status:** 1 founding member claimed, 99 spots remaining.

Would love to hear from anyone building agents — what memory challenges are you facing?
