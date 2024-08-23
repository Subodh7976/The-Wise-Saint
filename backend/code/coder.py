from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_verbose, set_debug
from llm import get_llm
from prompts import PROGRAMMER_AGENT_PROMPT

set_debug(True)
set_verbose(True)


'''
Code Solving Agent. Useful for solving Coding questions.
'''
class Coder:
    def __init__(self):
        self.llm = get_llm()
        self.programmer_agent_prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    PROGRAMMER_AGENT_PROMPT,
                ),
                (
                    "user",
                    "{query}"
                ),
            ]
        )

        self.programmer_agent = self.programmer_agent_prompt | self.llm | StrOutputParser()

    def invoke(self, query: str):
        """
        Invoking the Code Agent with the specific query.
        
        Args:
            query: str - The coding question that needs to be sent to the agent
        
        Return:
            str - The LLM generated response (containts analysis, algorithm, psuedo-code, code)

        """
        return self.programmer_agent.invoke({"query": query})