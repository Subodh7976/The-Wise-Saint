from .tools import MathsToolSpec
from llama_index.tools.wikipedia import WikipediaToolSpec
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini


llm = Gemini(model_name="models/gemini-pro")
tool_list = WikipediaToolSpec().to_tool_list()
tool_list.extend(MathsToolSpec().to_tool_list())

agent = ReActAgent.from_tools(tool_list, llm=llm, verbose=True, 
                   description="""You are helpful AI Tutor for mathematics. You have to take the query from user,
                               analyze it and with the help of available tools, try to answer the query fully with detailed explaination. 
                               The raw response you will get from the tools, you will have to refine them into easily understandable steps.
                                You have access to tools for plotting the equation or expression, calcuating answer of the equation and calculator for precise calculation, 
                                along with access to Wikipedia for any context related to terminologies""")

