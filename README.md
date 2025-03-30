# AI Debate Simulator

An interactive platform that enables AI agents from different domains to engage in structured debates on various topics.

## Project Overview

The AI Debate Simulator is a Flask-based web application that facilitates debates between AI agents specialized in different domains. Each agent utilizes domain-specific knowledge bases and Large Language Models (LLMs) to generate informed responses and engage in meaningful discussions.

## System Architecture

### Core Components

1. **Web Application (`app.py`)**
   - Flask server handling HTTP requests
   - Manages debate creation and status
   - Provides API endpoints for debate interaction

2. **Agent System (`agents/`)**
   - `agent.py`: Defines the base Agent class for debate participants
   - `orchestrator.py`: Manages debate flow and agent interactions
   - `specializations.py`: Creates domain-specific agents

3. **Knowledge Base (`knowledge_base/`)**
   - Domain-specific knowledge storage
   - RAG (Retrieval-Augmented Generation) implementation
   - Organized by domains (AI, Data Science, ML, etc.)

4. **Frontend (`static/`, `templates/`)**
   - Web interface for debate interaction
   - Real-time debate status updates
   - Debate visualization and logging

## Setup & Installation

1. Clone the repository
2. Set up a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure Ollama is installed and running for LLM support

## Usage Guide

1. Start the application:
   ```bash
   python app.py
   ```
2. Navigate to `http://localhost:5000` in your browser
3. Create a new debate by:
   - Selecting a topic
   - Choosing participating domains (minimum 2)
   - Setting the number of rounds
   - Selecting LLM type and model

## API Endpoints

### Main Routes

- `GET /`: Home page with debate creation form
- `GET /debates`: List of all active debates
- `POST /start_debate`: Initialize a new debate
- `GET /debate/<debate_id>`: View specific debate

### API Routes

- `GET /api/debate/<debate_id>/status`: Get debate status
  ```json
  {
    "status": "in_progress",
    "current_round": 2,
    "total_rounds": 3,
    "agents": ["AI Expert", "Data Scientist"],
    "log_length": 4,
    "has_summary": false
  }
  ```
- `GET /api/debate/<debate_id>/log`: Get debate log and summary
  ```json
  {
    "status": "completed",
    "log": [...],
    "summary": "Debate summary text"
  }
  ```

## Key Features

- Asynchronous debate progression
- Domain-specific knowledge integration
- Real-time status updates
- Automated debate summarization
- Multi-round structured discussions
- Support for various LLM backends

## Technical Details

### Agent System

The agent system consists of specialized AI agents that:
- Access domain-specific knowledge bases
- Generate contextual responses
- Maintain conversation history
- Support multiple LLM backends

### Debate Orchestration

The DebateOrchestrator manages:
- Round progression
- Agent turn management
- Context maintenance
- Summary generation
- Status tracking

## Supported Domains

Current knowledge domains include:
- Artificial Intelligence
- Data Analytics
- Data Science
- Machine Learning
- Programming
- UI/UX Design

Each domain has its own knowledge base stored in `knowledge_base/domains/`.