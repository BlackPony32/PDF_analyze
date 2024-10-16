
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
from . import custom_code_exec_tool
#from t_custom_code_exec_tool import CLITool
from . import code_executing_solution
from crewai_tools import CodeInterpreterTool
from dotenv import load_dotenv
load_dotenv()
from crewai_tools import CSVSearchTool

def AI_generation_plots_summary(file):
    plots_FOLDER = 'src/plots'
    summary_FOLDER = 'src/summary'

    # Ensure folders exist
    if not os.path.exists(plots_FOLDER):
        os.makedirs(plots_FOLDER)
    if not os.path.exists(summary_FOLDER):
        os.makedirs(summary_FOLDER)

    csv_tool = CSVSearchTool()
    OpenAIGpt4 = ChatOpenAI(
        temperature=0,
        model='gpt-4o'
    )

    #______________________agents block__________________________________________
    planner = Agent(
        role="Senior Data Scientist",
        goal="""Write code to visualize the data you have received and an explanation of the visualizations you will create.
                The code should be of the highest quality
                and follow the instructions clearly. Using the tool- run it.""",
        backstory="""You're working with visual studio code with plotly go code.
                Data saved in this file path '{csv_folder}/{file_name}'.""",
        allow_delegation=False,
        memory=True,
    	verbose=True
    )

    final_sum_agent = Agent(
        role="Senior data analyst",
        goal="""Clearly analyze the data obtained and provide complete statistics on the data in the detailed answer.
        """,
        backstory="""A data analyst with extensive experience who processes and analyzes various kinds
        of data to provide maximum statistics.""",
        max_iter=4,
        verbose=True
    )
    #_______________________tasks block_________________________________________
    plan = Task(
        description="""Task Description:

                        Analyze a CSV file and generate insightful visualizations using Plotly. The provided folders and file paths are already set up, so there's no need to check their existence.

                        Input Data:

                        Load the CSV file from the given path: {csv_folder}/{file_name}.
                        
                        Tasks:

                        -Analyze the data and create {tasks_for_data_num} specific tasks.
                        -Write visualization code (functions) using Plotly Graph Objects (Plotly GO) for each task.
                        Each task should include:
                        -Informative visualizations functions that show dependencies between columns.
                        -Functional code for each visualization.
                        Ensure all tasks are executed using a try-except block to handle errors gracefully.
                        
                        Requirements for every function you should use!:

                        Load the data using the code
                        df = pd.read_csv('{csv_folder}/{file_name}')

                        -Only use columns that exist in the dataframe: {data_columns}, and check column existence using conditional statements.
                        Each function should generate:
                        -use local variables like df 
                        -One visualization.
                        -A summary explanation.
                        -do not use different written functions like load dataset
                        Example good code for one function:
                        def task_1_visualization():
                            df = pd.read_csv('{csv_folder}/{file_name}')
                            columns = {data_columns}
                            if 'billing state' in columns:
                                billing_state_counts = df['billing state'].value_counts().head(15)
                                fig = go.Figure(data=[go.Bar(x=billing_state_counts.index, y=billing_state_counts.values)])
                                fig.update_layout(title='Top 15 Billing States', xaxis=dict(title='State'), yaxis=dict(title='Number of Customers'))
                                if not os.path.exists('src/plots'):
                                    os.makedirs('src/plots')
                                fig.write_image('src/plots/chart_1.png')
                                summary = ("This chart shows the top 15 billing states by customer count...")
                                if not os.path.exists('src/summary'):
                                    os.makedirs('src/summary')
                                with open('src/summary/sum_1.txt', 'w') as f:
                                    f.write(summary)
                        Group smaller column values, relative to the average, into a single category called “Other” to enhance visual clarity
                        Grouping Example:
                        main_data = product_data[product_data['percentage'] >= threshold]
                        other_data = product_data[product_data['percentage'] < threshold]
                        if not other_data.empty:
                            other_sales_sum = other_data['sum'].sum()
                            other_row = pd.DataFrame('sum': [other_sales_sum], 'count': [other_data['count'].sum()], 'percentage': [other_sales_sum / total_sales_sum], index=['Other'])
                            main_data = pd.concat([main_data, other_row], ignore_index=False)

                        Output:

                        Each visualization must:
                        Be saved as a PNG in the 'src/plots' folder (chart_n.png).
                        Include a summary saved in the 'src/summary' folder (sum_n.txt), each at least 1000 characters long, providing valuable business insights.
                        Be clearly labeled with appropriate legends and formatting.
                        Use different colors to enhance chart readability.
                        Optimize graphs for high-quality photo output.
                        Where relevant, use fig.add_trace() to combine charts.
                        Save all generated code in the final output file.
                        Ensure the output code and visualizations are optimized, error-free, and provide meaningful business analysis.
                    """,
        expected_output= "Summary.txt file with generated code for viz and summary. Code should be executed by tool",
        #context = [context],
        output_file = "Summary.txt",
        agent=planner,
        tools = [csv_tool], #, t_custom_code_exec_tool.CLITool.execute_code
        async_execution = False
    )
    
    final_sum_task = Task(
        description="""Read the CSV file located in this file path '{csv_folder}/{file_name}'.
        Make the most detailed description of the data using all possible data analytics tools available to you.
        The information should be clear and saved in text format in a file final_gen.txt.
        It should be a long Generated concise report of data anomalies or outliers that provides maximum detail
        + some statistics.
        Your final answer should include ONLY response to this task!
        Answer should contain math statistics from data! markdown text symbols only **!
        """,
        expected_output="A text report on the date analytics of the received data.",
        output_file = "final_gen.txt",
        agent=final_sum_agent,
        tools = [] #, t_custom_code_exec_tool.CLITool.execute_code
    )
    #_______________________run Crew_________________________________________
    crew1 = Crew(
        agents=[planner],
        tasks=[plan],
        process=Process.sequential,
        manager_llm=OpenAIGpt4
    )
    crew2 = Crew(
        agents=[final_sum_agent],
        tasks=[final_sum_task],
        process=Process.sequential,
        manager_llm=OpenAIGpt4
    )
    import pandas as pd
    df = pd.read_csv(f'src/uploads/{file}')
    columns = df.columns.tolist()
    data_config = {'lib':"plotly",
                   'tasks_for_data_num':'5',
                   'file_name': file,
                   'csv_folder': 'src/uploads',
                   'data_columns':columns}
    #crew.kickoff(inputs=data_config)
    crew1.kickoff(inputs=data_config)
    #crew2.kickoff(inputs=data_config)

    #return results
    #print(results)
    #from t import extract_and_execute_code
    code_executing_solution.extract_and_execute_code("Summary.txt")
    return "Everything is ok"