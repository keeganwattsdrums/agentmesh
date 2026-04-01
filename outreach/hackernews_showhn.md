# AgentMesh — Hacker News "Show HN" Post

**Title:** Show HN: AgentMesh – Memory infrastructure for AI agents

**Body:**

Hi HN,

I've been frustrated that every AI agent I build forgets everything when I restart it. Context lost. User preferences gone. Conversation history evaporated.

So I built AgentMesh — persistent memory infrastructure for AI agents.

**GitHub:** https://github.com/keeganwattsdrums/agentmesh
**Live API:** https://cuddly-bears-punch.loca.lt
**Landing page:** https://keeganwattsdrums.github.io/agentmesh/

**What it does:**
- Stores agent memory across sessions
- Semantic search through conversation history
- Context window optimization (prunes old memories intelligently)
- Zero-config deployment (Docker-ready)

**Why now:** GitHub Copilot just announced cross-file memory. OpenAI is investing heavily in agent memory. The infrastructure layer is forming.

**Tech details:**
- FastAPI backend
- SQLite + JSON storage (extensible to Postgres)
- Cosine similarity for semantic search
- Python SDK with async support

**Try it:**
```bash
pip install agentmesh
export AGENTMESH_API_KEY=your_key

from agentmesh import AgentMeshClient

client = AgentMeshClient()
client.remember("user_123", "prefers_python", True)
```

**Pricing:**
- Free tier: 1,000 API calls/month
- Pro: $47/month (unlimited calls)
- First 10 HN users get lifetime Pro free

**The ask:**
I'm building this in public. What would make this indispensable for your AI agents?

Thanks!

