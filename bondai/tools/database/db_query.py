import os
import psycopg2
from pydantic import BaseModel
from bondai.tools import Tool
from bondai.models.openai import OpenAILLM, MODEL_GPT35_TURBO_16K

class Parameters(BaseModel):
    question: str
    thought: str

TOOL_NAME = 'database_query_tool'
QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a database. Use the provided information to answer the user's QUESTION at the very end."
TOOL_DESCRIPTION = (
    "This tool allows you to ask a question and retrieve data from the user's database."
    "DO NOT ask the user for any additional information about the database."
    "All necessary information to connect to the database has already been captured."
    "Just specify your question using the 'question' parameter."
    "Your question will automatically be turned into SQL and the response will contain the resulting data."
)

PG_URI = os.environ.get('PG_URI')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = int(os.environ.get('PG_HOST', '5432'))
PG_USERNAME = os.environ.get('PG_USERNAME')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_DBNAME = os.environ.get('PG_DBNAME')

MAX_QUERY_RETRIES = 3

QUERY_PROMPT_TEMPLATE = """
Using the database schema below respond with a SQL query to answer the user's QUESTION.
VERY IMPORTANT: You must respond ONLY with a SQL query. Do not respond with any other text.

# DATABASE SCHEMA #

###DBSCHEMA###


# QUESTION #

###QUESTION###

VERY IMPORTANT: You must respond ONLY with a SQL query. Do not respond with any other text.
"""

RESPONSE_PROMPT_TEMPLATE = """
You were asked the following question:
###QUESTION###

The following information was returned from the database:
###QUERY_RESULTS###

Please respond with a friendly text response to the user's question.
"""

class DatabaseQueryTool(Tool):
    def __init__(self, 
                 pg_uri=PG_URI, 
                 pg_host=PG_HOST, 
                 pg_port=PG_PORT, 
                 pg_username=PG_USERNAME, 
                 pg_password=PG_PASSWORD, 
                 pg_dbname=PG_DBNAME,
                 llm=OpenAILLM(MODEL_GPT35_TURBO_16K)
            ):
        super(DatabaseQueryTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.pg_uri = pg_uri
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_username = pg_username
        self.pg_password = pg_password
        self.pg_dbname = pg_dbname
        self.llm = llm
    
    def run(self, arguments):
        question = arguments['question']

        if question is None:
            raise Exception('question is required')

        schema_str = self.__get_database_schema()
        query_prompt = QUERY_PROMPT_TEMPLATE.replace("###DBSCHEMA###", schema_str)
        query_prompt = query_prompt.replace("###QUESTION###", question)

        attempts = 0
        while True:
            try:
                query_response, _ = self.llm.get_completion(query_prompt)
                rows, colnames = self.__query_database(query_response)
                return self.__format_response(rows, colnames)
            except Exception as e:
                attempts += 1
                if attempts > MAX_QUERY_RETRIES:
                    raise e
    
    def __format_response(self, rows, colnames):
        markdown_output = "| " + " | ".join(colnames) + " |\n"
        markdown_output += "| " + " | ".join(["---"] * len(colnames)) + " |\n"

        for row in rows:
            markdown_output += "| " + " | ".join(map(str, row)) + " |\n"
        
        return markdown_output

    def __get_database_connection(self):
        if self.pg_uri:
            # Establish the connection
            return psycopg2.connect(self.pg_uri, sslmode='require')
        else:
            # Establish the connection
            return psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                user=self.pg_username,
                password=self.pg_password,
                dbname=self.pg_dbname
            )
    
    def __query_database(self, query):
        connection = None
        cursor = None
        try:
            connection = self.__get_database_connection()

            # Create a new cursor
            cursor = connection.cursor()

            # Execute the query
            cursor.execute(query)

            colnames = [desc[0] for desc in cursor.description]

            # Fetch all rows from the query result
            return cursor.fetchall(), colnames
        finally:
            # Close the cursor and the connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def __get_database_schema(self):
        # Query the schema from information_schema
        rows, _ = self.__query_database((
            "SELECT table_name, column_name, data_type, is_nullable, column_default\n"
            "FROM information_schema.columns\n"
            "WHERE table_schema = 'public'\n"
            "ORDER BY table_name, ordinal_position;"
        ))

        # Process the rows to create a formatted string
        schema_str = ""
        current_table = None
        for row in rows:
            table, column, data_type, is_nullable, default = row
            if table != current_table:
                if current_table:
                    schema_str += "\n"
                schema_str += f"Table: {table}\n"
                schema_str += "-" * (len(table) + 8) + "\n"
                current_table = table
            schema_str += f"{column}: {data_type}"
            if is_nullable == "NO":
                schema_str += " NOT NULL"
            if default:
                schema_str += f" DEFAULT {default}"
            schema_str += "\n"

        return schema_str


        



