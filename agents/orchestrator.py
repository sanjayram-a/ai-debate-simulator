import asyncio
from typing import List, Dict, Any
from .agent import Agent

class DebateOrchestrator:
    def __init__(
        self,
        topic: str,
        agents: List[Agent],
        rounds: int = 3,
        summary_llm_type: str = "ollama",
        summary_model_name: str = "qwen2.5:3b"
    ):
        """
        Initialize a DebateOrchestrator.

        Args:
            topic (str): The debate topic
            agents (List[Agent]): List of agents participating in the debate
            rounds (int): Number of debate rounds
            summary_llm_type (str): LLM type for generating summaries
            summary_model_name (str): Model name for generating summaries
        """
        self.topic = topic
        self.agents = agents
        self.total_rounds = rounds
        self.current_round = 0
        self.debate_log: List[Dict[str, Any]] = []
        self.summary = ""
        self.status = "initialized"
        self.summary_llm_type = summary_llm_type
        self.summary_model_name = summary_model_name

    async def conduct_round(self) -> None:
        """Conduct a single round of debate."""
        self.current_round += 1
        round_log = []

        # Generate context for this round
        context = {
            "topic": self.topic,
            "round": self.current_round,
            "total_rounds": self.total_rounds,
            "previous_responses": self.debate_log
        }

        # Each agent takes a turn
        for agent in self.agents:
            prompt = self._generate_prompt(agent, context)
            response = await agent.generate_response(prompt, context)
            round_log.append({
                "agent": agent.name,
                "response": response
            })

        self.debate_log.extend(round_log)

    def _generate_prompt(self, agent: Agent, context: Dict[str, Any]) -> str:
        """Generate a prompt for an agent based on context."""
        if self.current_round == 1:
            return f"As an expert in {agent.domain}, what is your initial position on the topic: {self.topic}?"
        else:
            # Include previous responses in the prompt
            previous_responses = "\n".join([
                f"{entry['agent']}: {entry['response']}"
                for entry in self.debate_log[-len(self.agents):]
            ])
            return f"""Consider the previous responses:

{previous_responses}

As an expert in {agent.domain}, how do you respond to these points regarding {self.topic}?"""

    async def generate_summary(self) -> str:
        """Generate a summary of the debate."""
        # TODO: Implement actual summary generation using LLM
        # For now, return a simple summary
        points = "\n".join([f"- {entry['agent']}: {entry['response']}" 
                           for entry in self.debate_log])
        self.summary =  f"""Debate Summary:
        Topic: {self.topic}
        Number of Rounds: {self.current_round}
        Key Points:
        {points}"""
        return self.summary


    async def conduct_debate(self) -> None:
        """Conduct the entire debate synchronously."""
        self.status = "in_progress"
        
        try:
            for _ in range(self.total_rounds):
                await self.conduct_round()
            
            await self.generate_summary()
            self.status = "completed"
        except Exception as e:
            self.status = "error"
            raise e

    def conduct_debate_async(self) -> None:
        """Start the debate asynchronously."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.conduct_debate())
        except Exception as e:
            self.status = "error"
            raise e
        finally:
            loop.close()

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the debate."""
        return {
            "status": self.status,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "agents": [agent.name for agent in self.agents],
            "log_length": len(self.debate_log),
            "has_summary": bool(self.summary)
        }