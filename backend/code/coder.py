from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_verbose, set_debug
from llm import get_llm
from prompts import PROGRAMMER_AGENT_PROMPT

class Coder:
    def __init__(self):
        set_debug(True)
        set_verbose(True)
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
        return self.programmer_agent.invoke({"query": query})


