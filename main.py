from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import hashlib
import json
from datetime import datetime

app = FastAPI(title="AgentMesh API", version="1.0.0")
security = HTTPBearer()

# In-memory storage for MVP (will use ChromaDB in production)
memory_store = {}

# Models
class MemoryRequest(BaseModel):
    agent_id: str
    content: str
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class MemoryResponse(BaseModel):
    id: str
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: str

class RecallRequest(BaseModel):
    agent_id: str
    query: str
    limit: int = 5
    tags: Optional[List[str]] = None

class ContextRequest(BaseModel):
    messages: List[Dict[str, Any]]
    max_tokens: int = 8000
    system_prompt: Optional[str] = None

class ContextResponse(BaseModel):
    messages: List[Dict[str, Any]]
    token_count: int
    truncated: bool

# Auth - simplified for MVP
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    token = credentials.credentials
    # For MVP, accept any token that looks valid (starts with 'am_')
    # In production, verify against database
    if not token.startswith('am_'):
        raise HTTPException(status_code=401, detail="Invalid token format")
    return token

# Simple semantic search (keyword-based for MVP)
def simple_semantic_search(query: str, documents: List[Dict]) -> List[Dict]:
    """Simple keyword matching for MVP - replace with embeddings in production"""
    query_words = set(query.lower().split())
    scored = []
    
    for doc in documents:
        content_words = set(doc.get('content', '').lower().split())
        tag_words = set(' '.join(doc.get('tags', [])).lower().split())
        
        score = len(query_words & content_words) + len(query_words & tag_words) * 2
        if score > 0:
            scored.append((score, doc))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored]

# Memory Endpoints
@app.post("/memory/remember", response_model=MemoryResponse)
async def remember(request: MemoryRequest, token: str = Depends(verify_token)):
    """Store a memory for an agent"""
    try:
        agent_id = request.agent_id
        
        if agent_id not in memory_store:
            memory_store[agent_id] = []
        
        # Generate ID
        memory_id = hashlib.md5(
            f"{agent_id}:{request.content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        memory = {
            "id": memory_id,
            "content": request.content,
            "tags": request.tags or [],
            "metadata": request.metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        memory_store[agent_id].append(memory)
        
        return MemoryResponse(**memory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/recall")
async def recall(request: RecallRequest, token: str = Depends(verify_token)):
    """Recall memories for an agent"""
    try:
        agent_id = request.agent_id
        
        if agent_id not in memory_store or not memory_store[agent_id]:
            return {"results": []}
        
        memories = memory_store[agent_id]
        
        # Filter by tags if specified
        if request.tags:
            memories = [m for m in memories if any(tag in m.get('tags', []) for tag in request.tags)]
        
        # Semantic search
        results = simple_semantic_search(request.query, memories)
        
        # Limit results
        results = results[:request.limit]
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/agent/{agent_id}")
async def get_agent_memories(agent_id: str, limit: int = 10, token: str = Depends(verify_token)):
    """Get all memories for an agent"""
    try:
        if agent_id not in memory_store:
            return {"memories": []}
        
        memories = memory_store[agent_id][-limit:]
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Context Management Endpoints
@app.post("/context/optimize", response_model=ContextResponse)
async def optimize_context(request: ContextRequest, token: str = Depends(verify_token)):
    """Optimize context window to fit within token limit"""
    try:
        # Simple token estimation (rough approximation)
        def estimate_tokens(text):
            if not text:
                return 0
            return int(len(text.split()) * 1.3)  # Rough estimate
        
        # Calculate current token count
        total_tokens = 0
        if request.system_prompt:
            total_tokens += estimate_tokens(request.system_prompt)
        
        for msg in request.messages:
            content = msg.get('content', '')
            if isinstance(content, str):
                total_tokens += estimate_tokens(content)
        
        # If under limit, return as-is
        if total_tokens <= request.max_tokens:
            return ContextResponse(
                messages=request.messages,
                token_count=total_tokens,
                truncated=False
            )
        
        # Need to truncate - remove oldest messages first
        truncated_messages = []
        current_tokens = estimate_tokens(request.system_prompt) if request.system_prompt else 0
        
        # Add system prompt first if exists
        if request.system_prompt:
            truncated_messages.append({"role": "system", "content": request.system_prompt})
        
        # Add messages from newest to oldest until we hit limit
        for msg in reversed(request.messages):
            msg_tokens = estimate_tokens(msg.get('content', ''))
            if current_tokens + msg_tokens <= request.max_tokens:
                truncated_messages.insert(1 if request.system_prompt else 0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return ContextResponse(
            messages=truncated_messages,
            token_count=current_tokens,
            truncated=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Key generation endpoint (for testing)
@app.get("/key/generate")
async def generate_key():
    """Generate a test API key"""
    key = f"am_{hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:24]}"
    return {"api_key": key, "note": "This is a test key. In production, keys will be tied to accounts."}

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0", "agents": len(memory_store)}

# Usage tracking (simplified for MVP)
@app.get("/usage")
async def get_usage(token: str = Depends(verify_token)):
    """Get current usage stats"""
    return {
        "operations_this_month": 0,
        "plan": "free",
        "limit": 1000
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
