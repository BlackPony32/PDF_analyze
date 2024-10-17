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
            "input": """Analyze my dataset according to the following rules:
- 25 percent of the answer should be devoted to statistical analysis. giving basic mathematical insights from the data is useful for business!
- 75 percent of the answer should be a detailed answer on data analysis - written in a way that is understandable for an ordinary user with an emphasis on business data analytics. For example, the difference in product sales in different periods of time. The answer should be as detailed as possible.
- It should be a voluminous answer disclosing the data to the maximum!
- answer should be only in txt format - not markdown formatting"""
        }
    )
    
    return result

def final_gen(file_path):
    agent_answer = final_agent_gen(file_path) 
    final_answer = agent_answer.get("output")

    with open('src/final_gen.txt', 'w') as file:
        file.write(final_answer)