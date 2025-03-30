import asyncio
from typing import List, Dict, Any
from .agent import Agent
import markdown
from llama_index.llms.ollama import Ollama

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
        self.summary_llm_type = "ollama"
        self.summary_model_name = "qwen2.5:3b"

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
        points = "\n".join([f"- {entry['agent']}: {entry['response']}" 
                           for entry in self.debate_log])
        prompt = f"""As an expert debate analyzer, provide a comprehensive markdown-formatted summary of this AI debate:

        {self.topic}

        ## Debate Overview
        - **Total Rounds**: {self.current_round}
        - **Participants**: {", ".join(agent.name for agent in self.agents)}

        ## Key Arguments
        {points}

        ## Analysis

        ### Main Points by Each Participant

        ###winner

        ### Conclusion 

        Note: dont give any debate agent respones in the summary, also give winner if possible,
        Format the response maintaining the markdown structure with proper headers, bullet points, and emphasis."""

        # Use LLM to generate summary
        if self.summary_llm_type == "ollama":
            llm = Ollama(model=self.summary_model_name, temperature=0.7, request_timeout=300)
        else:
            raise ValueError(f"Unsupported LLM type: {self.summary_llm_type}")

        try:
            response = llm.complete(prompt)
            # Clean the response and ensure it's a string
            response_text = str(response).strip()
            
            # Convert markdown to HTML with safe extensions
            self.summary = markdown.markdown(
                response_text,
                extensions=['extra', 'nl2br'],
                output_format='html5',
                safe_mode='escape'
            )
            return self.summary
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            print(error_msg)
            self.summary = f"<p class='error'>{error_msg}</p>"
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

    def _analyze_debate_quality(self) -> Dict[str, Any]:
        """Analyze the quality and progression of the debate."""
        analysis = {
            "participation": {},
            "interaction_score": 0,
            "knowledge_usage": {},
            "topic_adherence": 0
        }
        
        # Analyze participation and knowledge usage for each agent
        for agent in self.agents:
            agent_responses = [entry for entry in self.debate_log if entry["agent"] == agent.name]
            analysis["participation"][agent.name] = len(agent_responses)
            
            # Count domain-specific references
            knowledge_refs = sum(1 for entry in agent_responses
                              if f"[{agent.domain}]" in entry["response"])
            analysis["knowledge_usage"][agent.name] = knowledge_refs

        # Calculate interaction score based on cross-references
        total_responses = len(self.debate_log)
        cross_refs = sum(1 for entry in self.debate_log[len(self.agents):]
                        if any(agent.name in entry["response"]
                              for agent in self.agents))
        if total_responses > len(self.agents):
            analysis["interaction_score"] = cross_refs / (total_responses - len(self.agents))

        # Calculate topic adherence
        topic_mentions = sum(1 for entry in self.debate_log
                           if self.topic.lower() in entry["response"].lower())
        analysis["topic_adherence"] = topic_mentions / total_responses if total_responses > 0 else 0

        return analysis

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the debate with quality metrics."""
        status = {
            "status": self.status,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "agents": [agent.name for agent in self.agents],
            "log_length": len(self.debate_log),
            "has_summary": bool(self.summary)
        }

        # Add debate quality analysis if debate has started
        if self.debate_log:
            status["analysis"] = self._analyze_debate_quality()

        return status