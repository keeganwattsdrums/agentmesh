from setuptools import setup, find_packages

setup(
    name="agentmesh",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "server": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "chromadb>=0.4.0",
            "pyjwt>=2.8.0",
        ]
    },
    author="AgentMesh Team",
    author_email="hello@agentmesh.io",
    description="The Infrastructure Platform for AI Agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/agentmesh/agentmesh",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
