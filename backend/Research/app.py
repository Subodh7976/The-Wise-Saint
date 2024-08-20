from fastapi import FastAPI
from .agent import MathsTutor
# from pydantic_models import Query

from pydantic import BaseModel

class Query(BaseModel):
    query: str 
    thread_id: int 
    format_response: bool
    
app = FastAPI()

@app.post("/")
def make_request(request: Query):
    agent = MathsTutor()
    response = agent.run(request.query, request.thread_id, request.format_response)
    
    return {
        "response": response
    }
    
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
