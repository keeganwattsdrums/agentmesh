#!/usr/bin/env python3
"""
Initialize the competitive intelligence tracking database.
Creates SQLite database with predefined schema and default competitors.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.expanduser("~/competitive-intel.db")

COMPETITORS = [
    {
        "name": "Mem0",
        "category": "memory",
        "website": "https://mem0.ai",
        "pricing_url": "https://mem0.ai/pricing",
        "docs_url": "https://docs.mem0.ai",
        "description": "Memory layer for AI agents",
        "founded": "2024",
        "funding": "$YCombinator"
    },
    {
        "name": "LangSmith",
        "category": "observability", 
        "website": "https://smith.langchain.com",
        "pricing_url": "https://smith.langchain.com/pricing",
        "docs_url": "https://docs.smith.langchain.com",
        "description": "LLM observability and evaluation platform by LangChain",
        "founded": "2023",
        "funding": "LangChain Inc"
    },
    {
        "name": "Pinecone",
        "category": "vector-db",
        "website": "https://pinecone.io",
        "pricing_url": "https://pinecone.io/pricing",
        "docs_url": "https://docs.pinecone.io",
        "description": "Managed vector database for AI applications",
        "founded": "2019",
        "funding": "$138M Series B"
    },
    {
        "name": "Chroma",
        "category": "vector-db",
        "website": "https://trychroma.com",
        "pricing_url": "https://trychroma.com/pricing",
        "docs_url": "https://docs.trychroma.com",
        "description": "Open-source embedding database",
        "founded": "2022",
        "funding": "$18M Seed"
    },
    {
        "name": "Weaviate",
        "category": "vector-db",
        "website": "https://weaviate.io",
        "pricing_url": "https://weaviate.io/pricing",
        "docs_url": "https://weaviate.io/developers",
        "description": "Vector search engine with GraphQL interface",
        "founded": "2019",
        "funding": "$50M Series B"
    },
    {
        "name": "AutoGen",
        "category": "agent-framework",
        "website": "https://microsoft.github.io/autogen",
        "pricing_url": "https://microsoft.github.io/autogen",
        "docs_url": "https://microsoft.github.io/autogen/docs",
        "description": "Multi-agent conversation framework by Microsoft",
        "founded": "2023",
        "funding": "Microsoft Research"
    },
    {
        "name": "CrewAI",
        "category": "agent-framework",
        "website": "https://crewai.com",
        "pricing_url": "https://crewai.com/pricing",
        "docs_url": "https://docs.crewai.com",
        "description": "Framework for orchestrating role-playing AI agents",
        "founded": "2023",
        "funding": "Independent"
    }
]

PRICING_DATA = {
    "Mem0": [
        {"tier": "Developer", "price": 0, "unit": "free", "limits": "10k requests/month"},
        {"tier": "Pro", "price": 29, "unit": "month", "limits": "100k requests + features"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Unlimited + SLA"}
    ],
    "LangSmith": [
        {"tier": "Developer", "price": 0, "unit": "free", "limits": "5k traces/month"},
        {"tier": "Plus", "price": 39, "unit": "month", "limits": "10k traces + features"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Unlimited traces"}
    ],
    "Pinecone": [
        {"tier": "Starter", "price": 0, "unit": "free", "limits": "100k vectors, 1 pod"},
        {"tier": "Standard", "price": 70, "unit": "month", "limits": "2M vectors, 1 pod"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Custom resources"}
    ],
    "Chroma": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "Self-hosted, unlimited"},
        {"tier": "Cloud", "price": 0, "unit": "waitlist", "limits": "Managed service"}
    ],
    "Weaviate": [
        {"tier": "Sandbox", "price": 0, "unit": "free", "limits": "14-day trial"},
        {"tier": "Standard", "price": 25, "unit": "month", "limits": "Hosted, SLA"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Custom deployment"}
    ],
    "AutoGen": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "Apache 2.0 license"},
        {"tier": "Studio", "price": 0, "unit": "preview", "limits": "Visual IDE"}
    ],
    "CrewAI": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "Self-hosted"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Enterprise features"}
    ]
}

FEATURE_DATA = {
    "Mem0": {
        "memory_type": "Long-term, context-aware",
        "integration": "Python, JS, OpenAI, LangChain",
        "deployment": "Cloud, Self-hosted",
        "api_type": "REST API",
        "unique_features": ["Memory graph", "Multi-user support", "Adaptive personalization"]
    },
    "LangSmith": {
        "tracing": "Yes",
        "evaluation": "Yes, built-in datasets",
        "prompt_management": "Yes",
        "monitoring": "Real-time dashboards",
        "integration": "LangChain native",
        "unique_features": ["A/B testing", "Feedback collection", "Cost tracking"]
    },
    "Pinecone": {
        "indexing": "Real-time",
        "metadata_filtering": "Yes",
        "hybrid_search": "Yes",
        "scaling": "Auto-scale pods",
        "unique_features": ["Metadata filtering", "Namespace isolation", "Hybrid search"]
    },
    "Chroma": {
        "indexing": "Local/Cloud",
        "metadata_filtering": "Yes",
        "deployment": "Local, Docker, Cloud",
        "unique_features": ["Local-first", "Simple API", "Multi-modal"]
    },
    "Weaviate": {
        "query_interface": "GraphQL, REST",
        "modules": "Text2vec, QnA, Summarize",
        "hybrid_search": "Yes",
        "vectorization": "Built-in or bring-your-own",
        "unique_features": ["GraphQL interface", "Modular AI integrations", "Vector+BM25 hybrid"]
    },
    "AutoGen": {
        "agent_types": "Conversable, Assistant, UserProxy",
        "conversation_flow": "Multi-agent, group chat",
        "code_execution": "Yes, local/docker",
        "human_in_loop": "Yes",
        "unique_features": ["Code generation & execution", "Human-in-the-loop", "Custom agents"]
    },
    "CrewAI": {
        "agent_types": "Role-based",
        "task_management": "Sequential, hierarchical",
        "tools": "LangChain compatible",
        "process": "Structured workflows",
        "unique_features": ["Role-based agents", "Process orchestration", "Crew-based collaboration"]
    }
}

def init_database():
    """Initialize the SQLite database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Competitors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            website TEXT,
            pricing_url TEXT,
            docs_url TEXT,
            description TEXT,
            founded TEXT,
            funding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pricing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            tier TEXT NOT NULL,
            price REAL,
            unit TEXT,
            limits TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )
    ''')
    
    # Features table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            feature_name TEXT NOT NULL,
            feature_value TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )
    ''')
    
    # Launches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS launches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            launch_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            source_url TEXT,
            announced_at TIMESTAMP,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )
    ''')
    
    # Positioning table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positioning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            key_message TEXT,
            target_audience TEXT,
            differentiators TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT,
            title TEXT NOT NULL,
            description TEXT,
            old_value TEXT,
            new_value TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized at {DB_PATH}")

def populate_competitors():
    """Populate database with default competitors."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for comp in COMPETITORS:
        cursor.execute('''
            INSERT OR IGNORE INTO competitors 
            (name, category, website, pricing_url, docs_url, description, founded, funding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            comp["name"], comp["category"], comp["website"], 
            comp["pricing_url"], comp["docs_url"], comp["description"],
            comp["founded"], comp["funding"]
        ))
    
    conn.commit()
    conn.close()
    print(f"✓ Added {len(COMPETITORS)} competitors")

def populate_pricing():
    """Populate database with initial pricing data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for comp_name, tiers in PRICING_DATA.items():
        cursor.execute("SELECT id FROM competitors WHERE name = ?", (comp_name,))
        result = cursor.fetchone()
        if result:
            comp_id = result[0]
            for tier in tiers:
                cursor.execute('''
                    INSERT INTO pricing (competitor_id, tier, price, unit, limits)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comp_id, tier["tier"], tier["price"], tier["unit"], tier["limits"]))
    
    conn.commit()
    conn.close()
    print("✓ Added pricing data")

def populate_features():
    """Populate database with initial feature data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for comp_name, features in FEATURE_DATA.items():
        cursor.execute("SELECT id FROM competitors WHERE name = ?", (comp_name,))
        result = cursor.fetchone()
        if result:
            comp_id = result[0]
            for feature_name, feature_value in features.items():
                if isinstance(feature_value, list):
                    feature_value = json.dumps(feature_value)
                cursor.execute('''
                    INSERT INTO features (competitor_id, feature_name, feature_value)
                    VALUES (?, ?, ?)
                ''', (comp_id, feature_name, feature_value))
    
    conn.commit()
    conn.close()
    print("✓ Added feature data")

if __name__ == "__main__":
    print("🚀 Initializing Competitive Intelligence Database...")
    init_database()
    populate_competitors()
    populate_pricing()
    populate_features()
    print("\n✅ Database ready! Use fetch_pricing.py to update pricing data.")
