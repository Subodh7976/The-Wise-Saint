from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class Steps(BaseModel):
    steps: List[str]

class StepPlan(BaseModel):
    response: str 
    use_calculator: bool
    review_steps: bool
    
class Query(BaseModel):
    query: str 
    thread_id: int 
    format_response: bool