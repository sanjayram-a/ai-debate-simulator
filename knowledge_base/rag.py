import os
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.node_parser import SentenceSplitter

class KnowledgeBase:
    """RAG knowledge base for debate agents"""

    def __init__(
        self,
        domain_name: str,
        documents_dir: str,
        embedding_model: str = "nomic-embed-text:latest",
        llm_model: str = "qwen2.5:3b"
    ):
        self.domain_name = domain_name
        self.documents_dir = documents_dir
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.index = None

        # Initialize the knowledge base
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the vector database with documents."""
        try:
            # Configure settings
            Settings.embed_model = OllamaEmbedding(model_name=self.embedding_model)
            Settings.llm = Ollama(model=self.llm_model)
            Settings.node_parser = SentenceSplitter(chunk_size=1024)

            # Check if documents directory exists
            if not os.path.exists(self.documents_dir):
                print(f"Warning: Documents directory {self.documents_dir} does not exist.")
                # Create an empty index
                self.index = VectorStoreIndex([])
                return

            # Load documents
            documents = SimpleDirectoryReader(self.documents_dir).load_data()

            if not documents:
                print(f"Warning: No documents found in {self.documents_dir}")
                # Create an empty index
                self.index = VectorStoreIndex([])
                return

            print(f"Loaded {len(documents)} documents for domain: {self.domain_name}")

            # Create index
            self.index = VectorStoreIndex.from_documents(documents)

        except Exception as e:
            print(f"Error initializing knowledge base for {self.domain_name}: {e}")
            # Create an empty index as fallback
            self.index = VectorStoreIndex([])

    def enhance_prompt(self, prompt: str, domain: str) -> str:
        """
        Enhance a prompt with relevant knowledge from the knowledge base.
        
        Args:
            prompt (str): The original prompt
            domain (str): The domain of expertise
            
        Returns:
            str: The enhanced prompt with relevant context
        """
        try:
            # Query the knowledge base for relevant information
            context = self.query(prompt)
            
            # Combine the original prompt with retrieved context
            enhanced_prompt = f"""Use the following domain knowledge to inform your response:
{context}

Original prompt:
{prompt}"""
            
            return enhanced_prompt
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            return prompt  # Return original prompt if enhancement fails
            
    def query(self, query_text: str, max_tokens: int = 1024) -> str:
        """Query the knowledge base for information relevant to the query."""
        try:
            if not self.index:
                return f"[No knowledge base available for {self.domain_name}]"

            query_engine = self.index.as_query_engine(response_mode="tree_summarize",)
            response = query_engine.query(query_text)

            # Limit response length
            response_text = str(response)
            if len(response_text) > max_tokens:
                response_text = response_text[:max_tokens] + " [truncated]"

            return response_text
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return f"[Error retrieving information: {e}]"

    def add_document(self, content: str, doc_id: str) -> bool:
        """Add a new document to the knowledge base."""
        try:
            # Not implementing for this simple version
            return False
        except Exception as e:
            print(f"Error adding document: {e}")
            return False


class DomainKnowledgeBaseManager:
    """Manager for multiple domain-specific knowledge bases"""

    def __init__(self, base_dir: str = "knowledge_base/domains", embedding_model: str = "nomic-embed-text:latest"):
        self.base_dir = base_dir
        self.embedding_model = embedding_model
        self.knowledge_bases = {}

        # Initialize knowledge bases for each domain
        self._initialize_domains()

    def _initialize_domains(self) -> None:
        """Initialize knowledge bases for all domains."""
        # Define our domains
        domains = ["ai", "data_science", "ml", "data_analytics", "programming", "ui_ux"]

        for domain in domains:
            domain_dir = os.path.join(self.base_dir, domain)

            # Create directory if it doesn't exist
            if not os.path.exists(domain_dir):
                os.makedirs(domain_dir, exist_ok=True)

            # Initialize knowledge base for this domain
            self.knowledge_bases[domain] = KnowledgeBase(
                domain_name=domain,
                documents_dir=domain_dir,
                embedding_model=self.embedding_model
            )

            print(f"Initialized knowledge base for {domain}")

    def get_knowledge_base(self, domain: str) -> Optional[KnowledgeBase]:
        """Get the knowledge base for a specific domain."""
        return self.knowledge_bases.get(domain)

    def query_domain(self, domain: str, query_text: str) -> str:
        """Query a specific domain knowledge base."""
        kb = self.get_knowledge_base(domain)
        if not kb:
            return f"[Domain '{domain}' not found]"

        return kb.query(query_text)

    def query_all_domains(self, query_text: str) -> Dict[str, str]:
        """Query all domain knowledge bases and return combined results."""
        results = {}
        for domain, kb in self.knowledge_bases.items():
            results[domain] = kb.query(query_text)

        return results