from DatabaseConnector import DatabaseConnector
from SQLTunerAgent import SQLTunerAgent
from StreamlitApp import StreamlitApp

if __name__ == "__main__":
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'sakila'
    }

    # Initialize objects
    db_connector = DatabaseConnector(db_type='mysql', **db_params)
    sql_tuner_agent = SQLTunerAgent(db_connector)

    # Run the Streamlit app
    app = StreamlitApp(db_connector, sql_tuner_agent)
    app.run()