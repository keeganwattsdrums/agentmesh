#!/usr/bin/env python3
"""
Agent Cost Optimizer - Core Module
Smart caching, model routing, and token optimization
"""

import hashlib
import json
import time
from typing import Optional, Callable, Any, List, Dict
from functools import wraps
from dataclasses import dataclass
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

@dataclass
class CacheEntry:
    key: str
    value: Any
    timestamp: float
    embeddings: Optional[np.ndarray] = None

class SmartCache:
    """Semantic and exact match caching for agent responses"""
    
    def __init__(self, backend: str = "memory", ttl: int = 3600, 
                 similarity_threshold: float = 0.92):
        self.backend = backend
        self.ttl = ttl
        self.similarity_threshold = similarity_threshold
        self._cache: Dict[str, CacheEntry] = {}
        self._embeddings_model = None
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self._embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embeddings model: {e}")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text"""
        if self._embeddings_model is None:
            return None
        return self._embeddings_model.encode(text)
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def _make_key(self, text: str) -> str:
        """Create cache key from text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, query: str, use_semantic: bool = True) -> Optional[Any]:
        """Get cached response for query"""
        # Exact match first
        key = self._make_key(query)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry.timestamp < self.ttl:
                return entry.value
            else:
                del self._cache[key]
        
        # Semantic match
        if use_semantic and self._embeddings_model:
            query_emb = self._get_embedding(query)
            if query_emb is not None:
                best_match = None
                best_score = 0
                
                for entry in self._cache.values():
                    if entry.embeddings is not None:
                        sim = self._compute_similarity(query_emb, entry.embeddings)
                        if sim > self.similarity_threshold and sim > best_score:
                            best_score = sim
                            best_match = entry
                
                if best_match:
                    return best_match.value
        
        return None
    
    def set(self, query: str, value: Any):
        """Cache a response"""
        key = self._make_key(query)
        embeddings = self._get_embedding(query) if self._embeddings_model else None
        
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            embeddings=embeddings
        )
    
    def cached(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """Decorator for caching function results"""
        cache_ttl = ttl or self.ttl
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
                
                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Compute and cache
                result = func(*args, **kwargs)
                self.set(key, result)
                return result
            
            return wrapper
        return decorator
    
    def get_or_compute(self, query: str, compute_func: Callable, 
                       similarity_threshold: Optional[float] = None) -> Any:
        """Get from cache or compute"""
        cached = self.get(query, use_semantic=True)
        if cached is not None:
            return cached
        
        result = compute_func(query)
        self.set(query, result)
        return result


@dataclass
class ModelConfig:
    name: str
    max_complexity: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_latency_ms: float
    quality_score: float  # 0-1 scale

class ModelRouter:
    """Intelligent model routing based on complexity and cost"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.models: List[ModelConfig] = []
        self.default_strategy = "cost_quality_balanced"
        
        # Default model configs
        self.models = [
            ModelConfig("gpt-4o-mini", 0.6, 0.00015, 0.0006, 800, 0.75),
            ModelConfig("claude-3-haiku", 0.5, 0.00025, 0.00125, 700, 0.73),
            ModelConfig("gpt-4o", 1.0, 0.005, 0.015, 1200, 0.95),
            ModelConfig("claude-3-opus", 1.0, 0.015, 0.075, 1500, 0.97),
        ]
    
    def estimate_complexity(self, prompt: str) -> float:
        """Estimate prompt complexity (0-1 scale)"""
        # Simple heuristic-based complexity estimation
        factors = []
        
        # Length factor
        length_factor = min(len(prompt) / 2000, 1.0)
        factors.append(length_factor)
        
        # Question complexity
        question_words = ["why", "how", "explain", "analyze", "compare", "evaluate"]
        question_factor = sum(1 for w in question_words if w in prompt.lower()) / len(question_words)
        factors.append(question_factor)
        
        # Code/complex content indicators
        code_indicators = ["function", "class", "algorithm", "implement", "code"]
        code_factor = sum(1 for w in code_indicators if w in prompt.lower()) / len(code_indicators)
        factors.append(code_factor)
        
        return sum(factors) / len(factors)
    
    def select_model(self, prompt: str, min_quality: float = 0.7, 
                     max_cost: Optional[float] = None) -> ModelConfig:
        """Select best model for prompt"""
        complexity = self.estimate_complexity(prompt)
        
        # Filter by quality requirement
        candidates = [m for m in self.models if m.quality_score >= min_quality]
        
        # Filter by complexity
        candidates = [m for m in candidates if m.max_complexity >= complexity]
        
        if not candidates:
            # Fallback to most capable model
            return max(self.models, key=lambda m: m.quality_score)
        
        # Score candidates (lower is better)
        def score_model(m: ModelConfig) -> float:
            # Balanced scoring
            cost_score = (m.cost_per_1k_input + m.cost_per_1k_output) * 1000
            quality_penalty = (1 - m.quality_score) * 10  # Penalize lower quality
            return cost_score + quality_penalty
        
        return min(candidates, key=score_model)
    
    def complete(self, prompt: str, min_quality: float = 0.7,
                 max_cost: Optional[float] = None) -> Dict[str, Any]:
        """Route prompt to appropriate model"""
        model = self.select_model(prompt, min_quality, max_cost)
        
        # This would integrate with actual LLM APIs
        # For now, return routing decision
        return {
            "model_used": model.name,
            "estimated_cost_per_1k": model.cost_per_1k_input + model.cost_per_1k_output,
            "quality_score": model.quality_score,
            "complexity_detected": self.estimate_complexity(prompt)
        }


class TokenOptimizer:
    """Optimize prompts to reduce token usage"""
    
    def __init__(self):
        self.common_fillers = [
            "please", "kindly", "I would like to", "if you could",
            "I was wondering if", "it would be great if"
        ]
    
    def compress_prompt(self, prompt: str) -> Dict[str, Any]:
        """Compress prompt while preserving meaning"""
        original_tokens = self.estimate_tokens(prompt)
        
        # Remove redundant whitespace
        compressed = " ".join(prompt.split())
        
        # Remove filler phrases
        for filler in self.common_fillers:
            compressed = compressed.replace(filler, "")
        
        # Clean up extra spaces
        compressed = " ".join(compressed.split())
        
        new_tokens = self.estimate_tokens(compressed)
        
        return {
            "original": prompt,
            "compressed": compressed,
            "original_tokens": original_tokens,
            "tokens": new_tokens,
            "savings": original_tokens - new_tokens,
            "savings_percent": (original_tokens - new_tokens) / original_tokens * 100
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def summarize_history(self, messages: List[Dict], max_tokens: int = 4000,
                          preserve_key_facts: bool = True) -> List[Dict]:
        """Summarize conversation history to fit in token limit"""
        # Simple truncation strategy
        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)
        
        if total_tokens <= max_tokens:
            return messages
        
        # Keep first (system) and last N messages
        result = []
        if messages and messages[0].get("role") == "system":
            result.append(messages[0])
        
        # Add recent messages until limit
        remaining_budget = max_tokens - self.estimate_tokens(result[0].get("content", "")) if result else max_tokens
        recent_messages = []
        
        for msg in reversed(messages[len(result):]):
            msg_tokens = self.estimate_tokens(msg.get("content", ""))
            if msg_tokens <= remaining_budget:
                recent_messages.insert(0, msg)
                remaining_budget -= msg_tokens
            else:
                break
        
        result.extend(recent_messages)
        return result


class SavingsCalculator:
    """Calculate potential cost savings"""
    
    def estimate(self, monthly_cost: float, cache_hit_rate: float = 0.25,
                 routing_savings: float = 0.30, token_optimization: float = 0.20) -> Dict[str, float]:
        """Estimate monthly and yearly savings"""
        
        # Calculate savings from each strategy
        cache_savings = monthly_cost * cache_hit_rate * 0.9  # 90% of cached queries
        routing_savings_amt = monthly_cost * routing_savings
        token_savings = monthly_cost * token_optimization
        
        # Total savings (with overlap adjustment)
        total_monthly = (cache_savings + routing_savings_amt + token_savings) * 0.8
        
        return {
            "monthly": total_monthly,
            "yearly": total_monthly * 12,
            "cache_savings": cache_savings,
            "routing_savings": routing_savings_amt,
            "token_savings": token_savings,
            "roi_percent": (total_monthly / monthly_cost) * 100 if monthly_cost > 0 else 0
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cost_optimizer.py [cache|route|optimize|estimate]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "estimate":
        calc = SavingsCalculator()
        savings = calc.estimate(
            monthly_cost=1000,
            cache_hit_rate=0.25,
            routing_savings=0.30,
            token_optimization=0.20
        )
        print(json.dumps(savings, indent=2))
    elif command == "route":
        router = ModelRouter()
        result = router.complete("Explain quantum computing simply")
        print(json.dumps(result, indent=2))
    else:
        print(f"Demo mode: {command}")