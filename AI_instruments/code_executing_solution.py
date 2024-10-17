import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
# Ensure folders exist

plots_FOLDER = 'src/plots'
summary_FOLDER = 'src/summary'
if not os.path.exists(plots_FOLDER):
    os.makedirs(plots_FOLDER)
if not os.path.exists(summary_FOLDER):
    os.makedirs(summary_FOLDER)
    
def extract_and_execute_code(file_path):
    """
    Extracts Python code blocks from a file and executes them.
    :param file_path: Path to the text file containing Python code blocks.
    """
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            content = file.read()

        # Regex pattern to extract code blocks between ```python and ```
        code_blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)

        # For each extracted code block, execute it
        for i, code_block in enumerate(code_blocks, start=1):
            print(f"Executing code block {i}...\n")
            exec(code_block)
            print(f"Code block {i} executed successfully!\n")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
#extract_and_execute_code('Summary.txt')
