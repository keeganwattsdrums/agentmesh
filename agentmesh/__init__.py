"""
AgentMesh Python SDK
The easiest way to add persistent memory and context management to your AI agents.
"""

import requests
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Memory:
    """A single memory entry"""
    id: str
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime

class AgentMeshClient:
    """Main client for interacting with AgentMesh"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize AgentMesh client
        
        Args:
            api_key: Your AgentMesh API key (or set AGENTMESH_API_KEY env var)
            base_url: AgentMesh API URL (defaults to https://api.agentmesh.io)
        """
        self.api_key = api_key or os.getenv("AGENTMESH_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Pass api_key or set AGENTMESH_API_KEY env var")
        
        self.base_url = base_url or os.getenv("AGENTMESH_BASE_URL", "https://api.agentmesh.io")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def remember(
        self,
        agent_id: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        Store a memory for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            content: The memory content to store
            tags: Optional tags for categorization
            metadata: Optional metadata dictionary
            
        Returns:
            Memory object with ID and timestamp
        """
        response = requests.post(
            f"{self.base_url}/memory/remember",
            headers=self.headers,
            json={
                "agent_id": agent_id,
                "content": content,
                "tags": tags or [],
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        data = response.json()
        return Memory(
            id=data["id"],
            content=data["content"],
            tags=data["tags"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
    
    def recall(
        self,
        agent_id: str,
        query: str,
        limit: int = 5,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall memories for an agent based on semantic similarity
        
        Args:
            agent_id: Unique identifier for the agent
            query: Search query (semantic search)
            limit: Maximum number of results
            tags: Filter by specific tags
            
        Returns:
            List of memory objects sorted by relevance
        """
        response = requests.post(
            f"{self.base_url}/memory/recall",
            headers=self.headers,
            json={
                "agent_id": agent_id,
                "query": query,
                "limit": limit,
                "tags": tags
            }
        )
        response.raise_for_status()
        return response.json()["results"]
    
    def get_memories(
        self,
        agent_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory objects
        """
        response = requests.get(
            f"{self.base_url}/memory/agent/{agent_id}?limit={limit}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["memories"]
    
    def optimize_context(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 8000,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize message context to fit within token limit
        
        Intelligently truncates oldest messages first while preserving
        system prompt and most recent context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens allowed (default 8000)
            system_prompt: Optional system prompt to always include
            
        Returns:
            Dictionary with optimized messages, token count, and truncation flag
        """
        response = requests.post(
            f"{self.base_url}/context/optimize",
            headers=self.headers,
            json={
                "messages": messages,
                "max_tokens": max_tokens,
                "system_prompt": system_prompt
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        response = requests.get(
            f"{self.base_url}/usage",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


class Agent:
    """
    High-level agent wrapper with built-in memory and context management
    
    Example:
        ```python
        from agentmesh import Agent
        
        agent = Agent(
            name="customer-support",
            api_key="your-api-key",
            memory=True,
            context_limit=8000
        )
        
        # Store interaction
        agent.remember("User prefers email communication")
        
        # Later, recall relevant info
        memories = agent.recall("how should I contact user?")
        ```
    """
    
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        memory: bool = True,
        context_limit: int = 8000,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize an agent
        
        Args:
            name: Unique name for this agent
            api_key: AgentMesh API key
            memory: Enable persistent memory
            context_limit: Maximum tokens for context window
            system_prompt: Default system prompt
        """
        self.name = name
        self.client = AgentMeshClient(api_key=api_key)
        self.memory_enabled = memory
        self.context_limit = context_limit
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict[str, Any]] = []
    
    def remember(self, content: str, tags: Optional[List[str]] = None) -> Optional[Memory]:
        """Store a memory if memory is enabled"""
        if not self.memory_enabled:
            return None
        return self.client.remember(self.name, content, tags=tags)
    
    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall memories if memory is enabled"""
        if not self.memory_enabled:
            return []
        return self.client.recall(self.name, query, limit=limit)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_context(self) -> Dict[str, Any]:
        """Get optimized context for LLM call"""
        return self.client.optimize_context(
            messages=self.conversation_history,
            max_tokens=self.context_limit,
            system_prompt=self.system_prompt
        )
    
    def clear_history(self):
        """Clear conversation history (memories persist)"""
        self.conversation_history = []


# Convenience function for quick initialization
def init(api_key: Optional[str] = None, base_url: Optional[str] = None) -> AgentMeshClient:
    """
    Quick initialization of AgentMesh client
    
    Example:
        ```python
        import agentmesh
        
        client = agentmesh.init()
        client.remember("my-agent", "Important context...")
        ```
    """
    return AgentMeshClient(api_key=api_key, base_url=base_url)


# Backwards compatibility
Client = AgentMeshClient
