from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import chromadb
import hashlib
import jwt
from datetime import datetime, timedelta
import os

app = FastAPI(title="AgentMesh API", version="1.0.0")
security = HTTPBearer()

# Initialize ChromaDB
chroma_client = chromadb.Client()

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
    created_at: datetime

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

# Auth
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        # For MVP, accept any valid-looking token
        # In production, verify against database
        return credentials.credentials
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Memory Endpoints
@app.post("/memory/remember", response_model=MemoryResponse)
async def remember(
    request: MemoryRequest,
    token: str = Depends(verify_token)
):
    """Store a memory for an agent"""
    try:
        # Get or create collection for this agent
        collection_name = f"agent_{request.agent_id}"
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            collection = chroma_client.create_collection(collection_name)
        
        # Generate ID
        memory_id = hashlib.md5(
            f"{request.agent_id}:{request.content}:{datetime.now()}".encode()
        ).hexdigest()
        
        # Store in ChromaDB
        collection.add(
            documents=[request.content],
            ids=[memory_id],
            metadatas=[{
                "tags": request.tags,
                **request.metadata,
                "created_at": datetime.now().isoformat()
            }]
        )
        
        return MemoryResponse(
            id=memory_id,
            content=request.content,
            tags=request.tags,
            metadata=request.metadata,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/recall")
async def recall(
    request: RecallRequest,
    token: str = Depends(verify_token)
):
    """Recall memories for an agent"""
    try:
        collection_name = f"agent_{request.agent_id}"
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            return {"results": []}
        
        # Query ChromaDB
        results = collection.query(
            query_texts=[request.query],
            n_results=request.limit
        )
        
        # Format results
        memories = []
        for i, doc in enumerate(results['documents'][0]):
            memories.append({
                "id": results['ids'][0][i],
                "content": doc,
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "distance": results['distances'][0][i] if results['distances'] else 0
            })
        
        return {"results": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/agent/{agent_id}")
async def get_agent_memories(
    agent_id: str,
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """Get all memories for an agent"""
    try:
        collection_name = f"agent_{agent_id}"
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            return {"memories": []}
        
        results = collection.get(limit=limit)
        
        memories = []
        for i, doc in enumerate(results['documents']):
            memories.append({
                "id": results['ids'][i],
                "content": doc,
                "metadata": results['metadatas'][i] if results['metadatas'] else {}
            })
        
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Context Management Endpoints
@app.post("/context/optimize", response_model=ContextResponse)
async def optimize_context(
    request: ContextRequest,
    token: str = Depends(verify_token)
):
    """Optimize context window to fit within token limit"""
    try:
        # Simple token estimation (rough approximation)
        def estimate_tokens(text):
            return len(text.split()) * 1.3  # Rough estimate
        
        # Calculate current token count
        total_tokens = 0
        if request.system_prompt:
            total_tokens += estimate_tokens(request.system_prompt)
        
        for msg in request.messages:
            total_tokens += estimate_tokens(msg.get('content', ''))
        
        # If under limit, return as-is
        if total_tokens <= request.max_tokens:
            return ContextResponse(
                messages=request.messages,
                token_count=int(total_tokens),
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
            token_count=int(current_tokens),
            truncated=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# Usage tracking (simplified for MVP)
@app.get("/usage")
async def get_usage(token: str = Depends(verify_token)):
    """Get current usage stats"""
    # In production, query database
    return {
        "operations_this_month": 0,
        "plan": "free",
        "limit": 1000
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
