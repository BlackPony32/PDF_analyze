from crewai_tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from interpreter import interpreter
from dotenv import load_dotenv
load_dotenv()

interpreter.auto_run = True
interpreter.llm.model = "openai/gpt-4o"

class CLITool:
    @tool("Executor")
    def execute_code(command: str):
        """Create or execute code using Open Interpreter"""
        result = interpreter.chat(command)
        return result