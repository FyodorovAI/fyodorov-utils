# Fyodorov LLM Agents

<p>
<img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/fyodorovai/fyodorov-llm-agents" />
<img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/fyodorovai/fyodorov-llm-agents" />
<img alt="" src="https://img.shields.io/github/repo-size/fyodorovai/fyodorov-llm-agents" />
<img alt="GitHub Issues" src="https://img.shields.io/github/issues/fyodorovai/fyodorov-llm-agents" />
<img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/fyodorovai/fyodorov-llm-agents" />
</p>

`fyodorov_llm_agents` is a Python library that provides tooling for creating LLM-based agents using arbitrary API 
providers (such as OpenAI). You can optionally provide those agents with **tools** (via ChatGPT style plugins) and 
search to perform Retrieval Augmented Generation (RAG).

This library is used in the FyodorovAI suite to create agents and provide them with tools and access to a search 
database.

```Python
# Importing the library
from fyodorov_llm_agents import create_agent, OpenAIProvider, Tool, DostoyevskyRAG
agent = create_agent(
    llm=OpenAIProvider(api_key="###"),
    tools = [
        Tool("https://example.com/.well-known/tool-name.json"),
    ],
    rag=[
        DostoyevskyRAG(endpoint="https://dostoyevsky.example.com"),
    ],
)
```

## Installation

You can install `fyodorov_llm_agents` using pip: 
```shell
pip install fyodorov-llm-agents==0.0.1
```
