from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langgraph.graph import StateGraph, END 
from langgraph.checkpoint.sqlite import SqliteSaver 
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from typing import TypedDict, List, Any

from backend.Research.pydantic_models import Steps, StepPlan
from .prompts import *
from backend.Research.constants import *



class AgentState(TypedDict):
    query: str 
    definition: str 
    decomposed_steps: List[str]
    solved_steps: List[str]
    step_history: List[Any]
    completed_step: int
    review_count: int
    
class MathsTutor:
    def __init__(self, gemini_model: str = GEMINI_MODEL):
        self.memory = SqliteSaver.from_conn_string(":memory:")
        self.llm = ChatGoogleGenerativeAI(model=gemini_model)
        self.step_plan_parser = PydanticOutputParser(pydantic_object=StepPlan)
        self.step_parser = PydanticOutputParser(pydantic_object=Steps)
        self.graph = None
        self.__setup_builder()

    def __setup_builder(self):
        builder = StateGraph(AgentState)
        
        builder.add_node("definer", self.problem_definer_node)
        builder.add_node("decomposer", self.problem_decomposer_node)
        builder.add_node("solver", self.step_generator)
        builder.add_node("calculator", self.calculator)
        builder.add_node("steps_updater", self.update_steps)
        builder.add_node("steps_reviewer", self.review_steps)
        builder.add_node("response_refiner", self.refiner)
        builder.add_node("gateway_node", lambda x:x)
        
        builder.set_entry_point("definer")
        
        builder.add_edge("definer", "decomposer")
        builder.add_edge("decomposer", "gateway_node")
        builder.add_edge("steps_updater", "gateway_node")
        builder.add_edge("calculator", "solver")
        builder.add_edge("steps_reviewer", "decomposer")
        builder.add_edge("response_refiner", END)
        
        builder.add_conditional_edges(
            "gateway_node", 
            self.step_iterator, 
            {
                "refine_steps": "response_refiner", 
                "generate_step": "solver"
            }
        )
        builder.add_conditional_edges(
            "solver", 
            self.step_tool_decider, 
            {
                "calculator": "calculator",
                "update_steps": "steps_updater",
                "reset_steps": "steps_reviewer"
            }
        )
        
        self.graph = builder.compile(checkpointer=self.memory)
    
    def run(self, query: str, thread_id: int = 1, format_response: bool = True):
        thread = {
            "configurable": {"thread_id": thread_id}
        }
        
        response = self.graph.invoke({"query": query}, thread)
        
        if format_response:
            return "\n\n".join(response['solved_steps'])
        return response
    
    def problem_definer_node(self, state: AgentState):
        messages = [
            SystemMessage(content=PROBLEM_DEFINER_PROMPT),
            HumanMessage(content=state['query'])
        ]
        response = self.llm.invoke(messages)
        return {
            "definition": response.content,
            "review_count": 0
        }
    
    def problem_decomposer_node(self, state: AgentState):        
        chain = self.llm | self.step_parser
        system_message = f"{PROBLEM_DECOMPOSER_PROMPT}\n\nFormat Instructions: {self.step_parser.get_format_instructions()}"
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=state['definition'])
        ]
        
        steps = chain.invoke(messages)
        return {
            "decomposed_steps": steps.steps, 
            "completed_steps": 0, 
            "step_history": [], 
            "solved_steps": []
        }
        
    def step_generator(self, state: AgentState):
        solved_steps = state['solved_steps'] or []
        step_count = state['completed_step'] or 0
        messages = state['step_history'] or []
        
        chain = self.llm | self.step_plan_parser
        
        if len(messages) == 0:
            system_message = STEP_GENERATOR_PROMPT.format(
                format_instructions=self.step_plan_parser.get_format_instructions()
            )
            content = "\n\n".join(solved_steps)
            human_content = f"Original problem definition: {state['query']}. This is the solution so far: {content}\n\n and this is the description for next step: {state['decomposed_steps'][step_count]}"
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=human_content)
            ]
        
        retry = 0
        while True:
            try:
                response = chain.invoke(messages)
                break
            except OutputParserException as e:
                retry += 1
                if retry > EXCEPTION_RETRIES:
                    raise e
                continue
        messages.append(AIMessage(content=response.json()))
        
        return {
            "step_history": messages
        }
    
    def review_steps(self, state: AgentState):
        last_response = state['step_history'][-1]
        last_response = self.step_plan_parser.parse(last_response.content)
        
        solved_steps = state['solved_steps'] or []
        content = "\n\n".join(solved_steps)
        content += last_response.response
        
        content = "Problem Definition:\n" + state['definition'] + "\n\nSTEPS AND FEEDBACK:\n" + content
        
        messages = [
            SystemMessage(content=STEPS_REVIEW_PROMPT),
            HumanMessage(content=content)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "definition": response.content
        }
    
    def update_steps(self, state: AgentState):
        last_response = state['step_history'][-1]
        last_response = self.step_plan_parser.parse(last_response.content)
        
        step_count = state['completed_step'] or 0
        step_count += 1
        solved_steps = state['solved_steps'] or []
        solved_steps.append(last_response.response)
        
        return {
            "completed_step": step_count, 
            "solved_steps": solved_steps, 
            "step_history": []
        }
    
    def calculator(self, state: AgentState):
        last_response = state['step_history'][-1]
        last_response = self.step_plan_parser.parse(last_response.content)
        
        wolfram = WolframAlphaAPIWrapper()
        response = wolfram.run(last_response.response)
        human_content = f"With calculator response: {response}. Generate the whole solution."
        messages = state['step_history']
        messages.append(HumanMessage(
            content=human_content
        ))
        
        return {
            "step_history": messages
        }
    
    def refiner(self, state: AgentState):
        solved_steps = state['solved_steps'] or []
        content = "\n\n".join(solved_steps)
        
        query = state['query']
        human_content = f"Problem Definition: {query}\n\nSolved Steps: {content}"
        
        messages = [
            SystemMessage(content=REFINER_PROMPT),
            HumanMessage(content=human_content)
        ]
        
        response = self.llm.invoke(messages)
        solved_steps.append(response.content)
        return {
            "solved_steps": solved_steps
        }
    
    def step_iterator(self, state: AgentState):
        print("Steps completed - ", state['completed_step'])
        if (state['completed_step'] or 0) >= len(state['decomposed_steps']):
            return "refine_steps"
        return "generate_step"
    
    def step_tool_decider(self, state: AgentState):
        last_response = state['step_history'][-1]
        last_response = self.step_plan_parser.parse(last_response.content)
        
        if last_response.use_calculator:
            return "calculator"
        if last_response.review_steps:
            review_count = state['review_count'] or 0
            if review_count < MAX_REVIEW_COUNT:
                review_count += 1
                return "reset_steps"
        return "update_steps"
    
    