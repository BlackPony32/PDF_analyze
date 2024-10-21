
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
#from AI_instruments.custom_code_exec_tool import CLITool
#from t_custom_code_exec_tool import CLITool
from AI_instruments.code_executing_solution import extract_and_execute_code
from crewai_tools import CodeInterpreterTool
from dotenv import load_dotenv
load_dotenv()
from crewai_tools import CSVSearchTool

def AI_generation_plots_summary1(_data_dict, data_path):
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
        backstory="""You're working with visual studio code with plotly go code.""",
        allow_delegation=False,
        memory=True,
    	verbose=True
    )

    #_______________________tasks block_________________________________________
    plan = Task(
        description="""Task Description:

                        Analyze a CSV file and generate insightful visualizations using Plotly. The provided folders and file paths are already set up, so there's no need to check their existence.

                        Input Data:

                        The dataset is large in size, so I'm going to give you some basic information about it.
                        Analyze it and, based on the data, complete the tasks I will describe below. You get:
                        Dataset head: {head},
                        Some describe: {describe}
                        df info: {info}
                        information about missing values: {missing_values}
                        useful information about columns type and its name : {column_types}
                        shape: {shape}
                        memory_usage = {memory_usage}
                        
                        Tasks:

                        -Analyze the data and create {tasks_for_data_num} specific tasks.
                        -Write visualization code (functions) using Plotly Graph Objects (Plotly GO) for each task.
                        Each task should include:
                        -Informative visualizations functions that show dependencies between columns.
                        -Functional code for each visualization.
                        - use different plot style, colors
                        It should be visualizations for all data not only that ypu get/
                        Ensure all tasks are executed using a try-except block to handle errors gracefully.
                        
                        Requirements for every function you should use!:


                        -Only use columns that exist in the dataframe, and check column existence using conditional statements.
                        Each function should generate:
                        -use local variables like df 
                        -One visualization.
                        -A summary explanation.
                        -do not use different written functions like load dataset
                        -different color style, like Light24. (lib import plotly.express as px)
                        Donut chart prefer than standard pie-chart
                        Example good code for one function:
                        def task_1_visualization():
                            df = pd.read_csv('{data_path}')
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
    
    #_______________________run Crew_________________________________________
    crew1 = Crew(
        agents=[planner],
        tasks=[plan],
        process=Process.sequential,
        manager_llm=OpenAIGpt4
    )
    #final_answer = agent_answer.get("output")
    
    head = _data_dict.get("head")
    describe = _data_dict.get("describe")
    info = _data_dict.get("info")
    missing_values = _data_dict.get("missing_values")
    column_types = _data_dict.get("column_types")
    shape = _data_dict.get("shape")
    memory_usage = _data_dict.get("memory_usage")
    
    
    data_config ={
        'data_path': str(data_path),
        'tasks_for_data_num' : 5,
        'head': str(head),  # First 5 rows of the dataframe as a dictionary
        'describe':str(describe),  # Descriptive statistics of all columns
        'info': str(info),  # DataFrame info as a string
        'missing_values': str(missing_values),  # Count of missing values for each column
        'column_types': str(column_types),  # Data types of each column
        'shape': str(shape),  # Shape of the dataset (rows, columns)
        'memory_usage': str(memory_usage)  # Total memory usage of the dataset
    }
    with open('111final_gen.txt', 'w') as file:
        file.write(str(data_config))
    crew1.kickoff(inputs=data_config)

    extract_and_execute_code("Summary.txt")
    return "Everything is ok"