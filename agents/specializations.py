from .agent import Agent

def create_agent_for_domain(domain: str, knowledge_base, llm_type: str = "ollama", model_name: str = "llama2") -> Agent:
    """
    Create a specialized agent for a specific domain.
    
    Args:
        domain (str): The domain of expertise (e.g., 'ai', 'data_science', etc.)
        knowledge_base: The knowledge base for the domain
        llm_type (str): The type of LLM to use (default: "ollama")
        model_name (str): The name of the model to use (default: "llama2")
    
    Returns:
        Agent: A specialized agent for the domain
    """
    # Create a name for the agent based on the domain
    agent_name = f"{domain.replace('_', ' ').title()} Expert"
    
    # Create the agent with domain-specific knowledge
    agent = Agent(
        name=agent_name,
        domain=domain,
        knowledge_base=knowledge_base,
        llm_type=llm_type,
        model_name=model_name
    )
    
    return agent