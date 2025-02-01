import mysql.connector
from langchain.agents import  initialize_agent, Tool
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import json
class SQLTunerAgent:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        # Create a SQLDatabase object
        db = SQLDatabase.from_uri(
            f"mysql+mysqlconnector://{self.db_connector.connection_params['user']}:{self.db_connector.connection_params['password']}@{self.db_connector.connection_params['host']}/{self.db_connector.connection_params['database']}"
        )

        # Initialize the LLM
        # llm = OpenAI(temperature=0)
        llm = ChatOllama(model="deepseek-r1:1.5b")

        # Create the SQL toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        # Define your custom prompt template
        prompt_template = PromptTemplate(
            input_variables=["query"],
            template="""
            You are a SQL DBA expert. Tune the following SQL query for better performance. 
            Return the optimized SQL query in JSON format like this:
            ```json
            {
                "query": "<optimized query>"
            }
            ```
            Do not include any additional text like ** or reasoning outside the JSON format.

            Input Query:
            {query}

            Optimized Query (in JSON format):
            """
        )

        # Create a custom chain with the prompt template
        sql_chain = LLMChain(llm=llm, prompt=prompt_template)

        # Define the tool for query tunings
        tools = [
            Tool(
                name="SQL Query Tuner",
                func=lambda query: sql_chain.run(query),
                description="Useful for tuning SQL queries to improve performance."
            )
        ]

        # Initialize the custom agent
        return initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def tune_query(self, query):
        # Run the agent with the input query
        result = self.agent_executor.run(query)
        print("result ::" + result)
        return self._extract_sql_query(result)

    def _extract_sql_query(self, output):
        try:
            # Try parsing the output as JSON
            response_dict = json.loads(output)
            return response_dict["query"]
        except (json.JSONDecodeError, KeyError):
            # Fallback: Assume the output is a plain SQL query
            return output