from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

def final_agent_gen(file_path):
    df = pd.read_csv(file_path)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent_executor = create_pandas_dataframe_agent(
        llm,
        df,
        agent_type="tool-calling",
        verbose=True,
        allow_dangerous_code=True
    )
    result = agent_executor.invoke(
        {
            "input": """Analyze my dataset and give me an answer in 3 detailed points:
1) General data analysis
2) Statistical information - not very detailed, focus on useful information for business.
3) Detailed feedback on the data with conclusions that reveal the data and provide useful business insights that everyone can understand."""
        }
    )
    
    return result

def final_gen(file_path):
    agent_answer = final_agent_gen(file_path) 
    final_answer = agent_answer.get("output")

    with open('src/final_gen.txt', 'w') as file:
        file.write(final_answer)