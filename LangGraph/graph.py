from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from openai import OpenAI
from pydantic import BaseModel

# Schema
class DetectCallResponse(BaseModel):
    is_coding_question: bool

client = OpenAI(
    api_key= "",
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"
)

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    
def detect_query(state: State):
    user_message = state.get("user_message")
    
    # AI Call
    SYSTEM_PROMPT = """
    You are a helpful assistant. Your job is to detect if the user's query is related to coding question or not.
    Return the response in specified JSON boolean only.
    """
    response = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        response_format=DetectCallResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    
    state["is_coding_question"] = response.choices[0].message.parsed.is_coding_question
    return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

def solve_coding_question(state: State):
    user_message = state.get("user_message")
    
    response =  client.chat.completions.create(
        model="gemini-2.5-flash",
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Your job is to resolve the user quesry based on coding problem he is facing."},
            {"role": "user", "content": user_message}
        ]
)
    # AI Call (Coding Question)
    state["ai_message"] = response.choices[0].message.content
    
    return state

def solve_simple_question(state: State):
    user_message = state.get("user_message")
    
    # Non Coding Question
    state["ai_message"] = "Please ask some coding related question"
    
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Use the graph

def call_graph():
    state = {
        # "user_message": "Hey  there! How are you?",
        "user_message": "Write program to add to numbers in Python?",
        "ai_message": "",
        "is_coding_question": False
    }
    result = graph.invoke(state)
    print("Final Result: ", result)
    
call_graph()