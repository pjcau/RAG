import os
import sqlite3
from typing import List, Dict, Any
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType
from langchain_community.llms import Ollama
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParserWithRetries
from langchain_core.exceptions import OutputParserException


MODEL_NAME = "gemma3:12b"
TEMPERATURE = 0.0


# Configuration
DB_PATH = "cars_motors_data.db"


def format_sql_results(results: List[tuple], columns: List[str]) -> str:
    """Format SQL query results into a readable string"""
    if not results:
        return "No results found"

    output = []
    for row in results:
        row_dict = dict(zip(columns, row))
        formatted_row = "\n".join(
            [f"{col}: {val}" for col, val in row_dict.items()])
        output.append(formatted_row)

    return "\n\n".join(output)


def create_World_Wide_agent():
    """Create a SQL agent for World Wide database"""
    print(
        f"DB exist  {os.path.exists(DB_PATH)}")  # Should return True if the file exists

    # Initialize the database connection
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

    # Initialize the language model
    llm = OllamaLLM(
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    output_parser = StructuredChatOutputParserWithRetries.from_llm(llm=llm)

    # Create the SQL toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Custom system message for World Wide-specific queries
    system_message = SystemMessage(content="""You are an AI assistant specialized in querying World Wide Motors database. 
    The database contains information about World Wide vehicles including models, variants, prices, specifications, and sales data.
    
    When analyzing the data:
    1. Always format prices as currency with commas
    3. For any analysis, mention the sample size you're using
    4. Be specific about which models and variants you're discussing
    
    Guidelines for your responses:
    1. If asked about trends, include specific numbers and percentages
    2. For price analysis, mention both average and range
    3. When comparing models, cite specific differences in specifications
    4. If the data is insufficient, clearly state what's missing
    
    Before executing any query:
    1. Verify table and column names
    2. Check query syntax
    3. Ensure proper joins if needed
    4. Add appropriate limiting clauses
    
    DO NOT make any modifications to the database (no INSERT, UPDATE, DELETE, etc.).""")

    # Create the agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        system_message=system_message,
        output_parser=output_parser
    )

    return agent


def main():
    print("Welcome to the World Wide Motors Database Agent")
    print("Loading agent...")

    try:
        agent = create_World_Wide_agent()

        print("\nAgent initialized successfully!")
        print("\nYou can ask questions about World Wide vehicles, such as:")
        print("- What's the average price of  Mercedes-AMG G?")
        print("- How many vehicles were sold in California?")
        print("- Compare the specifications of Mercedes-AMG G and Audi RS e-tron GT ")
        print("\nType 'quit' to exit")

        while True:
            question = input(
                "\nWhat would you like to know about World Wide vehicles? ").strip()

            if question.lower() == 'quit':
                print(
                    "Thank you for using the World Wide Motors Database Agent. Goodbye!")
                break

            try:
                # Get response from agent
                response = agent.invoke({"input": question})

                # Print the response
                print("\nAnswer:", response["output"])

            except Exception as e:
                print(f"Error processing query: {str(e)}")
                print("Please try rephrasing your question.")

    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        print("Please check your database connection")


if __name__ == "__main__":
    main()
