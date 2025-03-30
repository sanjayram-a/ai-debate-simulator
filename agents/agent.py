import asyncio
from typing import Optional, Dict, Any
from llama_index.llms.ollama import Ollama

class Agent:
    def __init__(
        self,
        name: str,
        domain: str,
        knowledge_base,
        llm_type: str = "ollama",
        model_name: str = "qwen2.5:3b"
    ):
        """
        Initialize an Agent.

        Args:
            name (str): The name of the agent
            domain (str): The domain of expertise
            knowledge_base: The knowledge base for accessing domain-specific information
            llm_type (str): The type of LLM to use
            model_name (str): The name of the model to use
        """
        self.name = name
        self.domain = domain
        self.knowledge_base = knowledge_base
        self.llm_type = llm_type
        self.model_name = model_name
        self.context: Dict[str, Any] = {}
    
    
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response based on the prompt and context.

        Args:
            prompt (str): The input prompt
            context (Dict[str, Any], optional): Additional context for the response

        Returns:
            str: The generated response
        """
        # Update context with any new information
        if context:
            self.context.update(context)

        # Combine prompt with relevant knowledge from knowledge base
        enhanced_prompt = self.knowledge_base.enhance_prompt(prompt, self.domain)

        # Initialize LLM based on type
        if self.llm_type == "ollama":
            llm = Ollama(model=self.model_name, temperature=0.7,request_timeout=300)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

        # Create the full prompt with system prompt and context
        full_prompt = f"""{self.system_prompt}

        The current context includes:
        - Topic: {self.context.get('topic', 'Unknown')}
        - Round: {self.context.get('current_round', 0)} of {self.context.get('total_rounds', 0)}

        {enhanced_prompt}

Provide your expert perspective, using the knowledge from your domain to support your arguments."""

        # Generate response using LLM
        response = llm.complete(full_prompt)
        return f"[{self.name}]: {str(response)}"

    def reset_context(self):
        """Reset the agent's context."""
        self.context = {}

    @property
    def system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            str: The system prompt describing the agent's role and capabilities
        """
        return f"""You are an expert in {self.domain} speaking from that perspective.
        Your name is {self.name}.
        Base your responses on factual knowledge and current best practices in {self.domain}.
        Maintain a professional and objective tone while engaging in constructive debate. debate under 100words with simple words"""