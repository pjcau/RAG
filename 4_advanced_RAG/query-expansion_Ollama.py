import os
from typing import List
from pydantic import BaseModel, Field
#from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
#from langchain_ollama import OllamaLLM
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

# NON FUNZIONA implementazione


# Configuration variables
CHUNK_SIZE = 100
CHUNK_OVERLAP = 20
MODEL_NAME = "llama3.2"
TEMPERATURE = 0.4

class ParaphrasedQuery(BaseModel):
    """You have performed query expansion to generate a paraphrasing of a question."""
    
    paraphrased_query: str = Field(
        ...,
        description="A unique paraphrasing of the original question.",
    )

class QueryExpander:
    """A class to handle query expansion using LangChain and OpenAI."""
    
    def __init__(self):
        """Initialize the QueryExpander with necessary components."""
        
        # Define the system prompt
        self.system_prompt = """You are an expert at expanding user questions into multiple variations. \
            Perform query expansion. If there are multiple common ways of phrasing a user question \
            or common synonyms for key words in the question, make sure to return multiple versions \
            of the query with the different phrasings.

            If there are acronyms or words you are not familiar with, do not try to rephrase them.

            Return at least 3 versions of the question that maintain the original intent."""
        
        # Set up the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
             [
              ("system", self.system_prompt),
              ("human", "{question}")
             ]
        )

        # Initialize the language model
        llm = ChatOllama(
            model=MODEL_NAME,
            emperature=TEMPERATURE      
        # other params...
        ).bind_tools([ParaphrasedQuery])
        
        # Bind tools and create analyzer
        #self.llm_with_tools = self.llm.bind_tools([ParaphrasedQuery])
        self.query_analyzer = (
            self.prompt 
            #| self.llm_with_tools 
            | PydanticToolsParser(tools=[ParaphrasedQuery])
        )
    
    def expand_query(self, question: str) -> List[str]:
        """
        Expand a question into multiple paraphrased variations.
        
        Args:
            question (str): The original question to expand
            
        Returns:
            List[str]: List of paraphrased variations of the question
        """
        try:
            # Get paraphrased queries
            results = self.query_analyzer.invoke({"question": question})
            
            # Extract just the query strings
            variations = [result.paraphrased_query for result in results]
            
            return variations
            
        except Exception as e:
            print(f"Error expanding query: {str(e)}")
            return []

def main():
    """Example usage of the QueryExpander"""
    try:
        # Initialize the expander
        expander = QueryExpander()
        
        print("Welcome to LangChain Query Expander!")
        print("Enter a question to see different variations (or 'quit' to exit)")
        print("\nExample questions:")
        print("- How to use multi-modal models in a chain?")
        print("- What's the best way to stream events from an LLM agent?")
        print("- How to implement RAG with vector databases?")
        
        while True:
            question = input("\nEnter your question: ").strip()
            
            if question.lower() == 'quit':
                print("Thank you for using LangChain Query Expander. Goodbye!")
                break
                
            print("\nGenerating variations...")
            variations = expander.expand_query(question)
            
            print("\nExpanded Queries:")
            for i, variation in enumerate(variations, 1):
                print(f"\n{i}. {variation}")
            
            print("\nTotal variations generated:", len(variations))
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()