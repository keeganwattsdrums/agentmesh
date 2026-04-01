# AgentMesh — Reddit Launch Post

## r/LocalLLaMA

**Title:** Show HN: AgentMesh — Persistent memory infrastructure for AI agents

**Body:**

I've been building AI agents that forget everything between sessions. Every restart = blank slate.

So I built AgentMesh — memory infrastructure that survives across sessions.

**What it does:**
- Persistent memory for any AI agent
- Semantic search across conversation history
- Context window optimization
- Zero-config deployment

**Live demo:** https://cuddly-bears-punch.loca.lt
**GitHub:** https://github.com/keeganwattsdrums/agentmesh
**Landing page:** https://keeganwattsdrums.github.io/agentmesh/

**The problem:** GitHub Copilot just launched cross-file memory (March 2025). Every major AI tool is adding memory because it's painful when agents forget.

**My solution:** Open infrastructure that any agent can use.

**Tech stack:**
- FastAPI backend
- SQLite + JSON storage
- Semantic similarity search
- Docker-ready

**Try it:**
```bash
pip install agentmesh
export AGENTMESH_API_KEY=your_key
```

**First 10 users get free lifetime access.**

What would you want from agent memory infrastructure?

---

## r/ClaudeAI

**Title:** I built memory infrastructure for Claude agents that actually remembers

**Body:**

Every Claude session starts fresh. Context lost. Preferences forgotten. Workflows reset.

AgentMesh fixes this.

**Features:**
- Cross-session memory
- Preference persistence
- Conversation history search
- Zero setup

**Use case:** Claude Code + AgentMesh = remembers your codebase preferences, previous debugging sessions, code style.

**Demo:** https://keeganwattsdrums.github.io/agentmesh/

**Free for first 10 Claude users.**

What's your biggest pain point with Claude's memory?

